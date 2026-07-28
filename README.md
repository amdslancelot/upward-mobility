# upward-mobility

**Making a lower-tier model smarter.** A Claude Code plugin that externalizes senior-model judgment into durable operating rules, so a cheaper model can run long agent sessions with consistent discipline — without a human re-explaining the same rules every time.

The goal is not parity with any particular top-tier model. It's to raise the floor: a capable model already carries the reflexes that make a long session go well — it verifies before claiming done, it doesn't re-read what it already knows, it notices when the direction is wrong and backs out instead of stacking another fix. A cheaper model has the raw ability to do all of that. What it lacks is the habit of doing it unprompted, and the habit is the first thing to decay over a long run. These rules are that habit, written down.

> Some older documents under `docs/` and `project/` still carry the original framing — "if the top-tier model isn't available or affordable, can a cheaper one reach parity on its own?" That framing is retired; read them for their measurements, not their premise.

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

docs/    # design notes and benchmark write-ups behind the plugin's rules
project/ # a related, markdown-only "ops template pack" precursor — a portable,
         # project-agnostic version of the same operating discipline, meant to be
         # copied into other repos rather than installed as a Claude Code plugin
```

## Install

### From this repo (local marketplace)

```
/plugin marketplace add /path/to/upward-mobility/plugin
/plugin install upward@upward-mobility
```

### From GitHub

```
/plugin marketplace add amdslancelot/upward-mobility --path plugin
/plugin install upward@upward-mobility
```

After installing, run `/reload-plugins` (or restart Claude Code) to pick it up, then verify with `/plugin` — `upward` should show as installed and enabled.

For token-usage tracking, install the second plugin the same way: `/plugin install upward-stats@upward-mobility`. It works with or without `upward`.

## Usage

Once installed, the core rules load automatically at the start of every session via the `SessionStart` hook — there's nothing to run to turn it on. From there, the model calls the matching skill itself via the Skill tool when a situation calls for it (starting a multi-step task, about to dispatch a subagent, something's broken, unsure if work is really done, feeling stuck). You can also steer it directly in plain language — "make a plan for this first," "dispatch a fresh review before you call this done," "roll back and try a different approach" — and it maps that back to the relevant rule.

To turn on token-usage logging, install `upward-stats` and run `/upward-stats on` (and `/upward-stats off` to stop). See `plugin/upward-stats/README.md` for the full command set.

## What the measurements support

The rules in this repo were not designed in the abstract — most of them exist because a measured run paid for their absence, and the ones that stopped earning their place were removed. Two honest conclusions from that series:

- **The cost mechanics are settled.** The current chassis runs at a predictable per-call rate with no cache-miss lottery, and the always-on text itself costs roughly a cent over a long run. The rules that cut re-reads more than pay for the ones that don't.
- **Quality is not.** No generic-discipline variant reliably produced a *delivering* build on its own. The runs that did deliver had domain-specific defect memory available to them — which is exactly what a general-purpose plugin must not ship, since it would make the plugin useless for building anything else. Project-side defect memory that the plugin reads when present is the open design question.

Adopt this for the cost structure and the long-run discipline. Don't adopt it expecting it to substitute for knowing your own domain's failure modes.

## Full documentation

See [`plugin/upward/README.md`](plugin/upward/README.md) for the complete plugin documentation, including exactly how the hooks load `core.md` and notes for adapting this plugin to another project or harness.
