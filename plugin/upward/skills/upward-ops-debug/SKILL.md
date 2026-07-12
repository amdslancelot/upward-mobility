---
name: upward-ops-debug
description: Signal-first debugging loop. Use this when something is broken, throwing, failing, or slow and the cause is unknown — build a pass/fail signal that goes red on this specific bug before touching any code, then iterate hypothesis → minimal change → re-run signal, under nested round budgets that guarantee the loop terminates. Includes the environment/dependency checklist with its evidence gate, and the debug delegation template. Use when debugging a bug, a failing test, an error, a performance regression, or a fix that should work but does not take effect.
---
# Signal-First Debugging Loop

> Reader: the main-thread model, any tier. This skill covers *finding the cause*. What to do after repeated failure (rollback, changing course, escalation) already lives in `upward-ops-judge` and `upward-ops-dispatch` — this file only points there, it does not restate those rules.

## Rule zero: no signal, no fixing

Before touching any code, build a runnable pass/fail check that goes red on *this specific bug* — a failing test at whatever seam reaches the bug, a script ending in an assert, a curl plus its expected output, a grep over a build log. Then run it once: **it must come up red.** A signal that is green on the buggy code doesn't capture the bug; rebuild it until it goes red.

This step is the skill — everything after it is mechanical, because the signal is the judge for every later step: each iteration, each bisect replay, the environment evidence gate, and final verification all consume it. Spend disproportionate effort here. Without a signal, "still failing" and "fixed" are both feelings, and every round budget below becomes undecidable.

**Good**: "checkout returns 500 on an empty cart" → a test that builds an empty cart, calls checkout, asserts 200. Runs red before any fix. ✅
**Bad**: "I'll fix it first and then check whether the page looks right." No red baseline — you can't tell whether your change fixed the bug, masked it, or did nothing. ❌

## The loop

One round = one hypothesis, one minimal change, one signal run.

1. Write the hypothesis in one line ("the 500 comes from X assuming a non-empty list") into the round log.
2. Make the smallest change that tests that hypothesis — one variable at a time.
3. Run the signal. Green → go to "Done" below. Red → log the round, form the next hypothesis.

Keep the round log in plan.md's checkpoint/revision-log format (`upward-ops-plan` has the template). The log is what makes "check whether an earlier step went wrong" possible later, and it's what you hand over when escalating.

## Nested round budgets (what makes the loop terminate)

- **Per hypothesis: 2 rounds.** Still red after two changes under the same hypothesis → the hypothesis is dead, abandon it. This is the core rules' "retry the same thing at most two rounds," inherited unchanged.
- **Whole loop: 5 rounds total**, counted across all hypotheses and direction changes — switching hypotheses does not reset the counter. Budget exhausted → stop, package the signal definition plus the full round log, and ask the user. This outer cap is what this skill adds: without it, per-phase counters reset on every transition and the loop can spiral.

## When stuck, branch by symptom (pointers, not restatements)

- Hypothesis dead twice in a row, or any wrong-direction signal → roll back to the last green checkpoint and split regression-vs-wrong-approach per `upward-ops-judge` #4. When bisecting, run the signal at every replay step — the step that turns it red is the culprit.
- The fix looks right but won't take, or the stack points at a layer you never touched → environment checklist in the next section.
- Two hypotheses dead, or the error originates in third-party code (a library, framework, or tool) → web search the exact error message verbatim in quotes, plus the library name and version. What you find is a **new hypothesis, not a fix**: it still enters the loop as hypothesis → minimal change → signal run, and it still counts against the budget — pasting a Stack Overflow fix without running the signal is how bugs get masked instead of fixed. Search before escalating the model: a known upstream issue costs one search to find, and no tier of the ladder can out-think a bug that lives in someone else's code.
- Escalating the model → ladder in `upward-ops-dispatch`. Always attach the signal definition and the round log; escalating without them is re-rolling the dice. Run the environment checklist and the web search first — a broken environment or a known upstream bug stumps every model tier equally, so escalating past them just wastes the ladder.

## When the fix won't take: widen to environment (don't just stare at the failing line)

**Symptom**: a fix that should work doesn't, or the error stack points at a file/layer you've never touched. A weaker model's default is to stare at the reported line and keep tweaking it, but the root cause can live in the environment, a dependency, or an earlier step — and this class of root cause cannot be fixed by escalating the model. Staring at it just burns your round budget on a fight you can't win.

**Checklist (work through in order when the symptom won't budge)**:
1. Versions: lockfile vs. what's actually installed; does the runtime/language version match your assumptions?
2. Stale artifacts: build cache, `node_modules`/`__pycache__`, old compiled output not cleaned up.
3. Config/env: environment variables and config files not matching your assumptions.
4. Clean reproduction: run the signal from a clean clone / fresh install. **Red from a clean clone = it's the code; green from a clean clone = it's your local state.** This is the signal doing the isolating — no signal, no clean verdict.
5. Which layer the error originates from: stack points at a file you've never touched → the root cause is upstream (an earlier step or a dependency — go back to the regression branch of `upward-ops-judge` #4).

**Evidence gate (to stop abuse)**: "blame the environment" is the easiest excuse there is — nine times out of ten it's actually your own bug. Before accepting an environment/dependency hypothesis, produce evidence first: a version number that doesn't match, or a signal result from a clean clone. Suspicion alone doesn't count; the default assumption stays "it's my change" until the environment hypothesis has evidence behind it. Environment-checklist rounds count against the whole-loop budget like any other hypothesis.

**Good**: `node -v` prints 18, but the lockfile pins a package that needs 20 → concrete mismatch, environment hypothesis earns its place. ✅
**Bad**: "the test is flaky, probably a caching thing" with nothing measured → that's a guess, not evidence; keep assuming it's your change. ❌

## Delegating the debug (template)

Debugging is almost always ≥3–4 rounds of tool calls, so per the `upward-ops-dispatch` cheat sheet it gets dispatched (general-purpose, sonnet) rather than run in the main thread:

```
Background: [repo + one-sentence bug report: doing X, expected Y, got Z].
Signal: [exact command to run] — red looks like [output], green looks like [output]. Run it first and confirm it's red before changing anything; if it's green, stop and report that instead.
Task: find the cause and fix it. One hypothesis at a time: hypothesis → minimal change → re-run signal. Log every round (hypothesis, change, result). After two dead hypotheses, or if the error comes from third-party code, web search the exact error message before forming the next hypothesis — treat anything you find as a hypothesis to verify against the signal, not a fix to paste.
Scope: [files/dirs in scope]; do not touch [exclusion list].
Budget: [N] rounds total; a hypothesis still red after 2 rounds gets abandoned, not retried. Budget exhausted → report the round log and stop; do not keep grinding.
Acceptance criteria: signal green, existing tests pass, diff contains only cause-relevant changes.
Report format: root cause in one sentence + file:line, summary of the fix, the round log, signal and test output. On failure, the round log and what was ruled out — not "should work in theory."
```

## Done = signal green and nothing else broke

1. Signal green **and** the existing test suite passes (a fix that breaks something else is a new bug, not a fix).
2. Verification goes to a freshly spawned agent per the core rules (`upward-ops-review` for the dispatch details). It re-runs the signal and the tests — two commands of hard evidence, no need to understand the fix.
3. The signal graduates: commit it as a permanent test, so this bug can never come back silently.
