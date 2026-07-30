# upward-stats

A Claude Code plugin that logs per-API-call (or, collapsed, per-prompt) token usage and estimated cost for a session to `.upward/UPWARD-STATS.md`.

It was originally part of the [`upward`](../upward) operating-discipline plugin and is now packaged on its own — it works with or without `upward` installed.

## What it does

A `Stop` / `SubagentStop` hook (`hooks/upward_stats.py`) runs after every turn and after every finished subagent. When tracking is enabled it resumes parsing the session transcript from where it left off, sums token usage per API call, groups the calls into tasks (one per prompt), and appends the new rows to `.upward/UPWARD-STATS.md` — it never rereads the whole transcript or rewrites the whole file. Columns: calls, output, cache write, cache read, fresh input, cost, model. Skill loads are recorded as informational rows with an estimated injected-token size.

Output at `level: call` — one prompt, the three API calls it took, and the skill it pulled in:

| task | subtask | calls | output | cache write | cache read | fresh input | cost | model |
|---|---|---|---|---|---|---|---|---|
| (session start) | [skill] core.md (~1,408 tok injected) | 0 | 0 | 0 | 0 | 0 | - | - |
| price each row of the stats table | - | 3 | 1,763 | 5,494 | 153,853 | 7 | $0.1760 | claude-opus-5 |
| price each row of the stats table | 1. Read: upward_stats.py | 1 | 171 | 572 | 27,058 | 2 | $0.0235 | claude-opus-5 |
| price each row of the stats table | 2. Edit: upward_stats.py | 1 | 1,204 | 3,180 | 61,880 | 3 | $0.0929 | claude-opus-5 |
| price each row of the stats table | 3. Bash: run the hook against a fixture transcript | 1 | 388 | 1,742 | 64,915 | 2 | $0.0596 | claude-opus-5 |
| price each row of the stats table | [skill] upward-ops-review (~7,412 tok injected) | 0 | 0 | 0 | 0 | 0 | - | - |

Each prompt opens with its total row (`subtask` = `-`), followed by one row per API call. Two things the format is built to make visible: 153,853 cache-read tokens against 7 fresh input ones — a conversation's bill is mostly it re-reading itself, which is why the token types are broken out rather than summed — and a middle call costing 4× the first, because output tokens are 50× the price of a cache read and that call wrote a large edit.

## Commands

Tracking is **on by default** — installing the plugin is all it takes. The `/upward-stats` skill is the whole command surface:

| Command | What it does |
|---|---|
| `/upward-stats` | Report the current state, change nothing |
| `/upward-stats on` · `/upward-stats off` | Start / stop recording |
| `/upward-stats level call` | One row per API call, under a per-prompt total row (**default**) |
| `/upward-stats level task` | Collapse to one row per prompt |
| `/upward-stats clean` | Delete every archived `UPWARD-STATS-<id>.md` in this project |
| `/upward-stats clean keep 3` | …but keep the 3 most recent archives |
| `/upward-stats clean 02c6018f` | …delete only that session's archive |

`clean` lists what it is about to remove and asks before deleting. It never touches the live `UPWARD-STATS.md`, the state file, or the hook's parse cache. Archives appear on their own: when a session starts in a directory that already holds a previous session's table, the hook renames the old one to `UPWARD-STATS-<first 8 chars of its session id>.md` instead of destroying it.

State lives in `.upward/stats-state.json` under the project root: `{"enabled": true, "level": "call"}`. The skill only writes this file; the actual recording happens in the hook.

Everything lives inside the `.upward/` dot-directory so repo scans and glob patterns skip it by default. The directory is generated/local — add `.upward/` to your project's `.gitignore` if you don't want it tracked. (Plugin versions before the split wrote the files at the project root; the hook migrates them into `.upward/` automatically.)

When the sibling `upward` plugin is co-installed, the first row of each session's table also accounts for `upward`'s always-on `core.md` injection; without `upward` that row is omitted. Sibling files are located by globbing both layouts a plugin can live in — `<marketplace>/<plugin>/` when run from a marketplace directory, `<marketplace>/<plugin>/<version>/` when run from the install cache — and superseded versions in the cache (marked `.orphaned_at`) are skipped, so the installed version is the one that answers.

## The cost column

Every row carries an estimated USD cost, priced per call from the list prices in [`hooks/pricing.json`](hooks/pricing.json) and summed into the task row — so a task that mixed models still adds up. Cache reads are priced at 0.1× the model's input rate, 5-minute cache writes at 1.25×, and 1-hour cache writes at 2×; the transcript records which TTL each write used, so the two are billed apart rather than averaged.

- **A model with no price entry** shows `?`, and a task row mixing priced and unpriced calls shows `$0.0123+?` — a partial sum is never presented as the whole cost.
- **To fix or add a price**, drop a file of the same shape at `.upward/pricing.json` in your project. Its `models` entries override the shipped table per model id and survive plugin updates; only `input` and `output` are required per model.
- **These are defaults baked into the plugin, not a live feed** — check them against the current price list before trusting a total. Long-context (>200k input) premium tiers are not applied, because the transcript doesn't record which context tier a call was billed at.

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
│   ├── pricing.json              # USD/MTok list prices behind the cost column
│   └── upward_stats.py           # writes .upward/UPWARD-STATS.md when tracking is on
└── skills/
    └── upward-stats/             # /upward-stats on|off|level call|level task|clean
```
