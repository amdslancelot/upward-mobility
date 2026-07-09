---
name: ops-plan
description: Quality-loop orchestration for large tasks (brief → plan → execute → review → revise). Use this when starting a task with multiple deliverables, multiple steps, half a day or more of work, or output meant to stick around long-term — write the brief first (goal, acceptance criteria, assumptions, risks) to pin the direction, then break it into plan.md, execute item by item saving checkpoints, dispatch a fresh-context review when done, and work through every finding by going back and fixing the source. Use when starting a large multi-step or multi-output task that needs the full plan-execute-review-revise loop; skip for single-file or one-off work.
---

# The Lifecycle of a Large Task: brief → plan → execute → review → revise (self-applied by the model)

> Reader: the main-thread model. This is the active orchestration layer for "large task, multiple deliverables" — it takes a senior model's working instincts and writes them down as steps you follow yourself.
> See the last section for when to use this; skip it for small tasks (the fixed overhead of the whole loop eats the benefit).
> The human-driven version of this (the skeleton a person types prompts against) lives in the source repo's `WEAK-MODEL-PROMPT-GUIDE.md`. Both files are readers of the same loop — if you edit one, check the other.

## The problem this solves

A Sonnet-tier commander defaults to "I executed, therefore I'm done": it won't spontaneously write a task list, won't confirm direction before starting, won't proactively dispatch a review, and when findings come back it'll just relay them to the user instead of going back to fix its own output. This loop is a senior model's instinct — a weaker model only runs it when the steps are spelled out explicitly. The most expensive mistake is flawless execution in the wrong direction — which is why phase 0's brief can't be skipped.

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
- [ ] 1. <item> — Acceptance: <decidable criterion>
- [ ] 2. ...

## Checkpoints (log one every time a milestone passes its acceptance criteria)
- <milestone> → <git commit: sha or one-sentence description>

## Revision log (fill in after review)
- <finding> → fixed at <file:line> | or rejected: <one-sentence reason>
```

## The five phases (walk through these yourself)

**Phase 0 — brief (before starting work)**: write the goal, acceptance criteria, assumptions, and risks into the top of plan.md. If the direction is uncertain (requirements are vague, or you're guessing at the user's preferences or business context) → stop and confirm before starting work; see `ops-judge` skill#3 for the criteria. Don't skip this step: flawless execution in the wrong direction is the most expensive failure there is.

**Phase 1 — plan**: break the task into a list, attach decidable acceptance criteria to each item, freeze it into plan.md. If you drift mid-task or hit a `/compact`, this file is the anchor that gets you back to your task list.

**Phase 2 — execute**: work through items one at a time. The moment an item is done, save it and check it off in plan.md before starting the next one. At every milestone (one item, or a batch of related items, passing acceptance) commit to git as a checkpoint. Dispatch per `ops-dispatch` skill; write delegation briefs from its templates.

If an item still fails after two fix attempts → roll back to the last checkpoint first (don't stack a third fix on broken state), then split by symptom:
- Looks like a **regression** (whack-a-mole failures, the same error resurfacing verbatim, something that used to work and doesn't anymore) → replay changes one at a time and bisect to the single culprit.
- Looks like a **wrong approach** (fighting the tool/framework, the files you need to touch are more than double your estimate) → don't bisect; re-plan directly or escalate with the failure trace.

Full criteria in `ops-judge` skill#4.

**Phase 3 — review**: once every item is complete, dispatch a freshly spawned fresh-context agent to review the entire output (model choice: haiku for mechanical checks like file existence/line counts/grep, sonnet for semantic checks like contradictions/ambiguity/unverified claims — if unsure, pick the higher tier; full selection guidance and prompt add-ons are in the `ops-review` skill). Give it the review dimensions explicitly, item by item. Require every finding to come with file:line and severity, require it to explicitly state "checked, nothing found" for aspects with no findings, and forbid it from editing any files.

**Phase 4 — revise**: work through every finding one by one — accept it and go fix the underlying output (not just relay it to the user and stop; this is the core obligation of the entire loop), or reject it with a one-sentence reason, and update plan.md's revision log. Only 0 unresolved findings counts as done. Cap review-revise at two rounds; if findings remain after the second round, list them out and ask the user.

**The definition of done is the end of phase 4, not the end of phase 2.**

Good: review comes back with 4 findings → you fix 3 at the source, reject 1 with a reason, log all 4, then report "done: 3 fixed, 1 rejected."
Bad: review comes back with 4 findings → you paste them to the user and stop. Relaying findings is not revising; phase 2 was never the finish line.

## What each design choice guards against in a weaker model

| Design | Guards against |
|---|---|
| Pin the brief first + stop when direction is uncertain | Getting the first cut wrong — the biggest gap in a weaker commander |
| Assumptions written into their own field | A rollback point when things break: check whether an earlier assumption was wrong, instead of staring at the line that threw the error |
| Plan frozen into plan.md | An anchor against mid-task drift; survives `/compact` |
| Save immediately after every item completes | The session can be interrupted anytime — only what's saved counts; also leaves the reviewer something readable |
| Checkpoint per milestone + roll back on failure | A weaker model defaults to stacking fixes on broken state; checkpoints let it return to known-good before bisecting or re-planning |
| Reviewer is fresh-context + forbidden from editing | Verification isn't self-verification; the reviewer only reports, accepting or rejecting is the commander's judgment call |
| "Go back and fix the underlying output" spelled out explicitly | A weaker model defaults to relaying findings and stopping, instead of going back to fix the prior round's results itself |
| "Rejections need a reason" | Guards against both extremes: rubber-stamping everything (reviewers have false positives) and ignoring everything |
| "Max two rounds" | Guards against an infinite review-revise loop burning budget |
| Definition of done placed last | A weaker model latches onto whatever explicit definition it saw most recently; leave it out and it'll call phase 2 the finish line |

## When to use this, and when not to

- **Use it**: tasks with multiple deliverables (half a day or more of work), output meant to stick around long-term (operating-rule files, external-facing docs, core code), or when the cost of a mistake exceeds the cost of one review round (roughly 35-40k subagent tokens per round — see the cost section of `ops-review` skill).
- **Don't use it**: a small single-file edit, a one-off draft, a question whose answer is already sitting in the conversation — the full loop's fixed cost eats the benefit; just do the work plus a lightweight check instead.
- **Scaled-down version (medium-sized, direction already clear)**: skip the back-and-forth of phases 0/1, but keep the one non-negotiable core obligation: dispatch a fresh-context review when done → work through every finding by fixing the source → only report back once revisions are done.
