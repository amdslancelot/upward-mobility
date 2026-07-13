# upward

A Claude Code plugin that externalizes senior-model judgment into durable operating rules, so cheaper models (Sonnet, Haiku) can run long sessions without a human re-explaining the same discipline every time.

It injects a small always-on core of rules at session start, and defers the detailed playbooks to on-demand skills so they don't bloat every session's context.

## What it does

- **Commander doesn't descend.** Bulk reading, repo scans, batch edits, and verification runs get delegated to subagents. The main conversation only handles task breakdown, judgment calls, and talking to the user.
- **Verification isn't self-verification.** Completion claims need execution evidence (build, test, real run, read-back). Verification always goes to a fresh agent, never back to the agent that did the work.
- **Model escalation ladder.** Haiku fails once → escalate to Sonnet with the error attached. Sonnet fails twice on the same subtask → escalate to Opus with both failure traces. Opus solves the pattern → write it down as explicit steps and hand it back down to Sonnet/Haiku.
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

## Structure

```
plugin/upward/
├── .claude-plugin/plugin.json   # plugin manifest
├── core.md                      # always-on rules, injected by the SessionStart hook
├── hooks/
│   ├── hooks.json                # registers the SessionStart and Stop hooks
│   ├── activate.sh               # cats core.md to stdout on session start/resume/clear/compact
│   └── upward_stats.py           # Stop hook: writes UPWARD-STATS.md when upward-stats is on
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

`upward-stats` is a standalone toggle, unrelated to the always-on core rules: `/upward-stats on` writes `.upward-stats-state.json` at the project root, and the plugin's `Stop` hook checks that file after every turn, rewriting `UPWARD-STATS.md` with token usage grouped by prompt (and by individual API call, including model, at `level call`). `/upward-stats off` turns it back off. Both `UPWARD-STATS.md` and `.upward-stats-state.json` are generated/local — add them to your project's `.gitignore` if you don't want them tracked.

## Notes for adapting this to another project

Several sections in the skills are stamped with a verification date and are specific to the environment they were written in (model IDs, available agent types, which review tools are installed). If you copy this plugin to a different repo or harness, re-verify those sections rather than trusting the stamped values — each skill file says where to look.
