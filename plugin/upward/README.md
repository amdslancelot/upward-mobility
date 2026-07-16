# upward

A Claude Code plugin that externalizes senior-model judgment into durable operating rules, so cheaper models (Sonnet, Haiku) can run long sessions without a human re-explaining the same discipline every time.

It injects a small always-on core of rules at session start, and defers the detailed playbooks to on-demand skills so they don't bloat every session's context.

## What it does

- **One warm context does the work.** The main context executes all implementation itself and runs its own gates as it goes; subagents are read-only — the end-of-run consumer-seat review, read-backs, second opinions, bulk reads, and research digests — and never write project files.
- **Verification isn't self-verification.** Each item's completion claim stands on the worker's own execution evidence (build, test, real run); the final done-and-good-enough verdict gets exactly one independent pass — a fresh-context consumer-seat review, never performed by whoever did the work. **That review runs at LOW effort by default: a static-only pass** (full source read plus a sweep of the known recurring-defect classes; no build, no boot) whose verdict carries a STATIC-ONLY marker naming what was not checked. If you want execution-backed verification — build, boot, and probes (MED) or a live demonstration of findings (HIGH) — request the level in your prompt; the plugin recommends deeper levels when they matter but never escalates the spend on its own.
- **Model escalation ladder for dispatched (read-only) tasks.** Haiku fails once → escalate to Sonnet with the error attached. Sonnet fails twice on the same subtask → escalate to Opus with both failure traces. Opus cracks the pattern → write it down so cheaper checks can reuse it; any edits that follow are applied by the main context.
- **Roll back before re-approaching.** When a signal says the direction is wrong (whack-a-mole fixes, the same error recurring, scope doubling, fighting the tool), revert to the last known-good commit before stacking another fix on broken state.
- **Three narrow cases for asking the user.** Irreversible and not explicitly requested; two defensible options where the right one depends on context only the user has; or the task's premise itself looks wrong.

Full text of the always-on core lives in `core.md`.

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

After installing, run `/reload-plugins` (or restart Claude Code) to pick it up. Verify with `/plugin` — `upward` should show as installed and enabled.

## Usage

Once installed, the core rules load automatically at the start of every session — there's nothing to run to turn it on. From there:

- **You don't need to invoke the skills yourself.** `core.md` tells the model which skill fits a given situation (starting a multi-step task, about to dispatch a subagent, something's broken, unsure if work is actually done, feeling stuck) and it calls the matching skill via the Skill tool on its own. Skills only enter context when the situation actually calls for them.
- **You can still steer it directly** by naming what you want in plain language — "make a plan for this first," "dispatch a fresh review before you call this done," "that's not right, roll back and try a different approach" — the model maps that back to the relevant rule.
- **`/upward-stats on`** turns on per-prompt (and, at `level call`, per-API-call) token usage logging to `.upward/UPWARD-STATS.md`; `/upward-stats off` turns it back off. See `skills/upward-stats/` for the full command set.

### Setting the review-effort level

Every task's completion claim is checked by exactly one fresh-context review before the model calls the work done. That review defaults to **LOW**: a static-only pass (full source read, plus a sweep of known recurring-defect classes, no execution) whose verdict carries a **STATIC-ONLY** marker naming what wasn't checked. The plugin never raises this on its own — deeper verification only happens if you ask for it in your request:

| level | what it adds | when to ask for it |
|---|---|---|
| **LOW** (default) | Nothing to ask for — this is what happens if you say nothing. | Everyday work; docs; changes with no runtime surface. |
| **MED** | Installs and boots the artifact, runs any self-check it ships, probes the auth/entry gate and one feature path. | You want the review to actually run the thing, not just read it. |
| **HIGH** | MED, plus a live demonstration of the top finding and one repeatable-path check (e.g. run a scheduled job twice). | High-stakes changes where a runtime-only defect (boot failure, race condition, framework behavior) would be expensive to miss. |

