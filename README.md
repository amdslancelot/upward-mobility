# upward-mobility

**Making a lower-tier model smarter.** A Claude Code plugin that externalizes senior-model judgment into durable operating rules, so a cheaper model can run long agent sessions with consistent discipline — without a human re-explaining the same rules every time.

The goal is not parity with any particular top-tier model. It's to raise the floor: a capable model already carries the reflexes that make a long session go well — it verifies before claiming done, it doesn't re-read what it already knows, it notices when the direction is wrong and backs out instead of stacking another fix. A cheaper model has the raw ability to do all of that. What it lacks is the habit of doing it unprompted, and the habit is the first thing to decay over a long run. These rules are that habit, written down.

## The core idea

Long agentic coding sessions tend to drift: a weaker model forgets to verify its own work, dispatches tasks it should do itself, or keeps stacking fixes on a broken approach instead of rolling back. `upward` addresses this by splitting operating discipline into two layers:

- **A small always-on core** (`plugin/upward/core.md`, ~1.3K tokens), injected into every session at startup. It holds only the reflexes that must always be active — verification isn't self-verification, subagents are read-only, and the context-hygiene rules — plus a router that tells the model which on-demand skill to reach for in a given situation.
- **On-demand skills**, loaded only when the situation calls for them via Claude Code's `Skill` tool, so the detailed playbooks don't bloat every session's context budget.

Two structural rules run through the whole design:

- **One warm context does the work.** The main conversation is the only executor — it implements, refactors, and runs its own gates (build, test, real run) as it goes. Subagents are strictly read-only: they read, run, and report, used only for fresh-context reviews, read-backs, second opinions, and bulk reads that would otherwise flood the main context. They never write project files. This is structural rather than a judgment call because every judgment-shaped exception that was measured cost more than it saved — per-item builder dispatch lost to cold starts, and a three-builder split shipped its fatal defects exactly at the contract seams between the builders.
- **Verification isn't self-verification.** Each task item's completion claim stands on the worker's own execution evidence. The final "done and good enough" verdict, however, always gets exactly one independent pass — a fresh-context consumer-seat review performed by an agent that did not do the work, and whoever authored the plan or its acceptance criteria counts as having done the work too. That review is **static by default**: it reads the work in full and attacks it, and only builds, boots, or exercises the artifact when the user asked for execution-backed depth. Its verdict states which it did, so a static pass is never mistaken for a demonstrated one.

## Key features

- **Model escalation ladder** for dispatched read-only tasks: Haiku fails once → escalate to Sonnet with the error attached; Sonnet fails twice on the same subtask → escalate to Opus with both failure traces; once Opus cracks the pattern, the answer is written down so cheaper checks can reuse it.
- **Rollback-before-reapproach**: when a signal shows the current direction is wrong (whack-a-mole fixes, a recurring error, scope creep, fighting the tool), the rule is to revert to the last known-good commit before stacking another attempt on top of broken state.
- **Three narrow cases for asking the user**: an irreversible action that wasn't explicitly requested, two defensible options where only the user has the context to pick, or a task whose premise itself looks wrong.
- **Token-cost discipline as structural rules**, not suggestions: fetched external material is written to a file and only a short digest stays in the conversation; a bookkeeping edit (a check-off, a log line) never travels as a message of its own but rides inside the next real-work message; verbose gate output is piped to a file and judged by exit code rather than read back in full — and read in full the moment it fails.
- **Cost, not token count, is the unit.** The token types are priced far apart, so the rules target the expensive ones — everything added to the conversation is re-read by every later call.

## The skills

| Skill | What it covers |
|---|---|
| `upward-ops-plan` | Turns a brief into a frozen `plan.md` before execution starts, for tasks with multiple deliverables or half a day or more of work; hands off execution/review/escalation to the skills below. |
| `upward-ops-dispatch` | How to pick agent type, model tier, and dispatch level; delegation prompt templates; the escalation ladder; how to dispatch a review. |
| `upward-ops-review` | Whether a completed task actually counts as done and good enough — the quality floor by artifact type, and how to triage findings. |
| `upward-ops-judge` | Rubric for escalating the model vs. rolling back and changing course, when to stop and ask the user, and taste/judgment calls. |
| `upward-harness-diagnose` | Standalone harness playbook: where the harness leaks tokens or context, `/compact` vs. `/clear`. |
| `upward-debug` | Standalone signal-first debugging loop: build a red pass/fail signal before touching any code, nested round budgets, environment checklist. |

`upward-ops-plan`, `upward-ops-dispatch`, `upward-ops-review`, and `upward-ops-judge` form one operating loop (plan → execute/dispatch → review → judge-when-stuck). `upward-debug` and `upward-harness-diagnose` are standalone tools usable with or without that loop — which is why their names drop the `-ops-` infix.

Token-usage tracking used to ship inside this plugin as a seventh skill. It now lives in the separate **`upward-stats`** plugin, installable on its own.

## Repo layout

