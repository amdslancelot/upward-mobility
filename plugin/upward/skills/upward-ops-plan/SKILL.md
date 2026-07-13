---
name: upward-ops-plan
description: Turning a large task into a frozen plan.md — brief (goal, acceptance criteria, assumptions, risks) plus a task list with decidable acceptance criteria per item. Use this when starting a task with multiple deliverables, multiple steps, half a day or more of work, or output meant to stick around long-term. Stops once plan.md is frozen and hands off execution, review, and escalation to their own skills (`upward-ops-dispatch`, `upward-ops-review`, `upward-ops-judge`). Use when starting a large multi-step or multi-output task that needs a real plan before work begins; skip for single-file or one-off work.
---

# The Brief and the Plan (self-applied by the model)

> Reader: the main-thread model. This covers phase 0 (brief) and phase 1 (plan) of a large task — turning it into a frozen `plan.md` before any execution starts. Execution, review, and escalation are each their own skill's job once `plan.md` exists — see "Once plan.md is frozen" below.
> See the last section for when to use this; skip it for small tasks (the fixed overhead of writing a brief and a plan eats the benefit).

## The problem this solves

A Sonnet-tier commander defaults to "I'll just start working": it won't spontaneously write a task list, and it won't confirm direction before diving in. Both failures happen before a single line of execution — the most expensive mistake is flawless execution in the wrong direction, which is exactly why phase 0's brief can't be skipped.

## plan.md template (create before starting work, maintain throughout)

```
# <task name> — plan.md
Status: <planning / executing: item N / reviewing / revising>   Updated: <date>

## Brief (pinned down before work starts; this section stands in for a senior model's "get the first cut right")
- Goal and motivation: <what to do, why>
- Acceptance criteria (decidable, itemized): <"following these steps gets tests green" is fine; "written clearly" is not>
- Assumptions: <things you're taking as true in order to proceed — if something breaks, check this first for a wrong assumption>
- Risks / out of scope: <known risks, explicitly excluded scope>

## Task list
- [ ] 1. <task name>
  - Model: <haiku/sonnet/opus> — Reason: <why this tier>
  - Target: <files/scope to touch>   Product: <what it emits: file, diff, report>
  - Dependency: <task #s that must finish first, or —>
  - Acceptance / Review: <decidable done-criterion + who verifies (fresh-context agent)>
- [ ] 2. ...

## Checkpoints (log one every time a milestone passes its acceptance criteria)
- <milestone> → <git commit: sha or one-sentence description>

## Revision log (fill in after review)
- <finding> → fixed at <file:line> | or rejected: <one-sentence reason>
```

## The two phases this skill owns

**Phase 0 — brief (before starting work)**: write the goal, acceptance criteria, assumptions, and risks into the top of plan.md. If the direction is uncertain (requirements are vague, or you're guessing at the user's preferences or business context) → stop and confirm before starting work; see `upward-ops-judge` skill#2 for the criteria. Don't skip this step: flawless execution in the wrong direction is the most expensive failure there is.

**Phase 1 — plan**: break the task into a list, attach decidable acceptance criteria to each item, freeze it into plan.md. When filling in each item's `Model:` and `Target:` fields, use `upward-ops-dispatch` skill's tiered dispatch cheat sheet to pick the model and agent type — a task list that doesn't know what each item costs to execute isn't a real plan. If you drift mid-task or hit a `/compact`, this file is the anchor that gets you back to your task list.

## Once plan.md is frozen

Planning stops here — execution, review, and escalation are each their own skill's job, not this one's:

- Work through the list, dispatching each item per `upward-ops-dispatch` skill.
- Save progress and check items off in plan.md as you go; commit to git as a checkpoint at every milestone (the session can be interrupted anytime — only what's saved counts, and it leaves a reviewer something readable).
- Once every item is done, check the work is actually done and good enough per `upward-ops-review` skill.
- Stuck, need to escalate the model, or hit a signal the direction is wrong → `upward-ops-judge` skill.

Tell the user `plan.md` is ready rather than assuming you should charge ahead — e.g. "`plan.md` is frozen at N items — say go and I'll start executing item 1."

## What each design choice guards against in a weaker model

| Design | Guards against |
|---|---|
| Pin the brief first + stop when direction is uncertain | Getting the first cut wrong — the biggest gap in a weaker commander |
| Assumptions written into their own field | A rollback point when things break: check whether an earlier assumption was wrong, instead of staring at the line that threw the error |
| Plan frozen into plan.md | An anchor against mid-task drift; survives `/compact` |

## When to use this, and when not to

- **Use it**: tasks with multiple deliverables (half a day or more of work), output meant to stick around long-term (operating-rule files, external-facing docs, core code), or when the cost of a mistake exceeds the cost of one review round (see the cost-intuition section of `upward-ops-dispatch` skill for how to estimate that for your environment).
- **Don't use it**: a small single-file edit, a one-off draft, a question whose answer is already sitting in the conversation — the fixed cost of a brief and a plan eats the benefit; just do the work plus a lightweight check instead.
- **Scaled-down version (medium-sized, direction already clear)**: skip phase 0/1's back-and-forth entirely, but still dispatch a fresh-context review when the work is done (per `upward-ops-dispatch` skill) and work through every finding by fixing the source (per `upward-ops-review` skill) before reporting back.
