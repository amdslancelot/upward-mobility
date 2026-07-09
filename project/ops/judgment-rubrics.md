# Externalizing judgment: rubrics and checklists

> Reader: smaller models. Every rule ships with one good example and one bad example (the examples are generic — swap in a real instance from your own project and they work better).
> Rules are concrete enough to follow literally. Following them beats improvising.

## 1. When to escalate the model

**Rule**: escalate (path in `ops/model-dispatch.md`) if any of these hold:
- The same subtask has already failed (once on haiku / twice on sonnet), and the failure wasn't caused by a prompt missing information.
- The task requires "picking one option among several that all sound reasonable," and picking wrong costs more than a day of rework.
- The task involves deletion, data migration, or a public release, and you can't say how you'd undo it if it goes wrong.

**Good example**: sonnet fails to hit the acceptance bar twice (say, error needs to be <50ms, only gets to 200ms) — package up both failure trails and escalate to opus. ✅
**Bad example**: escalating because "this task feels hard" — difficulty as a feeling isn't the rubric, failure evidence is. ❌

**Check yourself before escalating**: check whether the delegation prompt was missing one of the three required elements. Half of "the model's too weak" is actually "the prompt was too vague."

## 2. When something actually counts as done

**Rule**: all three must pass before it counts as done:
1. Every acceptance criterion checked item by item (not "roughly matches").
2. Verification comes from an execution result (test output, an actual run, a read-back) — not "I read the code and it looked right."
3. The completion claim in the report carries no hedge words like "should," "probably," or "in theory."

**Good example**: "Build passes (0 errors), 3 new test cases green, read-back confirms the file is complete." ✅
**Bad example**: "I've finished the change, logically this should work now" — if you haven't run it, it's not done. Write "changes made, unverified, because X" instead. ❌

## 3. When to stop and ask the user

**Rule**: stop only in these three situations:
- The action is irreversible and wasn't explicitly authorized by the task (deleting a branch, overwriting a file you didn't create, publishing to an external service).
- Two options are both reasonable, but the right choice depends on a preference or business context only the user knows.
- You discover the task's premise is wrong (the user says "fix the bug in X," but X is actually working as designed).

Everything else: pick the sensible default → state in one sentence in your report what you picked → keep going.

**Good example**: the file you're about to overwrite wasn't one you created, and its contents don't match its description → stop, report. ✅
**Bad example**: "Should the test file go in `__tests__` or next to the source?" — the repo already has a convention; look at it and follow it. ❌

## 4. What signals mean the direction is wrong and you should change course, not keep retrying

**Rule**: any of these signals appears → stop retrying, write down your current assumptions, and either change course or escalate:
- Every fix produces a new error, three times in a row (whack-a-mole = you're fixing the wrong layer).
- The fix requires touching more than double the number of files you estimated (your understanding of scope was wrong — go reread it).
- You've started fighting the tool/framework (monkey-patching a library, working around the type system, hacking around a lifecycle) instead of using it.
- The exact same error message shows up a second time (your last fix didn't take — first confirm the file you edited is actually on the execution path; if it's still stubborn, check whether environment/dependencies/stale artifacts are the culprit, per `ops/harness-diagnosis.md`#5).

**Good example**: you start high-frequency polling to work around some API's rate limit → that's fighting the tool; the right fix is a different architecture. ✅
**Bad example**: giving up on the whole approach after a single test failure — one failure is information, not a signal. ❌

**When stuck, roll back first, then branch on the symptom.** When you hit one of the signals above, always restore to the last green checkpoint first (git commit; if the project isn't using git, `git init` first). Don't stack another fix on a broken state — that only lets the blast radius grow. Precondition: **you save a checkpoint every time a milestone clears acceptance.** No checkpoint, no rollback.

After rolling back, there are two paths forward:
- **Looks like a regression** (whack-a-mole three times in a row, the same error reappearing verbatim, something that used to work and now doesn't): there's a single culprit. Replay one change at a time, find the exact step that broke it, then fix it. Bisecting works here.
- **Looks like the wrong approach** (fighting the tool/framework, files to touch running at double your estimate): there's no single culprit — the whole approach is the disease. **Don't bisect** — replaying one change at a time will just reconfirm the direction is wrong and burn rounds for nothing. Re-plan directly, or escalate with the failure trail attached.

A hand-written "here's what I changed" prose log doesn't count as a checkpoint. It drifts, and it'll lie to you about having "already rolled back." Rolling back needs git-grade state that can't lie, not a narrative.

**Good example**: three rounds of whack-a-mole in a row → go back to the last green state and cherry-pick changes one at a time; the second change reproduces the error the moment it's applied → culprit located. ✅
**Bad example**: noticing the number of files to touch has exploded (wrong direction) but forcing through "replay one change at a time" anyway → there's no single culprit to find, and it takes several wasted rounds before anyone admits a re-plan is needed. ❌

## 5. How to verify the quality bar

**Rule** (by output type):
- **Code**: build passes + the path gets actually run once, or has a test. Anything touching core functionality: run it for real, once. New logic with branches/loops/parsing: leave behind one minimal runnable check.
- **Documents**: dispatch a fresh-context haiku read-back: "Without seeing any other context, can you follow this document as written? Which sentence has more than one reading?" Rewrite any sentence with two readings until it only has one.
- **Architectural judgment calls**: write down "the earliest observable signal that this judgment call was wrong" — if you can't write one, the judgment call isn't verifiable; downgrade it to an experiment (do a small spike first).
- **General**: any "I think this is fine" needs to point to matching execution evidence. Can't point to it = not verified.

## 6. Ambiguous questions and taste calls (the honesty clause)

Decomposition, verification, and multi-sample review can shore up execution quality. But **the direction of decomposing an ambiguous requirement, product taste, and sensory quality (audio, visuals, feel) are things a weak model cannot make up for.** When you hit one of these, don't force it:
1. If you can measure it, measure it (turn a taste question into a numbers question using a measurement tool — investing in these tools is a very high priority).
2. If you can't measure it, escalate to opus for two reasoned options and let the user choose.
3. If neither works, say plainly "this is beyond what I can reliably judge," and attach the parts you are confident about.

**Good example**: "Does this animation feel smooth?" → don't guess, have the user look at an A/B comparison of two versions. ✅
**Bad example**: making up a "best-feeling" parameter value on your own. ❌
