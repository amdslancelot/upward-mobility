# Big-task lifecycle: brief → plan → execute → review → revise (model self-applies)

> Reader: the main-conversation model. This is the proactive orchestration layer for "large multi-output tasks" — it writes down the top-tier model's working instincts as steps you follow yourself.
> See the last section for when to use this; skip it for small tasks (the fixed cost of the whole loop eats the payoff).
> The human-driven version (the skeleton a person hands-feeds as a prompt) lives in `WEAK-MODEL-PROMPT-GUIDE.md` in the source repo. The two files are two readers of the same loop — if you edit one, go check the other.

## The problem this solves

A Sonnet-tier commander defaults to "declare victory the moment execution stops": it won't spontaneously write a task list, won't confirm direction first, won't proactively dispatch a review, and when it gets findings back it'll just relay them to the user instead of going back and fixing its own output. This loop is a top-tier model's instinct — a weaker model only runs it if the steps are spelled out. The most expensive mistake is executing perfectly after getting the direction wrong, which is why phase 0's brief can't be skipped.

## plan.md template (build before starting work, maintain throughout)

```
# <task name> — plan.md
Status: <planning / executing: item N / reviewing / revising>   Updated: <date>

## Brief (nail this down before starting; this section substitutes for the top-tier model's "get the first cut right")
- Goal and motivation: <what, and why>
- Acceptance criteria (judgable, itemized): <"runnable per instructions, tests green" is fine; "written clearly" is not>
- Assumptions: <things you're taking as true in order to proceed — when something breaks, check this box first for a wrong assumption>
- Risks / out of scope: <known risks, explicitly excluded scope>

## Task list
- [ ] 1. <item> — Acceptance: <judgable standard>
- [ ] 2. ...

## Checkpoints (log one every time a milestone clears acceptance)
- <milestone> → <git commit: sha or one-line description>

## Revision log (fill in after review)
- <finding> → fixed at <file:line> | or rejected: <one-line reason>
```

## The five phases (walk through these yourself)

**Phase 0 — brief (before starting work)**: write the goal, acceptance criteria, assumptions, and risks into the top of plan.md. If direction is uncertain — requirements are fuzzy, or you're guessing the user's preferences or business context — stop and confirm before starting; see `ops/judgment-rubrics.md`#3 for the rubric. Don't skip this step: perfect execution in the wrong direction is the most expensive failure there is.

**Phase 1 — plan**: break the task into a list, attach judgable acceptance criteria to each item, freeze it into plan.md. If you drift mid-task or run `/compact`, this file is the anchor that gets you back to your task list.

**Phase 2 — execute**: work through items one by one. Save and check each one off in plan.md the moment it's done, then move to the next. Commit to git as a checkpoint at every milestone (one item, or a batch of related items, clearing acceptance).

If an item fails twice on the fix, roll back to the last checkpoint first, don't stack a third fix on a broken state. Then branch on the symptom:
- Looks like a **regression** (whack-a-mole errors, the same error reappearing verbatim, something that used to work and now doesn't) → replay changes one at a time and bisect to the single culprit.
- Looks like a **wrong approach** (you're fighting the tool/framework, or the files you need to touch are running at double your estimate) → don't bisect. Re-plan directly or escalate with the failure trail attached.

Full rubric at `ops/judgment-rubrics.md`#4.

**Phase 3 — review**: once every item is done, dispatch a freshly-opened fresh-context agent to review all the output. Model choice: haiku for mechanical checks (file existence, line counts, grep), sonnet for semantic checks (contradictions, ambiguity, unverified claims) — pick the level up when unsure. Full selection rules and prompt add-ons in `ops/review-dispatch.md`. Hand it the review dimensions one by one, require every finding to carry a file:line plus severity, require it to state explicitly "checked, no findings" for any dimension with nothing wrong, and tell it not to touch any files.

**Phase 4 — revise**: once findings come back, dispose of each one. If you accept it, go back and fix the corresponding output — relaying it to the user and stopping there is NOT enough; that's the core obligation of the entire loop. If you reject it, write one line of reasoning. Update plan.md's revision log either way. Only done when 0 findings remain unresolved; cap review-and-revise at two rounds — if findings remain after round two, list them and ask the user.

**The definition of done is the end of phase 4, not the end of phase 2.**

**Good example**: review comes back with 4 findings → you fix 3 at the source, reject 1 with a reason, log all 4, then report "done: 3 fixed, 1 rejected." ✅
**Bad example**: review comes back with 4 findings → you paste them to the user and stop. Relaying findings is not revising; phase 2 was never the finish line. ❌

## What each design defends against in a weak model

| Design | Defends against |
|---|---|
| Nail the brief first + stop when direction is uncertain | Getting the first cut of direction wrong — the biggest gap in a weak commander |
| Assumptions written into their own box | Having a place to backtrack to when things break: check whether an earlier assumption was wrong, instead of staring at the error line |
| Plan frozen into plan.md | An anchor against mid-task drift; survives `/compact` |
| Save immediately after every item | Sessions can be interrupted anytime; only what's saved counts, and it leaves the reviewer something readable |
| Checkpoint per milestone + roll back on failure | A weak model defaults to stacking fixes on a broken state; checkpoints let it return to known-good before bisecting or re-planning |
| Reviewer is fresh-context + forbidden to edit files | Verification isn't self-verification; the reviewer only reports, and whether to accept is the commander's call |
| "Go back and fix the corresponding output" spelled out explicitly | A weak model defaults to relaying findings and stopping; it won't go back and fix the previous round's results on its own |
| "Write a reason when rejecting" | Guards against the two extremes: rubber-stamping everything (reviewers have false positives) and ignoring everything |
| "Maximum two rounds" | Guards against an infinite review-revise loop burning through budget |
| Definition of done placed last | A weak model trusts whatever definition it saw last; skip it and the model calls it quits at phase 2 |

## When to use this, when not to

- **Use it**: multi-output tasks (half a day or more of work), output meant to be relied on long-term (institutional docs, external-facing documents, core code), when the cost of a mistake exceeds the cost of one review round (about 35–40k subagent tokens per round — see the cost section in `ops/review-dispatch.md`).
- **Don't use it**: small single-file edits, one-off drafts, questions whose answer is already in the conversation — the loop's fixed cost eats the payoff here; just do it plus a light verification pass.
- **Shortened version (medium-sized, direction already clear)**: skip the back-and-forth of phases 0/1, but keep the core, non-skippable obligation: dispatch a fresh-context review once done → dispose of every finding by going back and fixing → only report once the fixes are done.