To ask for a deeper pass, say so directly in your request, e.g. "review this at MED effort" or "I want a HIGH-effort review before you call this done." The reviewer's own report always states which level it ran and shows that level's evidence; if it thinks the work deserves more scrutiny than you asked for, it says so in a recommended-level line rather than spending more than requested.

(This is the plugin's own internal end-of-task review, distinct from the separate `/code-review` command's `low`/`medium`/`high`/`max`/`ultra` scale for auditing a diff — see `/code-review` for that.)

## Structure

```
plugin/upward/
├── .claude-plugin/plugin.json   # plugin manifest
├── core.md                      # always-on rules, injected by the SessionStart hook
├── hooks/
│   ├── hooks.json                # registers the SessionStart, Stop, and SubagentStop hooks
│   ├── activate.sh               # cats core.md to stdout on session start/resume/clear/compact
│   └── upward_stats.py           # Stop/SubagentStop hook: writes .upward/UPWARD-STATS.md when upward-stats is on
└── skills/
    ├── upward-ops-plan/         # brief → frozen plan.md for large tasks; hands off execution/review/escalation to the skills below
    ├── upward-ops-dispatch/     # how to pick agent type/model/tier, delegation prompt templates, escalation ladder, how to dispatch a review
    ├── upward-ops-review/       # is a completed task actually done and good enough — quality floor by artifact type, findings triage
    ├── upward-ops-judge/        # rubric: when to escalate the model vs. roll back and change course, when to ask the user, taste-judgment honesty clause
    ├── upward-harness-diagnose/ # standalone harness playbook: token leaks, context bloat, /compact vs /clear
    ├── upward-debug/            # standalone signal-first debugging loop: red signal before any fix, nested round budgets, environment checklist
    └── upward-stats/             # /upward-stats on|off|level task|level call — per-prompt/per-call token usage log
```

## How it loads

The `SessionStart` hook (matches `startup`, `resume`, `clear`, `compact`) runs `activate.sh`, which prints `core.md` to stdout. Claude Code injects that stdout into the session as context — so the core rules are present from the very first turn, in every new or resumed session.

None of the six skills above are injected automatically. The core rules tell the model which skill to invoke via the Skill tool for a given situation (e.g. "starting a multi-step task" → `upward-ops-plan`), so the detailed playbook only enters context when it's actually needed. Four of them (`upward-ops-plan`, `upward-ops-dispatch`, `upward-ops-review`, `upward-ops-judge`) form one operating loop — plan hands off to dispatch for execution, review checks the result, judge handles getting stuck — while `upward-debug` and `upward-harness-diagnose` are standalone tools usable with or without that loop, which is why their names drop the `-ops-` prefix.

`upward-stats` is a standalone toggle, unrelated to the always-on core rules: `/upward-stats on` writes `.upward/stats-state.json` under the project root, and the plugin's `Stop` hook checks that file after every turn, appending token usage grouped by prompt (and by individual API call, including model, at `level call`) to `.upward/UPWARD-STATS.md`. The same script also runs on `SubagentStop`, so a dispatched subagent's own token usage is recorded as an `[agent]` row even in a headless one-turn session, where `Stop` fires only once. `/upward-stats off` turns it back off. Everything lives inside the `.upward/` dot-directory so repo scans and glob patterns skip it by default; the directory is generated/local — add `.upward/` to your project's `.gitignore` if you don't want it tracked. (Older plugin versions wrote the three files at the project root; the hook migrates them into `.upward/` automatically.) The hook anchors everything it writes to the directory the session started in — recovered from the session transcript's project slug — so a mid-session `cd` into a subdirectory does not scatter a fresh `.upward/` there.

## Notes for adapting this to another project

Several sections in the skills are stamped with a verification date and are specific to the environment they were written in (model IDs, available agent types, which review tools are installed). If you copy this plugin to a different repo or harness, re-verify those sections rather than trusting the stamped values — each skill file says where to look.
