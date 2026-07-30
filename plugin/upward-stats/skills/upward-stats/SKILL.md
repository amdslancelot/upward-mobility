---
name: upward-stats
description: Toggle per-prompt/per-call token usage and cost tracking written to .upward/UPWARD-STATS.md, and clean up the archived tables of earlier sessions. Use when the user runs "/upward-stats", "/upward-stats on", "/upward-stats off", "/upward-stats level call", "/upward-stats level task", or "/upward-stats clean" — or asks to prune old UPWARD-STATS files.
---
# upward-stats: toggle token-usage tracking, and prune its archives

This skill flips a switch and cleans up files. The actual recording (reading the session transcript, summing token usage per call, costing it against `hooks/pricing.json`, grouping into tasks, writing the table) happens automatically in a `Stop` hook shipped with this plugin (`hooks/upward_stats.py`) — it runs after every turn and checks the switch. Don't try to compute or write the stats table by hand; that duplicates what the hook already does correctly.

If the user wants a price corrected or a missing model priced, write `.upward/pricing.json` — `{"models": {"<model-id>": {"input": <USD per MTok>, "output": <USD per MTok>}}}` — which overrides the shipped table per model id. Don't edit the plugin's own `pricing.json`; a plugin update overwrites it.

## State file

`.upward/stats-state.json` under the project root (current working directory). All stats artifacts — the state file, the hook's parse cache, and the generated `UPWARD-STATS.md` — live inside the `.upward/` dot-directory so repo scans and glob patterns skip them by default. Shape:

```json
{"enabled": true, "level": "call"}
```

Tracking is **on by default**: if this file is missing or unparsable, the hook treats it as `{"enabled": true, "level": "call"}`. Run `/upward-stats off` to opt out.

## On each invocation

If the argument starts with `clean`, go to the cleanup section below and don't touch the state file. Otherwise:

1. Read `.upward/stats-state.json` in the cwd if it exists. If missing or unparsable, treat as `{"enabled": true, "level": "call"}` (tracking is on by default).
2. Apply the argument:
   - `on` → `enabled: true`
   - `off` → `enabled: false`
   - `level call` → `level: "call"` (one row per prompt, plus one row per individual API call underneath — the default)
   - `level task` → `level: "task"` (one row per prompt only)
   - anything else / no argument → don't change the file, just report the current state
3. Write the full JSON object back to `.upward/stats-state.json`, creating the `.upward/` directory first if it doesn't exist (preserve the field you didn't just change).
4. Report the resulting state in one line, e.g. "upward-stats: on, level=call — writes to .upward/UPWARD-STATS.md after each turn."

Turning tracking on for the first time won't produce `.upward/UPWARD-STATS.md` until the *next* turn finishes (the hook writes it at Stop, not at skill-invocation time).

## `/upward-stats clean` — delete archived tables

When a session starts in a directory that already holds another session's `.upward/UPWARD-STATS.md`, the hook renames that file to `UPWARD-STATS-<first 8 chars of its session id>.md` rather than destroying it. Those archives accumulate; this is how they get removed.

Two things are **never** deleted, whatever the user asks for:

- `.upward/UPWARD-STATS.md` — the live table for the current session, still being appended to.
- `.upward/stats-state.json` and `.upward/stats-cache.json` — the toggle and the hook's parse offset. Deleting the cache mid-session makes the hook restart the current table from scratch.

So the target set is exactly `.upward/UPWARD-STATS-*.md` — the suffixed ones — under the project root.

1. List the candidates with size and modification time, newest first:

   ```bash
   ls -lht .upward/UPWARD-STATS-*.md   # archives only; the live UPWARD-STATS.md has no -<id> suffix
   ```

   If the glob matches nothing, say there's nothing to clean and stop — don't go hunting in other directories.

2. Work out which of them to delete from the rest of the argument:
   - `clean` alone → **all** of them
   - `clean keep <n>` → all but the `<n>` most recently modified
   - `clean <session id or prefix>` (e.g. `clean 02c6018f`) → just that one

3. Show the user the exact list you're about to delete (filename, size, date) and ask for confirmation. This is an irreversible delete of measurement data that may be the only remaining record of a run — never skip the confirmation, even if the user's phrasing sounds decisive.

4. On confirmation, delete exactly those paths by name — one `rm` with the listed filenames spelled out, not a re-expanded glob, so the set that gets deleted is the set that was shown. Then report the count and the freed space in one line.

If the user wants an archive kept but out of the way, moving it (e.g. into a `runs/` directory of their choosing) is a fine alternative to offer — but only if they ask; don't move files on your own initiative.
