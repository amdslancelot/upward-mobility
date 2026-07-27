# upward-mobility

A Claude Code plugin that externalizes senior-model judgment into durable operating rules, so cheaper models (Sonnet, Haiku) can run long agent sessions with consistent discipline — without a human re-explaining the same rules every time.

## The core idea

Long agentic coding sessions tend to drift: a weaker model forgets to verify its own work, dispatches tasks it should do itself, or keeps stacking fixes on a broken approach instead of rolling back. `upward` addresses this by splitting operating discipline into two layers:

- **A small always-on core** (`plugin/upward/core.md`), injected into every session at startup. It holds only the reflexes that must always be active — verification isn't self-verification, subagents are read-only, roll back before re-approaching — plus a router that tells the model which on-demand skill to reach for in a given situation.
- **On-demand skills**, loaded only when the situation calls for them via Claude Code's `Skill` tool, so the detailed playbooks don't bloat every session's context budget.

Two structural rules run through the whole design:

- **One warm context does the work.** The main conversation is the only executor — it implements, refactors, and runs its own gates (build, test, real run) as it goes. Subagents are strictly read-only: they read, run, and report, used only for fresh-context reviews, read-backs, second opinions, and bulk reads that would otherwise flood the main context. They never write project files.
- **Verification isn't self-verification.** Each task item's completion claim stands on the worker's own execution evidence. The final "done and good enough" verdict, however, always gets exactly one independent pass — a fresh-context consumer-seat review performed by an agent that did not do the work. That review defaults to a **LOW**-effort static-only pass (full source read plus a sweep of known defect classes, no execution), clearly marked as such; deeper **MED** (boot and probe) or **HIGH** (live demonstration) levels are only used when explicitly requested — the plugin never escalates spend on its own.

## Key features

- **Model escalation ladder** for dispatched read-only tasks: Haiku fails once → escalate to Sonnet with the error attached; Sonnet fails twice on the same subtask → escalate to Opus with both failure traces; once Opus cracks the pattern, the answer is written down so cheaper checks can reuse it.
- **Rollback-before-reapproach**: when a signal shows the current direction is wrong (whack-a-mole fixes, a recurring error, scope creep, fighting the tool), the rule is to revert to the last known-good commit before stacking another attempt on top of broken state.
- **Three narrow cases for asking the user**: an irreversible action that wasn't explicitly requested, two defensible options where only the user has the context to pick, or a task whose premise itself looks wrong.
- **Token-cost discipline as structural rules**, not suggestions: external fetches always go through a read-only reader subagent instead of the main thread calling WebSearch/WebFetch directly; file writes are batched into as few API calls as possible; verbose gate output is piped to a file and judged by exit code rather than read back in full.
- **Per-prompt / per-call usage tracking** via `/upward-stats on|off|level task|level call`, logged automatically to `.upward/UPWARD-STATS.md` by the plugin's `Stop` and `SubagentStop` hooks.

## The skills

| Skill | What it covers |
|---|---|
| `upward-ops-plan` | Turns a brief into a frozen `plan.md` before execution starts, for tasks with multiple deliverables or half a day or more of work; hands off execution/review/escalation to the skills below. |
| `upward-ops-dispatch` | How to pick agent type, model tier, and dispatch level; delegation prompt templates; the escalation ladder; how to dispatch a review. |
| `upward-ops-review` | Whether a completed task actually counts as done and good enough — the quality floor by artifact type, and how to triage findings. |
| `upward-ops-judge` | Rubric for escalating the model vs. rolling back and changing course, when to stop and ask the user, and taste/judgment calls. |
| `upward-harness-diagnose` | Standalone harness playbook: where the harness leaks tokens or context, `/compact` vs. `/clear`. |
| `upward-debug` | Standalone signal-first debugging loop: build a red pass/fail signal before touching any code, nested round budgets, environment checklist. |
| `upward-stats` | `/upward-stats on\|off\|level task\|level call` — per-prompt/per-call token usage logging. |

`upward-ops-plan`, `upward-ops-dispatch`, `upward-ops-review`, and `upward-ops-judge` form one operating loop (plan → execute/dispatch → review → judge-when-stuck). `upward-debug` and `upward-harness-diagnose` are standalone tools usable with or without that loop. `upward-stats` is an unrelated toggle for cost visibility.

## Repo layout

```
plugin/
├── .claude-plugin/marketplace.json   # marketplace manifest listing the "upward" plugin
└── upward/
    ├── .claude-plugin/plugin.json    # plugin manifest (name, version, description)
    ├── core.md                       # always-on rules, injected by the SessionStart hook
    ├── README.md                     # full plugin documentation (install, usage, structure)
    ├── hooks/
    │   ├── hooks.json                 # registers SessionStart, Stop, and SubagentStop hooks
    │   ├── activate.sh                 # cats core.md to stdout on session start/resume/clear/compact
    │   └── upward_stats.py             # Stop/SubagentStop hook: writes .upward/UPWARD-STATS.md
    └── skills/                        # the seven on-demand skills listed above
        ├── upward-ops-plan/
        ├── upward-ops-dispatch/
        ├── upward-ops-review/
        ├── upward-ops-judge/
        ├── upward-harness-diagnose/
        ├── upward-debug/
        └── upward-stats/

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

## Usage

Once installed, the core rules load automatically at the start of every session via the `SessionStart` hook — there's nothing to run to turn it on. From there, the model calls the matching skill itself via the Skill tool when a situation calls for it (starting a multi-step task, about to dispatch a subagent, something's broken, unsure if work is really done, feeling stuck). You can also steer it directly in plain language — "make a plan for this first," "dispatch a fresh review before you call this done," "roll back and try a different approach" — and it maps that back to the relevant rule.

To turn on token-usage logging, run `/upward-stats on` (and `/upward-stats off` to stop). See `plugin/upward/skills/upward-stats/SKILL.md` for the full command set.

## Full documentation

See [`plugin/upward/README.md`](plugin/upward/README.md) for the complete plugin documentation, including the review-effort level table (LOW/MED/HIGH), exactly how the hooks load `core.md`, and notes for adapting this plugin to another project or harness.
