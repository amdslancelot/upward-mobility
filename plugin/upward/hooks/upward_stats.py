#!/usr/bin/env python3
# upward-stats — Stop and SubagentStop hook. Runs after every turn (and after
# every finished subagent); no-op unless .upward/stats-state.json (under the
# project root) has {"enabled": true}.
# When enabled, resumes parsing the session transcript from where it left off
# (byte offset cached in .upward/stats-cache.json) and appends only the rows
# for newly-completed tasks to .upward/UPWARD-STATS.md — it never rereads the
# whole transcript or rewrites the whole file. Everything lives in the .upward/
# dot-directory so repo scans and glob patterns skip it by default. Subagent rows are held back until
# their jsonl file's size is unchanged across two consecutive hook events
# (i.e. the subagent has finished writing); this avoids emitting a row for a
# still-running background agent and then never being able to fix the count.
# SubagentStop events exist so those two sightings happen even in a headless
# one-turn session, which fires Stop exactly once — without them a dispatch's
# row would register but never emit. On SubagentStop the main-task rows are
# NOT flushed: the main turn is still in flight at that moment, and a task row
# is emitted only once per prompt, so flushing early would freeze a partial
# count that no later event could correct.
# Never raises past main() — a stats bug must not break the user's session.
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


def upward_dir(cwd):
    return os.path.join(cwd, ".upward")


def migrate_root_files(cwd):
    """Plugin versions before 0.2.0 wrote the three stats files directly at
    the project root. Move the state file (user-set preference) into .upward/
    and delete the two generated files — the hook regenerates them there."""
    old_state = os.path.join(cwd, ".upward-stats-state.json")
    new_state = os.path.join(upward_dir(cwd), "stats-state.json")
    try:
        if os.path.isfile(old_state):
            if os.path.exists(new_state):
                os.remove(old_state)
            else:
                os.makedirs(upward_dir(cwd), exist_ok=True)
                os.replace(old_state, new_state)
    except Exception:
        pass
    for name in (".upward-stats-cache.json", "UPWARD-STATS.md"):
        try:
            os.remove(os.path.join(cwd, name))
        except Exception:
            pass


def load_state(cwd):
    # Default on: no state file (or unparsable) means tracking is enabled.
    default = {"enabled": True, "level": "task"}
    path = os.path.join(upward_dir(cwd), "stats-state.json")
    try:
        with open(path) as f:
            state = json.load(f)
    except Exception:
        return default
    return state if isinstance(state, dict) else default


def cache_path(cwd):
    return os.path.join(upward_dir(cwd), "stats-cache.json")


def stats_path(cwd):
    return os.path.join(upward_dir(cwd), "UPWARD-STATS.md")


def empty_cache(transcript_path, level):
    return {
        "transcript_path": transcript_path,
        "level": level,
        "offset": 0,
        "current_pid": None,
        "tasks": {},
        "order": [],
        "seen_msg_ids": [],
        "emitted_pids": [],
        "subagents": {},
    }


def load_cache(cwd, transcript_path, level):
    """Returns (cache, reset). reset is True when the cache didn't match this
    transcript/level (new session, or user flipped /upward-stats level) — the
    caller must then start UPWARD-STATS.md over instead of appending to it."""
    try:
        with open(cache_path(cwd)) as f:
            c = json.load(f)
    except Exception:
        c = None
    if not isinstance(c, dict) or c.get("transcript_path") != transcript_path or c.get("level") != level:
        return empty_cache(transcript_path, level), True
    return c, False


def save_cache(cwd, cache):
    # Temp-file + rename so a concurrent reader can never see a half-written
    # cache (a torn read parses as invalid, forces reset=True, and the
    # same-session reset branch would delete UPWARD-STATS.md mid-session).
    path = cache_path(cwd)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(cache, f)
        os.replace(tmp, path)
    except Exception:
        pass


