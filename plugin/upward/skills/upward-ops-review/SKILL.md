---
name: upward-ops-review
description: How to judge whether a completed task is actually done and good enough. Covers the four-part done-criteria rubric, the quality floor by artifact type (code, docs, architectural judgment calls, general claims), and what to do once review findings come back — accept or reject each one individually, apply fixes at the source, report with numbers. (Dispatching the review itself — which tool, which model, prompt structure — lives in `upward-ops-dispatch`.) Use after a task's execution is finished, to decide whether it's actually done.
---
# How to review task quality after a task is done

> Audience: the main-conversation model. This answers "is this task actually finished, by what bar, and what do I do with the findings once I have them" — not "how do I dispatch the review" (that's `upward-ops-dispatch skill`, which now owns every "how to hand this off" question including review-shaped ones).
> If a review turns up something you can't resolve on your own — stuck, need to escalate the model, or it's a taste call only the user can make — see `upward-ops-judge`.

## 1. When a task actually counts as done

**Rule**: all four must pass:
1. Every acceptance criterion checked off individually (not "roughly matches").
2. Verification comes from execution results (test output, a real run, a read-back) — not "I read the code and it looks right."
3. The report contains no hedges like "should," "probably," "in theory" around the completion claim.
4. Acceptance criteria you authored yourself are a floor, not the definition of done — at least one verification pass must exercise the artifact the way its real consumer would, hunting for what the criteria don't cover. Every box green while you can't say "the real consumer could use this now" means the plan was wrong, not the work done — go back and revise the plan (`upward-ops-plan`), don't ship. Revising means fixing the plan against reality, never loosening the criteria to match what got built — that would be the same Goodharting one level up.

**Good**: "Build passes (0 errors), 3 new test cases added and green, read-back confirms the file is complete, and booting the production build serves real requests." ✅
**Bad**: "I've made the change, logically it should work now" — if you haven't run it, it's not done. Write "changes made, unverified, because X" instead. ❌
**Bad**: "Clean-room rebuild passed, all plan criteria green" — while the ingress is still hardcoded to `example.com`. Process rigor is not evidence the artifact works; nobody asked "would traffic actually reach the app?" ❌

## 2. How to verify the quality floor

The one who did the work doesn't verify their own output — verification always goes to a freshly spawned agent (general-purpose, never continued via `SendMessage` from the agent that did the work), because whoever did the work carries the author's point of view and will mentally fill in gaps the artifact never actually states.

**Rule** (by artifact type):
- **Code**: build passes, plus the path in question has been run for real once, or has a test. "Run for real" means from the consumer's seat: boot the built artifact the way it will actually be run — production build, real HTTP requests, deploy-script dry-run, a real input file — not only build and tests green. Anything touching core functionality: actually exercise it once. New logic with branches/loops/parsing: leave behind one minimal runnable check. Dispatch: run the tests or a real execution — "looks right" doesn't count.
- **Docs, or any file in general**: dispatch a fresh-context Haiku read-back: "Without any other context, can you follow this document? Does it exist, does it cover X/Y/Z, any broken sentences or gaps, which sentence has two possible readings?" Rewrite any sentence with two readings until it only has one.
- **Architectural judgment calls**: write down "the earliest observable signal if this judgment turns out wrong" — if you can't write that down, the judgment isn't verifiable, so downgrade it to an experiment (do a small spike first). For high-stakes calls, get a second opinion: dispatch another agent to answer the same question independently and compare for divergence, or have a judge pick the best of multiple answers.
- **General**: any "I think this is fine" needs to point to matching execution evidence. Can't point to it? It's unverified.
- **The open-ended hunt pass (required for any multi-item task)**: at least one review dispatch must be adversarial and unscripted — attach the original user request verbatim, declare the acceptance criteria suspect, and ask "what breaks in real use that the criteria don't cover?" A reviewer that only confirms the checklist inherits the checklist's blind spots: it verifies the work against the plan when what's needed is to verify the plan against reality. The commander dispatches this pass once all task items are checked off, to a fresh general-purpose agent, using the "Reality check (consumer-seat smoke)" review type in `upward-ops-dispatch`. If the plan already carries a consumer-seat reality check as its final task (per `upward-ops-plan`), that task discharges the run-the-artifact half of this pass — what the hunt pass adds on top is re-attacking the criteria against the original request.

## 3. Obligations once review findings come back

1. Judge each finding individually — accept or reject. Reviewers produce false positives; accepting everything blindly is just as negligent as ignoring everything. Attach one reason when rejecting.
2. Accepted findings get **applied back to the actual output** — relaying them to the user isn't the same as handling them.
3. After fixing, do a lightweight verification (grep/`wc`-level checks are fine to do yourself — mechanical confirmation doesn't count as bulk reading, no need to dispatch another round for it).
4. Report back to the user with numbers: how many findings, how many high/low severity, what got fixed, what got rejected — "review passed" carries zero information.

## 4. If you're stuck

A review turning up findings you can't resolve yourself isn't this skill's problem to solve — it's `upward-ops-judge`'s: stuck on whether to escalate the model, hitting a signal the whole approach is wrong, needing to stop and ask the user, or facing a taste/ambiguous call a weaker model can't make alone all route there.
