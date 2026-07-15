---
name: upward-stats
description: Turn per-prompt/per-call token tracking on or off, written to .upward/UPWARD-STATS.md. Use for /upward-stats on, off, or level.
---
# upward-stats: toggle token-usage tracking

This skill only flips a switch. The actual recording (reading the session transcript, summing token usage per call, grouping into tasks, writing the table) happens automatically in a hook shipped with this plugin (`hooks/upward_stats.py`) — it runs on `Stop` after every turn and on `SubagentStop` after every finished subagent (so dispatched agents' usage lands as `[agent]` rows even in a one-turn headless session), checking the switch each time. Don't try to compute or write the stats table by hand; that duplicates what the hook already does correctly.

## State file

`.upward/stats-state.json` under the project root (current working directory). All stats artifacts — the state file, the hook's parse cache, and the generated `UPWARD-STATS.md` — live inside the `.upward/` dot-directory so repo scans and glob patterns skip them by default. Shape:

```json
{"enabled": true, "level": "task"}
```

Tracking is **on by default**: if this file is missing or unparsable, the hook treats it as `{"enabled": true, "level": "task"}`. Run `/upward-stats off` to opt out.

## On each invocation

1. Read `.upward/stats-state.json` in the cwd if it exists. If missing or unparsable, treat as `{"enabled": true, "level": "task"}` (tracking is on by default).
2. Apply the argument:
   - `on` → `enabled: true`
   - `off` → `enabled: false`
   - `level task` → `level: "task"` (one row per prompt)
   - `level call` → `level: "call"` (one row per prompt, plus one row per individual API call underneath, with a model column)
   - anything else / no argument → don't change the file, just report the current state
3. Write the full JSON object back to `.upward/stats-state.json`, creating the `.upward/` directory first if it doesn't exist (preserve the field you didn't just change).
4. Report the resulting state in one line, e.g. "upward-stats: on, level=task — writes to .upward/UPWARD-STATS.md after each turn."

Turning tracking on for the first time won't produce `.upward/UPWARD-STATS.md` until the *next* turn or subagent finishes (the hook writes it at Stop or SubagentStop, not at skill-invocation time).
