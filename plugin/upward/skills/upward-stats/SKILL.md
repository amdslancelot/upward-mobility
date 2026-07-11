---
name: upward-stats
description: Turn per-prompt/per-call token usage tracking on or off, written to UPWARD-STATS.md. Use when the user runs "/upward-stats on", "/upward-stats off", "/upward-stats level task", or "/upward-stats level call".
---
# upward-stats: toggle token-usage tracking

This skill only flips a switch. The actual recording (reading the session transcript, summing token usage per call, grouping into tasks, writing the table) happens automatically in a `Stop` hook shipped with this plugin (`hooks/upward_stats.py`) — it runs after every turn and checks the switch. Don't try to compute or write the stats table by hand; that duplicates what the hook already does correctly.

## State file

`.upward-stats-state.json` at the project root (current working directory). Shape:

```json
{"enabled": false, "level": "task"}
```

## On each invocation

1. Read `.upward-stats-state.json` in the cwd if it exists. If missing or unparsable, treat as `{"enabled": false, "level": "task"}`.
2. Apply the argument:
   - `on` → `enabled: true`
   - `off` → `enabled: false`
   - `level task` → `level: "task"` (one row per prompt)
   - `level call` → `level: "call"` (one row per prompt, plus one row per individual API call underneath, with a model column)
   - anything else / no argument → don't change the file, just report the current state
3. Write the full JSON object back to `.upward-stats-state.json` (preserve the field you didn't just change).
4. Report the resulting state in one line, e.g. "upward-stats: on, level=task — writes to UPWARD-STATS.md after each turn."

Turning tracking on for the first time won't produce `UPWARD-STATS.md` until the *next* turn finishes (the hook writes it at Stop, not at skill-invocation time).