```
plugin/
├── .claude-plugin/marketplace.json   # marketplace manifest listing both plugins
├── upward/                           # the operating-discipline plugin
│   ├── .claude-plugin/plugin.json    # plugin manifest (name, version, description)
│   ├── core.md                       # always-on rules, injected by the SessionStart hook
│   ├── README.md                     # full plugin documentation (install, usage, structure)
│   ├── hooks/
│   │   ├── hooks.json                # registers the SessionStart hook
│   │   └── activate.sh               # cats core.md to stdout on session start/resume/clear/compact
│   └── skills/                       # the six on-demand skills listed above
│       ├── upward-ops-plan/
│       ├── upward-ops-dispatch/
│       ├── upward-ops-review/
│       ├── upward-ops-judge/
│       ├── upward-harness-diagnose/
│       └── upward-debug/
└── upward-stats/                     # standalone token-usage tracker
    ├── .claude-plugin/plugin.json
    ├── README.md
    ├── hooks/
    │   ├── hooks.json                # registers the Stop and SubagentStop hooks
    │   └── upward_stats.py           # writes .upward/UPWARD-STATS.md
    └── skills/upward-stats/          # the /upward-stats toggle

project/ # a related, markdown-only "ops template pack" precursor — a portable,
         # project-agnostic version of the same operating discipline, meant to be
         # copied into other repos rather than installed as a Claude Code plugin
```

## Install

This repo is a single marketplace, `upward-mobility`, holding two plugins that install and run independently:

| Plugin | What it gives you |
|---|---|
| `upward` | The operating discipline — the always-on core plus the six on-demand skills. |
| `upward-stats` | Token-usage logging to `.upward/UPWARD-STATS.md`, toggled with `/upward-stats`. |

Neither requires the other. Installing both is the usual case: `upward` supplies the rules, `upward-stats` shows what they cost.

**Step 1 — add the marketplace once.** From GitHub:

```
/plugin marketplace add amdslancelot/upward-mobility --path plugin
```

Or from a local clone:

```
/plugin marketplace add /path/to/upward-mobility/plugin
```

**Step 2 — install whichever you want.** Both plugins come from the marketplace added above, so there's nothing further to add:

```
/plugin install upward@upward-mobility
/plugin install upward-stats@upward-mobility
```

**Step 3 — reload.** Run `/reload-plugins` (or restart Claude Code), then check `/plugin`: each plugin you installed should show as installed and enabled. `upward` takes effect on the next session start, since its rules load through the `SessionStart` hook.

## Usage

Once installed, the core rules load automatically at the start of every session via the `SessionStart` hook — there's nothing to run to turn it on. From there, the model calls the matching skill itself via the Skill tool when a situation calls for it (starting a multi-step task, about to dispatch a subagent, something's broken, unsure if work is really done, feeling stuck). You can also steer it directly in plain language — "make a plan for this first," "dispatch a fresh review before you call this done," "roll back and try a different approach" — and it maps that back to the relevant rule.

With `upward-stats` installed, tracking is on by default; `/upward-stats off` stops it, and `/upward-stats level call` adds a row per API call on top of the per-prompt row.

## Does it work?

The rules here were not designed in the abstract. One fixed build task was run many times, each run on a different plugin version, and each measured on real dollars and on the quality of what shipped. Most rules exist because a run paid for their absence; the ones that stopped earning their place were removed. One thing has to be said about that series before any number from it means anything.

**Review depth turned out not to be unifiable.** How hard the reviewer looked moved the score more than the plugin version did — re-grading a single unchanged artifact against a stricter standard moved it by more than three points. So the only comparison worth reading is the one board on which all 19 runs were graded to a single standard.

On that board, the first plugin version and the current one against the runs with no plugin:

| Condition | Delivery tier | Headline |
|---|---|---|
| plugin 0.1.x | **T1 — delivers** | 9.6 |
| plugin 0.6.0 | **T1 — delivers** | 9.5 |
| no plugin, verified zero injection | T2 — delivers with faults | 6.8 |
| no plugin, but an old core.md was injected — "bare" Opus / Fable / Sonnet | T3 — does not deliver | 4.4 / 4.3 / 4.2 |

Both plugin versions land a full delivery tier above the cleanest no-plugin control, on the same task and the same grading standard, and two tiers above the older bare runs. That is what this repo claims: the discipline itself moves what a model actually ships.

Cost behaves independently and is measured separately: zero cache misses across 338 small-write calls, per-call deliberation back at its floor, and the always-on text itself costing about a cent over a long run. Total spend is a different question and is not settled — the remaining gap to the cheapest measured run is build footprint (calls × context), which no rule currently governs.

## Full documentation

Each plugin documents itself:

- [`plugin/upward/README.md`](plugin/upward/README.md) — the complete rule set, exactly how the hook loads `core.md`, and notes for adapting the plugin to another project or harness.
- [`plugin/upward-stats/README.md`](plugin/upward-stats/README.md) — what the hook records, the columns in `.upward/UPWARD-STATS.md`, and the full `/upward-stats` command set.
