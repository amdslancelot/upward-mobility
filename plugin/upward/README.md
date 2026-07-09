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
│   ├── hooks.json                # registers the SessionStart hook
│   └── activate.sh               # cats core.md to stdout on session start/resume/clear/compact
└── skills/
    ├── ops-plan/       # brief → plan.md → execute → review → revise loop for large tasks
    ├── ops-dispatch/   # how to pick agent type/model, delegation prompt templates, escalation ladder
    ├── ops-review/     # which review type needs which tool/model, findings triage
    ├── ops-judge/       # rubric: when to escalate, when a task is actually done, when to change course
    └── ops-diagnose/   # context bloat and environment-diagnosis playbook
```

## How it loads

The `SessionStart` hook (matches `startup`, `resume`, `clear`, `compact`) runs `activate.sh`, which prints `core.md` to stdout. Claude Code injects that stdout into the session as context — so the core rules are present from the very first turn, in every new or resumed session.

The five `ops-*` skills are **not** injected automatically. The core rules tell the model which skill to invoke via the Skill tool for a given situation (e.g. "starting a multi-step task" → `ops-plan`), so the detailed playbook only enters context when it's actually needed.

## Notes for adapting this to another project

Several sections in the skills are stamped with a verification date and are specific to the environment they were written in (model IDs, available agent types, which review tools are installed). If you copy this plugin to a different repo or harness, re-verify those sections rather than trusting the stamped values — each skill file says where to look.
