---
name: upward-ops-judge
description: Externalized judgment: escalate the model vs roll back and change course, when to stop and ask the user, and taste calls. Use when stuck or unsure.
---
# Judgment, externalized: rubric and checklist

> Audience: the smaller model. Every rule ships with one good example and one bad example (the examples are generic — swapping in a real instance from your own project works better).
> Rules are specific enough to just follow; following them beats improvising.

## 1. When to escalate the model, and when to roll back instead

Both branches of this section start the same way: a signal fired telling you that retrying-as-is won't work. The question is *which* signal, because it decides whether you escalate to a stronger model or change course on the same one. Escalate when the model is the bottleneck; roll back and re-approach when the *direction* is the bottleneck. When a wrong-direction signal also warrants a stronger model, escalate with the failure traces attached — but roll back first regardless, because you never want to hand off or retry on top of broken state.

**Before you do either, check the prompt.** Half of "the model's too weak" is actually "the prompt was too vague." Before escalating, confirm the delegation brief wasn't missing one of its three required elements — difficulty *feeling* hard isn't the rubric, failure evidence is.

**Escalate the model** if any of these hold:
- The same subtask has already failed (once for Haiku / twice for Sonnet), and the failure wasn't caused by the prompt missing information.
- The task requires picking one option among several defensible ones, and picking wrong costs more than a full day's rework.
- The task involves deletion, data migration, or a public release, and you can't say how you'd roll it back if it goes wrong.

**How far to escalate** (this ladder applies to dispatched tasks, which are read-only — searches, read-backs, reviews, research; subagents never write project files, so a failure in implementation work is handled in the main context via the change-course/rollback branch below, not by re-dispatching it):
- **Haiku fails once** → escalate to sonnet, re-dispatch the same task with the error output attached.
- **Sonnet fails twice on the same subtask** → escalate to opus with the full failure trace (both prompts and error outputs). Escalating without the trace is just re-rolling the dice.
- **Once opus cracks the pattern** → write the answer down (in plan.md or the report) so cheaper checks can reuse it; any edits that follow from it are applied by the main context, never handed to a subagent.
- **Rule out environment/dependency root causes before escalating**: escalating the model doesn't fix a broken environment (version mismatch, stale build, missing dependencies) — that kind of root cause stumps opus just as much. For a stubborn error, run the environment checklist in `upward-debug skill` first, then decide whether escalation is even warranted.
- **Retry the same thing at most two rounds** (escalation included). The third round isn't "keep trying" — it's changing course or asking the user (section 2 below).

**Good**: a Sonnet consistency reviewer twice returns findings that don't hold up against the file — bundle both reports and escalate the review to Opus. ✅
**Bad**: escalating just because "this task feels hard," with no failure evidence behind it. ❌

**Change course instead of retrying** when any of these signals fire — the direction is wrong, not the model:
- Every fix spawns a new error, three times in a row (that's whack-a-mole — you're fixing the wrong layer).
- The fix touches more than double the number of files you estimated (you misjudged the scope — go back and re-read it).
- You've started fighting the tool or framework (monkey-patching a library, working around the type system, hacking the lifecycle) instead of using it as designed.
- The exact same error message shows up a second time (your last fix didn't take — first confirm the file you edited is actually on the execution path; if it's still stuck, run the environment checklist in `upward-debug skill` for environment/dependency/stale-artifact causes).

**Good**: you start high-frequency polling as a hack to work around some API's limitation → that's fighting the tool, and the real fix is a different architecture. ✅
**Bad**: abandoning the whole approach after a single test failure — one failure is information, not a signal. ❌

**Roll back before re-approaching, then split your next step by symptom.** The moment one of the wrong-direction signals fires, revert to the last known-good checkpoint first (a git commit; if the project doesn't use git, run `git init` first). Don't stack another fix on broken state — that only grows the blast radius. This has a precondition: **save a checkpoint every time a milestone clears its acceptance criteria.** No checkpoint, no rollback. A handwritten "what I changed" prose log doesn't count — it drifts, and it'll happily lie that something's "already reverted." Rolling back needs git-grade state that can't lie to you, not a narrative.

After rolling back, two paths diverge by what the signal looked like:
- **Looks like a regression** (whack-a-mole three times running, the exact same error recurring, something that used to work and doesn't anymore): there's a single culprit. Replay one change at a time, find the step that broke it, then fix it. Bisecting works here.
- **Looks like the wrong approach** (fighting the tool/framework, files touched more than double your estimate): there's no single culprit — the whole approach is the problem. **Don't bisect** — replaying one change at a time just reconfirms the direction is wrong and burns rounds. Re-plan directly, or escalate with the failure traces attached.

**Good**: three rounds of whack-a-mole in a row → roll back to the last green checkpoint and cherry-pick changes one at a time; the second change reintroduces the error → culprit found. ✅
**Bad**: you notice the file count has exploded (wrong direction) but force through "replay one change at a time" anyway → there's no single culprit to find, and you only admit you need to re-plan after burning several rounds for nothing. ❌

## 2. When to stop and ask the user

**Rule**: only stop for these three cases:
- The action is irreversible and wasn't explicitly requested by the task (deleting a branch, overwriting a file you didn't create, publishing to an external service).
- Two options are both defensible, but the right choice depends on a preference or business context only the user knows.
- You discover the task's premise itself is wrong (the user says "fix the bug in X," but X is actually working as designed).

Everything else: pick the sensible default → state in one line in your report what you picked → keep going.

**Good**: the file you're about to overwrite wasn't created by you and its contents don't match its description → stop, report it. ✅
**Bad**: "should test files go in `__tests__` or alongside the source?" — the repo already has a convention; check it yourself and follow precedent. ❌

## 3. Ambiguous calls and taste judgments (the honesty clause)

Decomposition, verification, and multi-sample review can shore up execution quality — but **the direction you decompose an ambiguous requirement into, product taste, and sensory quality (audio, visual, feel) are things a weaker model cannot make up for.** When you hit one of these, don't force it:
1. If you can measure it, measure it (turn a taste question into a numbers question with a measurement tool — building that kind of tool is a very high-priority investment).
2. If you can't measure it, escalate to Opus for two options with reasoning, and let the user pick.
3. If neither works, say plainly "this is outside what I can reliably judge," and attach the parts you *are* sure of.

**Good**: "does this animation feel smooth?" → don't guess, ask the user to look at A/B versions. ✅
**Bad**: making up a "feels-optimal" parameter value yourself. ❌