def call_usage(msg):
    usage = msg.get("usage") or {}
    return {
        "model": msg.get("model", "unknown"),
        "output": usage.get("output_tokens", 0),
        "cache_write": usage.get("cache_creation_input_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "fresh_input": usage.get("input_tokens", 0),
        "desc": None,
    }


def describe_block(block):
    """One-line human description of an assistant content block: the command a
    Bash call ran, the file an edit touched, etc. Returns (priority, text);
    higher priority wins so a tool_use beats a preceding text/thinking block."""
    t = block.get("type")
    if t == "tool_use":
        name = block.get("name", "tool")
        inp = block.get("input") or {}
        if name == "Bash":
            key = inp.get("description") or inp.get("command")
        elif name in ("Read", "Edit", "Write", "NotebookEdit"):
            key = inp.get("file_path")
            if key:
                key = key.split("/")[-1]
        elif name in ("Agent", "Task"):
            key = inp.get("description")
        elif name in ("Grep", "Glob"):
            key = inp.get("pattern")
        elif name == "Skill":
            key = inp.get("skill")
        elif name == "ToolSearch":
            key = inp.get("query")
        else:
            key = (inp.get("description") or inp.get("command")
                   or inp.get("file_path") or inp.get("pattern") or inp.get("query"))
        text = f"{name}: {key}" if key else name
        return 2, " ".join(str(text).split())[:60]
    if t == "text":
        text = " ".join((block.get("text") or "").split())
        if text:
            return 1, text[:60]
    return 0, None


def update_desc(call, content):
    if not isinstance(content, list):
        return
    for block in content:
        prio, text = describe_block(block)
        if text and prio > call.get("_desc_prio", 0):
            call["desc"] = text
            call["_desc_prio"] = prio


def collect_skills(content, into):
    """Append the name of every Skill tool_use block in `content` to `into`.
    Tracked separately from the per-call description because several tool_use
    blocks can share one API call, and the description keeps only the first —
    a Skill load batched with another tool call would otherwise go unrecorded."""
    if not isinstance(content, list):
        return
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
            name = (block.get("input") or {}).get("skill")
            if name:
                into.append(str(name))


def skill_injected_estimate(name):
    """Approximate token cost of a skill's SKILL.md landing in context, for
    skills that ship with this plugin (resolved relative to this hook file).
    Returns a short label fragment; the ~len/4 heuristic is an estimate and is
    marked as such. Unknown skills return 'size unknown'."""
    here = os.path.dirname(os.path.abspath(__file__))
    if name == "core.md":
        path = os.path.join(here, "..", "core.md")
    else:
        short = name.split(":")[-1]
        path = os.path.join(here, "..", "skills", short, "SKILL.md")
    try:
        with open(path) as f:
            n = len(f.read()) // 4
        return f"~{n:,} tok injected"
    except Exception:
        return "size unknown"


def parse_transcript_incremental(path, cache):
    """Resume parsing the main transcript from cache["offset"], merging newly
    seen lines into cache["tasks"]/["order"] in place. Each 'assistant' JSONL
    line is one content block, not one API call — several lines can share the
    same message.id, so usage is only counted once per unique message id."""
    seen_msg_ids = set(cache["seen_msg_ids"])
    tasks = cache["tasks"]
    order = cache["order"]
    current_pid = cache["current_pid"]
    try:
        fh = open(path, "rb")
    except Exception:
        return
    with fh:
        # Binary mode with an explicit readline loop: a SubagentStop event can
        # fire while the main turn is still appending to this file, so the
        # last line may be a torn partial write. Only newline-terminated lines
        # are consumed; an unterminated tail is left for the next event to
        # re-read whole — advancing the offset past a fragment would silently
        # lose the rest of that record (or a promptId) forever.
        fh.seek(cache["offset"])
        while True:
            raw = fh.readline()
            if not raw:
                break
            if not raw.endswith(b"\n"):
                fh.seek(-len(raw), os.SEEK_CUR)
                break
            line = raw.decode("utf-8", "replace").strip()
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
                    cmd_m = re.search(r"<command-name>([^<]*)</command-name>", content)
                    if cmd_m:
                        label = cmd_m.group(1).strip()
                        args_m = re.search(r"<command-args>([^<]*)</command-args>", content)
                        if args_m and args_m.group(1).strip():
                            label += " " + args_m.group(1).strip()
                        label = label[:70]
                    else:
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
                calls = tasks[current_pid]["calls"]
                collect_skills(msg.get("content"), tasks[current_pid].setdefault("skills", []))
                if msg_id and msg_id in seen_msg_ids:
                    if calls:
                        update_desc(calls[-1], msg.get("content"))
                    continue
                if msg_id:
                    seen_msg_ids.add(msg_id)
                call = call_usage(msg)
                update_desc(call, msg.get("content"))
                calls.append(call)
        cache["offset"] = fh.tell()
    cache["current_pid"] = current_pid
    cache["seen_msg_ids"] = list(seen_msg_ids)


def collect_new_main_tasks(cache):
    """A Stop event only fires once its whole turn (all promptIds seen so far
    in this run) has finished, so every not-yet-emitted pid is safe to emit."""
    new_tasks = []
    for pid in cache["order"]:
        if pid in cache["emitted_pids"]:
            continue
        task = cache["tasks"].get(pid)
        if not task or not task["calls"]:
            continue
        new_tasks.append({"label": task["label"] or "(tool continuation)",
                           "calls": task["calls"], "ts": task["ts"],
                           "skills": task.get("skills", [])})
        cache["emitted_pids"].append(pid)
    return new_tasks


def aggregate_all_calls(path):
    """Full one-shot parse of a subagent transcript into a flat call list —
    only called once per subagent file, when process_subagents has decided
    it's finished (see below)."""
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
            if msg_id and msg_id in seen:
                if calls:
                    update_desc(calls[-1], msg.get("content"))
                continue
            if msg_id:
                seen.add(msg_id)
            call = call_usage(msg)
            update_desc(call, msg.get("content"))
            calls.append(call)
    return calls, ts


def process_subagents(session_dir, cache):
    """A subagent's row is only emitted once its jsonl file's size is
    unchanged from the previous Stop event — proof it's done writing.
    A background agent that's still growing gets skipped this turn and
    picked up whole+accurate on a later one, rather than emitted early
    with a count that can never be corrected."""
    subdir = os.path.join(session_dir, "subagents")
    if not os.path.isdir(subdir):
        return []
    new_tasks = []
    cache_sub = cache["subagents"]
    for jsonl_path in sorted(glob.glob(os.path.join(subdir, "*.jsonl"))):
        try:
            size = os.path.getsize(jsonl_path)
        except OSError:
            continue
        entry = cache_sub.get(jsonl_path)
        if entry and entry.get("emitted"):
            continue
        if entry is None:
            cache_sub[jsonl_path] = {"size": size, "emitted": False}
            continue
        if entry["size"] != size:
            entry["size"] = size
            continue
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
        entry["emitted"] = True
        if not calls:
            continue
        label = f"[agent] {desc or agent_type or os.path.basename(jsonl_path)}"
        new_tasks.append({"label": label, "calls": calls, "ts": ts})
    return new_tasks


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


def header_cells(level):
    header = ["task", "subtask", "calls", "output", "cache write", "cache read", "fresh input"]
    if level == "call":
        header.append("model")
    return header


def render_rows(tasks, level):
    lines = []

    def row(task_label, subtask, s, model=None):
        cells = [task_label, subtask, fmt(s["calls"]), fmt(s["output"]),
                 fmt(s["cache_write"]), fmt(s["cache_read"]), fmt(s["fresh_input"])]
        if level == "call":
            cells.append(model or "")
        lines.append("| " + " | ".join(esc(c) for c in cells) + " |")

    zero = {"calls": 0, "output": 0, "cache_write": 0, "cache_read": 0, "fresh_input": 0}
    for task in tasks:
        total = summarize(task["calls"])
        row(task["label"], "-", total, models_label(task["calls"]) if level == "call" else None)
        if level == "call":
            for i, c in enumerate(task["calls"], 1):
                subtask = c.get("desc") or f"call {i}"
                row(task["label"], f"{i}. {subtask}", summarize([c]), c["model"])
        # One informational row per Skill load, at both levels. Token columns
        # stay zero on purpose: the injected content is already inside the
        # following call's cache write, so putting an amount here would double
        # count — the size estimate travels in the label instead.
        for name in task.get("skills", []):
            row(task["label"], f"[skill] {name} ({skill_injected_estimate(name)})",
                zero, "-" if level == "call" else None)
    return lines


def write_new_file(path, session_id, level, rows):
    header = header_cells(level)
    lines = [
        "# Upward Stats",
        "",
        f"Session: `{session_id}` · Level: `{level}` · "
        f"Started: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
    ]
    lines.extend(rows)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def append_rows(path, rows):
    if not rows:
        return
    with open(path, "a") as f:
        f.write("\n".join(rows) + "\n")


def acquire_lock(cwd):
    """Exclusive advisory lock for the whole run of main(). Stop events never
    overlap, but two SubagentStop events can fire near-simultaneously when
    agents finish together — unserialized, both could read the parse cache
    before either saves it and emit the same [agent] row twice. Returns the
    open lock file handle (held until process exit) or None where flock isn't
    available (Windows); the single-writer assumption then holds as before."""
    try:
        import fcntl
        fh = open(os.path.join(upward_dir(cwd), ".lock"), "w")
        fcntl.flock(fh, fcntl.LOCK_EX)
        return fh
    except Exception:
        return None


def main():
    hook_input = read_hook_input()
    cwd = hook_input.get("cwd") or os.getcwd()

    migrate_root_files(cwd)
    state = load_state(cwd)
    if not state or not state.get("enabled"):
        return
    level = state.get("level") if state.get("level") in ("task", "call") else "task"
    try:
        os.makedirs(upward_dir(cwd), exist_ok=True)
    except Exception:
        return
    lock = acquire_lock(cwd)  # held (referenced) until main() returns

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        transcript_path = find_recent_transcript(cwd)
    if not transcript_path or not os.path.isfile(transcript_path):
        return

    cache, reset = load_cache(cwd, transcript_path, level)
    parse_transcript_incremental(transcript_path, cache)

    # On SubagentStop the main turn is still running: parse (cheap, keeps the
    # offset current) but only flush main-task rows on Stop — a task row is
    # emitted once per prompt, so an early flush would freeze a partial count.
    on_subagent_stop = hook_input.get("hook_event_name") == "SubagentStop"
    new_tasks = [] if on_subagent_stop else collect_new_main_tasks(cache)
    session_dir = os.path.splitext(transcript_path)[0]
    new_tasks += process_subagents(session_dir, cache)
    new_tasks.sort(key=lambda task: task.get("ts") or "")

    out_path = stats_path(cwd)
    session_id = os.path.basename(session_dir)
    if reset and os.path.exists(out_path):
        # Starting over. If the existing file belongs to a DIFFERENT session,
        # it is someone else's data (e.g. this session's shell wandered into a
        # directory holding a finished benchmark run's stats) — archive it
        # aside instead of destroying it. Only a same-session reset (the user
        # flipped /upward-stats level) discards the file.
        try:
            with open(out_path) as f:
                head = f.read(2000)
            m = re.search(r"Session: `([^`]+)`", head)
            old_session = m.group(1) if m else None
            if old_session and old_session != session_id:
                os.replace(out_path, os.path.join(
                    upward_dir(cwd), f"UPWARD-STATS-{old_session[:8]}.md"))
            else:
                os.remove(out_path)
        except Exception:
            pass

    if new_tasks:
        rows = render_rows(new_tasks, level)
        if not os.path.exists(out_path):
            # First write of a session also records the always-on injection:
            # core.md enters context at every SessionStart, before any task.
            zero = ["0"] * 5 + (["-"] if level == "call" else [])
            core_row = ("| (session start) | [skill] core.md "
                        f"({skill_injected_estimate('core.md')}) | " + " | ".join(zero) + " |")
            write_new_file(out_path, session_id, level, [core_row] + rows)
        else:
            append_rows(out_path, rows)

    save_cache(cwd, cache)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
