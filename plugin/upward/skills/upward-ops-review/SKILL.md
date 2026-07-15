---
name: upward-ops-review
description: The done-criteria rubric, the quality floor by artifact type, and findings triage. Use when judging whether finished work is actually done and good enough.
---
# How to review task quality after a task is done

> Audience: the main-conversation model. This answers "is this task actually finished, by what bar, and what do I do with the findings once I have them" — not "how do I dispatch the review" (that's `upward-ops-dispatch skill`, which owns every "how to hand this off" question including review-shaped ones).
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

Whoever does the work runs their own gates as they go — build, test, execute the path just changed, log the evidence. That self-run evidence is what each item's completion claim stands on, and running those gates in the warm working context is the cheap path. What it can never stand in for is the final verdict on the whole task: authoring the plan and its acceptance criteria counts as doing the work, and the criteria author's blind spots are exactly what a review exists to catch. So the one independent pass — the consumer-seat hunt pass below — always goes to a freshly spawned agent (general-purpose, never continued via `SendMessage` from anyone who touched the work), because whoever did the work carries the author's point of view and will mentally fill in gaps the artifact never actually states.

**Rule** (by artifact type):
- **Code**: build passes, plus the path in question has been run for real once, or has a test. "Run for real" means from the consumer's seat: boot the built artifact the way it will actually be run — production build, real HTTP requests, deploy-script dry-run, a real input file — not only build and tests green. Anything touching core functionality: actually exercise it once, yourself, as you finish the work — "looks right" doesn't count. This per-item run is the item's own gate; it never discharges the end-of-run consumer-seat hunt pass below, which stays with a fresh agent. New logic with branches/loops/parsing: leave behind one minimal runnable check.
- **Docs, or any file in general**: for anything meant to stick around, a fresh-context Haiku read-back is a cheap option worth taking ("without any other context, can you follow this document? which sentence has two possible readings?") — rewrite any sentence with two readings until it only has one.
- **Architectural judgment calls**: write down the earliest observable signal if the judgment turns out wrong — can't name one? The judgment isn't verifiable; downgrade it to a small spike first. High-stakes calls get an independent second opinion (Opus, per `upward-ops-dispatch`).
- **General**: any "I think this is fine" needs to point to matching execution evidence. Can't point to it? It's unverified.
- **The open-ended consumer-seat hunt pass (required for any multi-item task, never skippable)**: exactly one review dispatch, at the end of the run, adversarial and unscripted — attach the original user request verbatim, declare the acceptance criteria suspect, and ask "what breaks in real use that the criteria don't cover?" A reviewer that only confirms the checklist inherits the checklist's blind spots: it verifies the work against the plan when what's needed is to verify the plan against reality. The commander dispatches this pass once all task items are checked off, to a fresh general-purpose agent (foreground), using the "Reality check (consumer-seat smoke)" review type in `upward-ops-dispatch`. The plan's consumer-seat reality check (per `upward-ops-plan`) does not discharge this pass — it is executed *by* this pass, at the review-effort level the run's brief declares (the definitions live in `upward-ops-dispatch`; the default is LOW): at MED or HIGH the same fresh-context dispatch boots and exercises the artifact from the consumer's seat — including running any repeatable consumer path twice and requiring the second run to change nothing — while at LOW it performs the static Known-killers sweep with no execution and its verdict carries the STATIC-ONLY marker; at every level it *also* re-attacks the criteria against the original request. One dispatch, both halves, and no part of it is handed back to the plan's author. Its scope is the real entrypoints and the blind spots: it does not re-run install/build/test gates the worker already ran and logged with execution evidence — that logged evidence plus this one independent consumer-seat run is the complete verification budget; any extra pass over the same gates adds tokens, not assurance.

## 3. Obligations once review findings come back

1. Judge each finding individually — accept or reject. Reviewers produce false positives; accepting everything blindly is just as negligent as ignoring everything. Attach one reason when rejecting.
2. Accepted findings get **applied back to the actual output** — fix them yourself, at the source, in the working context; relaying them to the user isn't the same as handling them.
3. After fixing, re-run only the specific gate the finding names, plus a grep/`wc`-level read-back to confirm the edit landed. A fix of any size gets exactly that — never a second review dispatch and never a full gate sweep; the one hunt pass already spent the run's independent-review budget.
4. Report back to the user with numbers: how many findings, how many high/low severity, what got fixed, what got rejected — "review passed" carries zero information.

## 4. If you're stuck

A review turning up findings you can't resolve yourself isn't this skill's problem to solve — it's `upward-ops-judge`'s: stuck on whether to escalate the model, hitting a signal the whole approach is wrong, needing to stop and ask the user, or facing a taste/ambiguous call a weaker model can't make alone all route there.
