# upward-stats

A Claude Code plugin that logs per-prompt (and optionally per-API-call) token usage for a session to `.upward/UPWARD-STATS.md`.

It was originally part of the [`upward`](../upward) operating-discipline plugin and is now packaged on its own — it works with or without `upward` installed.

## What it does

A `Stop` / `SubagentStop` hook (`hooks/upward_stats.py`) runs after every turn and after every finished subagent. When tracking is enabled it resumes parsing the session transcript from where it left off, sums token usage per API call, groups the calls into tasks (one per prompt), and appends the new rows to `.upward/UPWARD-STATS.md` — it never rereads the whole transcript or rewrites the whole file. Columns: calls, output, cache write, cache read, fresh input (plus a `model` column at call level). Skill loads are recorded as informational rows with an estimated injected-token size.

Tracking is **on by default**. The `/upward-stats` skill flips the switch:

- `/upward-stats on` / `/upward-stats off` — enable or disable tracking
- `/upward-stats level task` — one row per prompt (default)
- `/upward-stats level call` — one row per prompt plus one row per individual API call, with a model column
- `/upward-stats` (no argument) — report the current state

State lives in `.upward/stats-state.json` under the project root: `{"enabled": true, "level": "task"}`. The skill only writes this file; the actual recording happens in the hook.

Everything lives inside the `.upward/` dot-directory so repo scans and glob patterns skip it by default. The directory is generated/local — add `.upward/` to your project's `.gitignore` if you don't want it tracked. (Plugin versions before the split wrote the files at the project root; the hook migrates them into `.upward/` automatically.)

When the sibling `upward` plugin is co-installed, the first row of each session's table also accounts for `upward`'s always-on `core.md` injection; without `upward` that row is omitted.

## Install

### From this repo (local marketplace)

```
/plugin marketplace add /path/to/upward-mobility/plugin
/plugin install upward-stats@upward-mobility
```

### From GitHub

```
/plugin marketplace add amdslancelot/upward-mobility --path plugin
/plugin install upward-stats@upward-mobility
```

After installing, run `/reload-plugins` (or restart Claude Code) to pick it up. Verify with `/plugin` — `upward-stats` should show as installed and enabled.

## Structure

```
plugin/upward-stats/
├── .claude-plugin/plugin.json   # plugin manifest
├── hooks/
│   ├── hooks.json                # registers the Stop and SubagentStop hooks
│   └── upward_stats.py           # writes .upward/UPWARD-STATS.md when tracking is on
└── skills/
    └── upward-stats/             # /upward-stats on|off|level task|level call toggle
```
