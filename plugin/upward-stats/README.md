# upward-stats

A Claude Code plugin that logs per-API-call (or, collapsed, per-prompt) token usage and estimated cost for a session to `.upward/UPWARD-STATS.md`.

It was originally part of the [`upward`](../upward) operating-discipline plugin and is now packaged on its own — it works with or without `upward` installed.

## What it does

A `Stop` / `SubagentStop` hook (`hooks/upward_stats.py`) runs after every turn and after every finished subagent. When tracking is enabled it resumes parsing the session transcript from where it left off, sums token usage per API call, groups the calls into tasks (one per prompt), and appends the new rows to `.upward/UPWARD-STATS.md` — it never rereads the whole transcript or rewrites the whole file. Columns: calls, output, cache write, cache read, fresh input, cost, model. Skill loads are recorded as informational rows with an estimated injected-token size.

Output at `level: call` — one prompt, the three API calls it took, and the skill it pulled in:

| task | subtask | calls | output | cache write | cache read | fresh input | cost | model |
|---|---|---|---|---|---|---|---|---|
| (session start) | [injected] upward/core.md (~1,408 tok) | 0 | 0 | 0 | 0 | 0 | - | - |
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

## Standing injections

A `SessionStart` hook can put text into context without any of it passing through the conversation — `upward` does exactly that, `cat`-ing its `core.md` when a session starts. No tool call, no message; the only trace is that every later API call carries it. A table that ignores it understates the standing cost of the session.

The transcript does record it, as the hook's own output, so that is what gets measured — **the text that actually entered context**, not a file read as a stand-in for it. Both injection channels count: a hook's raw stdout and a returned `additionalContext`. Each becomes a `(session start)` row labelled with the hook's matcher and the first line of what it injected:

```
| (session start) | [injected] startup: Upward-Mobility Operating Discipline (a… (~1,408 tok) | 0 | 0 | 0 | 0 | 0 | - | - |
```

Token columns stay zero for the same reason skill rows do — the text is already inside the following call's cache write, so a number there would double count.

Treat the size as a **lower bound**. It is characters ÷ 4, and the harness wraps injected text before it reaches the model. Two identical one-prompt sessions differing only in whether `upward` was enabled came out 1,891 cache-read tokens apart, against an estimate of ~1,408 for the same injection — the estimate was about a third low. It is a scale marker, not an invoice; the `cost` column, which comes from the API's own usage numbers, is the invoice.

Measuring the record rather than the file means the count can't drift from reality: a plugin that is installed but **disabled** never runs its hook, so nothing is recorded and nothing is claimed; a `resume` or `compact` that re-injects mid-session produces another row, in place, rather than being silently folded into the first one; and a `SessionStart` hook you wrote yourself in `settings.json` is counted the same as a plugin's, with nothing to declare.

Compaction adds a second kind of row. Discarding the conversation would also discard the text of any skill loaded into it, so that text is written back — and recorded, which is what makes it countable. Those become `(re-injected)` rows: a skill already paid for, paid for again. Replaying a real session through the hook shows both kinds and what they add up to:

```
| (session start) | [injected] resume: Upward-Mobility Operating Discipline (a… (~1,323 tok) | …
| (session start) | [injected] resume: CAVEMAN MODE ACTIVE — level: full (~412 tok)          | …
| (session start) | [injected] resume: PONYTAIL MODE ACTIVE — level: full (~1,430 tok)       | …
| (re-injected)   | [injected] upward:ops-judge (~1,942 tok)                                 | …
| (re-injected)   | [injected] upward:ops-diagnose (~1,909 tok)                              | …
| (session start) | [injected] compact: Upward-Mobility Operating Discipline (a… (~1,323 tok) | …
| (session start) | [injected] compact: PONYTAIL MODE ACTIVE — level: full (~1,430 tok)      | …
| (session start) | [injected] compact: CAVEMAN MODE ACTIVE — level: full (~412 tok)         | …
```

The three always-on plugins cost ~3,165 tokens at `resume` and the same ~3,165 again at `compact`, because a compaction re-runs the `SessionStart` hooks; the two loaded skills cost another ~3,851 on the way through. Roughly 7,000 of the ~10,200 tokens of injected text in that session were re-payment for text that had already been in context.

Skill loads are a separate case: the transcript records that a skill was invoked but usually not its text, so a skill's size label still comes from reading its `SKILL.md`. Sibling plugins are located by globbing both layouts a plugin can live in — `<marketplace>/<plugin>/` in a marketplace directory, `<marketplace>/<plugin>/<version>/` in the install cache — requiring a `.claude-plugin/plugin.json` to count as a plugin at all, and skipping cache versions marked `.orphaned_at` so the installed version is the one that answers.

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
