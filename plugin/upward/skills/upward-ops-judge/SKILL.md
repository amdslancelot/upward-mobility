---
name: upward-ops-judge
description: Judgment externalized as a rubric. Check here when stuck or unsure — when to escalate the model, when a task actually counts as done, when to stop and ask the user, what signals mean the direction is wrong and you should change course instead of retrying (including "roll back before re-approaching"), how to verify a quality floor, and the honesty clause for ambiguous calls and taste judgments. Use when stuck, unsure whether a task is done, considering escalation, or deciding whether to change approach.
---
# Judgment, externalized: rubric and checklist

> Audience: the smaller model. Every rule ships with one good example and one bad example (the examples are generic — swapping in a real instance from your own project works better).
> Rules are specific enough to just follow; following them beats improvising.

## 1. When to escalate the model

**Rule**: escalate (see `upward-ops-dispatch skill` for the ladder) if any of these hold:
- The same subtask has already failed (once for Haiku / twice for Sonnet), and the failure wasn't caused by the prompt missing information.
- The task requires "picking one option among several defensible ones," and picking wrong costs more than a full day's rework.
- The task involves deletion, data migration, or a public release, and you can't say how you'd roll it back if it goes wrong.

**Good**: Sonnet fails to hit the acceptance criteria twice in a row (e.g., needs <50ms error, only gets to 200ms) — bundle both traces and escalate to Opus. ✅
**Bad**: escalating just because "this task feels hard" — difficulty *feeling* hard isn't the rubric, failure evidence is. ❌

**Check yourself before escalating**: before escalating, check whether the delegation prompt was missing one of the three required elements. Half of "the model's too weak" is actually "the prompt was too vague."

## 2. When a task actually counts as done

**Rule**: all three must pass:
1. Every acceptance criterion checked off individually (not "roughly matches").
2. Verification comes from execution results (test output, a real run, a read-back) — not "I read the code and it looks right."
3. The report contains no hedges like "should," "probably," "in theory" around the completion claim.

**Good**: "Build passes (0 errors), 3 new test cases added and green, read-back confirms the file is complete." ✅
**Bad**: "I've made the change, logically it should work now" — if you haven't run it, it's not done. Write "changes made, unverified, because X" instead. ❌

## 3. When to stop and ask the user

**Rule**: only stop for these three cases:
- The action is irreversible and wasn't explicitly requested by the task (deleting a branch, overwriting a file you didn't create, publishing to an external service).
- Two options are both defensible, but the right choice depends on a preference or business context only the user knows.
- You discover the task's premise itself is wrong (the user says "fix the bug in X," but X is actually working as designed).

Everything else: pick the sensible default → state in one line in your report what you picked → keep going.

**Good**: the file you're about to overwrite wasn't created by you and its contents don't match its description → stop, report it. ✅
**Bad**: "should test files go in `__tests__` or alongside the source?" — the repo already has a convention; check it yourself and follow precedent. ❌

## 4. What signals mean the direction is wrong, and you should change course instead of retrying

**Rule**: any of these signals → stop retrying, write down your current assumptions, then change course or escalate:
- Every fix spawns a new error, three times in a row (that's whack-a-mole — you're fixing the wrong layer).
- The fix touches more than double the number of files you estimated (you misjudged the scope — go back and re-read it).
- You've started fighting the tool or framework (monkey-patching a library, working around the type system, hacking the lifecycle) instead of using it as designed.
- The exact same error message shows up a second time (your last fix didn't take — first confirm the file you edited is actually on the execution path; if it's still stuck, run the environment checklist in `upward-ops-debug skill` for environment/dependency/stale-artifact causes).

**Good**: you start high-frequency polling as a hack to work around some API's limitation → that's fighting the tool, the real fix is a different architecture. ✅
**Bad**: abandoning the whole approach and changing course after a single test failure — one failure is information, not a signal. ❌

**Roll back before re-approaching, then split your next step by symptom.** The moment you hit one of the signals above, revert to the last known-good checkpoint first (a git commit; if the project doesn't use git, run `git init` first). Don't stack another fix on broken state — that only grows the blast radius. Precondition: **save a checkpoint every time a milestone clears its acceptance criteria.** No checkpoint, no rollback.

After rolling back, there are two paths forward:
- **Looks like a regression** (whack-a-mole three times running, the exact same error recurring, something that used to work and doesn't anymore): there's a single culprit. Replay one change at a time, find the step that broke it, then fix it. Bisecting works here.
- **Looks like the wrong approach** (fighting the tool/framework, files touched more than double your estimate): there's no single culprit — the whole approach is the problem. **Don't bisect** — replaying one change at a time just reconfirms the direction is wrong and burns rounds. Re-plan directly, or escalate with the failure traces attached.

A handwritten "what I changed" prose log doesn't count as a checkpoint. It drifts, and it'll happily lie that something's "already reverted." Rolling back needs git-grade state that can't lie to you, not a narrative.

**Good**: three rounds of whack-a-mole in a row → roll back to the last green checkpoint and cherry-pick changes one at a time; the second change reintroduces the error → culprit found. ✅
**Bad**: you notice the file count has exploded (wrong direction) but force through "replay one change at a time" anyway → there's no single culprit to find, and you only admit you need to re-plan after burning several rounds for nothing. ❌

## 5. How to verify the quality floor

**Rule** (by artifact type):
- **Code**: build passes, plus the path in question has been run for real once, or has a test. Anything touching core functionality: actually exercise it once. New logic with branches/loops/parsing: leave behind one minimal runnable check.
- **Docs**: dispatch a fresh-context Haiku read-back: "Without any other context, can you follow this document? Which sentence has two possible readings?" Rewrite any sentence with two readings until it only has one.
- **Architectural judgment calls**: write down "the earliest observable signal if this judgment turns out wrong" — if you can't write that down, the judgment isn't verifiable, so downgrade it to an experiment (do a small spike first).
- **General**: any "I think this is fine" needs to point to matching execution evidence. Can't point to it? It's unverified.

## 6. Ambiguous calls and taste judgments (the honesty clause)

Decomposition, verification, and multi-sample review can shore up execution quality — but **the direction you decompose an ambiguous requirement into, product taste, and sensory quality (audio, visual, feel) are things a weaker model cannot make up for.** When you hit one of these, don't force it:
1. If you can measure it, measure it (turn a taste question into a numbers question with a measurement tool — building that kind of tool is a very high-priority investment).
2. If you can't measure it, escalate to Opus for two options with reasoning, and let the user pick.
3. If neither works, say plainly "this is outside what I can reliably judge," and attach the parts you *are* sure of.

**Good**: "does this animation feel smooth?" → don't guess, ask the user to look at A/B versions. ✅
**Bad**: making up a "feels-optimal" parameter value yourself. ❌
