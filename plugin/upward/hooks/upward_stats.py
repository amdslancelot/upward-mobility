#!/usr/bin/env python3
# upward-stats — Stop hook. Runs after every turn; no-op unless
# .upward-stats-state.json (project root) has {"enabled": true}.
# When enabled, re-parses the session transcript and rewrites UPWARD-STATS.md
# with per-prompt (task) or per-API-call token usage, grouped by the prompt
# that triggered each call. Never raises past main() — a stats bug must not
# break the user's session.
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone


def read_hook_input():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def find_recent_transcript(cwd):
    slug = re.sub(r"[^A-Za-z0-9]", "-", cwd)
    project_dir = os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)
    candidates = glob.glob(os.path.join(project_dir, "*.jsonl"))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def load_state(cwd):
    path = os.path.join(cwd, ".upward-stats-state.json")
    try:
        with open(path) as f:
            state = json.load(f)
    except Exception:
        return None
    return state if isinstance(state, dict) else None


def call_usage(msg):
    usage = msg.get("usage") or {}
    return {
        "model": msg.get("model", "unknown"),
        "output": usage.get("output_tokens", 0),
        "cache_write": usage.get("cache_creation_input_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "fresh_input": usage.get("input_tokens", 0),
    }


def parse_transcript(path):
    """Group the main transcript into tasks keyed by promptId. Each 'assistant'
    JSONL line is one content block, not one API call — several lines can share
    the same message.id (same call, split into thinking/text/tool_use blocks),
    so usage is only counted once per unique message id."""
    tasks = {}
    order = []
    current_pid = None
    seen_msg_ids = set()
    try:
        fh = open(path)
    except Exception:
        return []
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("isSidechain"):
                continue
            t = d.get("type")
            if t == "user":
                pid = d.get("promptId")
                if not pid:
                    continue
                content = d.get("message", {}).get("content")
                label = None
                if isinstance(content, str):
                    label = " ".join(content.strip().split())[:70]
                if pid not in tasks:
                    tasks[pid] = {"label": label, "calls": [], "ts": d.get("timestamp")}
                    order.append(pid)
                elif label and not tasks[pid]["label"]:
                    tasks[pid]["label"] = label
                current_pid = pid
            elif t == "assistant":
                if current_pid is None:
                    continue
                msg = d.get("message", {})
                msg_id = msg.get("id")
                if msg_id:
                    if msg_id in seen_msg_ids:
                        continue
                    seen_msg_ids.add(msg_id)
                tasks[current_pid]["calls"].append(call_usage(msg))
    result = []
    for pid in order:
        task = tasks[pid]
        if not task["calls"]:
            continue
        result.append({
            "label": task["label"] or "(tool continuation)",
            "calls": task["calls"],
            "ts": task["ts"],
        })
    return result


def aggregate_all_calls(path):
    """Flatten every assistant call in a subagent transcript into one list —
    subagent runs are reported as a single task row, not split by internal
    prompt turns."""
    calls = []
    seen = set()
    ts = None
    try:
        fh = open(path)
    except Exception:
        return calls, ts
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if ts is None:
                ts = d.get("timestamp")
            if d.get("type") != "assistant":
                continue
            msg = d.get("message", {})
            msg_id = msg.get("id")
            if msg_id:
                if msg_id in seen:
                    continue
                seen.add(msg_id)
            calls.append(call_usage(msg))
    return calls, ts


def collect_subagent_tasks(session_dir):
    subdir = os.path.join(session_dir, "subagents")
    if not os.path.isdir(subdir):
        return []
    tasks = []
    for jsonl_path in sorted(glob.glob(os.path.join(subdir, "*.jsonl"))):
        meta_path = os.path.splitext(jsonl_path)[0] + ".meta.json"
        desc = agent_type = None
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            desc = meta.get("description")
            agent_type = meta.get("agentType")
        except Exception:
            pass
        calls, ts = aggregate_all_calls(jsonl_path)
        if not calls:
            continue
        label = f"[agent] {desc or agent_type or os.path.basename(jsonl_path)}"
        tasks.append({"label": label, "calls": calls, "ts": ts})
    return tasks


def summarize(calls):
    return {
        "calls": len(calls),
        "output": sum(c["output"] for c in calls),
        "cache_write": sum(c["cache_write"] for c in calls),
        "cache_read": sum(c["cache_read"] for c in calls),
        "fresh_input": sum(c["fresh_input"] for c in calls),
    }


def models_label(calls):
    models = sorted(set(c["model"] for c in calls))
    return models[0] if len(models) == 1 else "mixed"


def esc(cell):
    return str(cell).replace("|", "\\|").replace("\n", " ")


def fmt(n):
    return f"{n:,}"


def render_table(tasks, level):
    header = ["task", "subtask", "calls", "output", "cache write", "cache read", "fresh input"]
    if level == "call":
        header.append("model")
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]

    def row(task_label, subtask, s, model=None):
        cells = [task_label, subtask, fmt(s["calls"]), fmt(s["output"]),
                 fmt(s["cache_write"]), fmt(s["cache_read"]), fmt(s["fresh_input"])]
        if level == "call":
            cells.append(model or "")
        lines.append("| " + " | ".join(esc(c) for c in cells) + " |")

    for task in tasks:
        total = summarize(task["calls"])
        row(task["label"], "-", total, models_label(task["calls"]) if level == "call" else None)
        if level == "call":
            for i, c in enumerate(task["calls"], 1):
                row(task["label"], f"call {i}", summarize([c]), c["model"])
    return "\n".join(lines)


def main():
    hook_input = read_hook_input()
    cwd = hook_input.get("cwd") or os.getcwd()

    state = load_state(cwd)
    if not state or not state.get("enabled"):
        return
    level = state.get("level") if state.get("level") in ("task", "call") else "task"

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        transcript_path = find_recent_transcript(cwd)
    if not transcript_path or not os.path.isfile(transcript_path):
        return

    main_tasks = parse_transcript(transcript_path)
    session_dir = os.path.splitext(transcript_path)[0]
    subagent_tasks = collect_subagent_tasks(session_dir)

    all_tasks = main_tasks + subagent_tasks
    all_tasks.sort(key=lambda task: task.get("ts") or "")
    if not all_tasks:
        return

    session_id = os.path.basename(session_dir)
    table = render_table(all_tasks, level)
    content = (
        "# Upward Stats\n\n"
        f"Session: `{session_id}` · Level: `{level}` · "
        f"Updated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n"
        f"{table}\n"
    )

    out_path = os.path.join(cwd, "UPWARD-STATS.md")
    try:
        with open(out_path, "w") as f:
            f.write(content)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
