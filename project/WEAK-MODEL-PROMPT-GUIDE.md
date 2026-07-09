# Plan → Execute → Review → Revise: a prompt pattern that gets a weak model through the whole quality loop

> Reader: you, the user (copy the skeleton when writing a prompt); secondary reader: the main-thread model (follow the phases when you receive this kind of prompt).
> Written: 2026-07-07, Fable 5 session.
> The model-self-driven version (the model runs the phases itself, no human prompting needed) is `ops/plan-lifecycle.md`. These are the same loop — edit one, check the other.
>
> The problem this solves: a Sonnet-tier commander defaults to "declare done the moment execution finishes." It won't spontaneously list out tasks, won't proactively delegate a review, and when it gets review findings back, it'll just relay them to you instead of going back and fixing its own output.
> This loop (a top-tier model's working instinct) has to be spelled out as an explicit obligation in the prompt. Only then can Sonnet actually run it.

## The skeleton (copy this directly, fill in the `[ ]` blanks)

```
Task: [goal and motivation].

Phase 1 (Plan): First list out the tasks, each with a decidable acceptance criterion, saved to plan.md for me to review.
Don't start work before I confirm.

Phase 2 (Execute): Work through each item, saving immediately after finishing and checking it off in plan.md before moving to the next.
Record a checkpoint (git commit) in plan.md whenever an item passes its acceptance criteria.
Delegate per ops/model-dispatch.md, copy briefs from ops/prompt-templates.md.
If an item fails twice after fixing, roll back to the last checkpoint first — don't stack a third fix on a broken state;
then decide, based on the symptom, whether to bisect (regression) or re-plan/escalate (wrong approach) — criteria in ops/judgment-rubrics.md#4.

Phase 3 (Review): Once every item is done, delegate to a freshly-spawned fresh-context agent to review all the output
(agent and model choice, prompt add-ons — see ops/review-dispatch.md).
Give it the review angles explicitly: [e.g., contradicting rules / wrong paths or names / ambiguous wording a weak model would misread / unverified claims].
Require it to: attach file:line + severity to every finding; explicitly state "checked, nothing found" for angles with no findings; not edit any files.

Phase 4 (Revise): Once findings come back, handle each one — if accepted, go back and fix the corresponding output; if rejected, write one line of reasoning why.
After fixing, update plan.md recording "which finding fixed which file."
Only done once 0 findings remain unhandled; at most two rounds of review-and-revise — if findings remain after round two, list them and ask me.

Definition of done: end of phase 4, not end of phase 2.
```

## What each design counters in a weak model

| Design | What it defends against |
|---|---|
| Plan frozen into a file (plan.md) | After mid-session drift, the file is the anchor the model uses to recover the task list; /compact won't lose it either |
| "Don't start work before I confirm" | Getting the first cut wrong — the biggest gap for a weak commander (`meta/AUDIT-2026-07-07.md`, failure mode 3) |
| Save immediately after each item | A session can be interrupted anytime; only what's saved counts — this also leaves readable output for phase 3's reviewer |
| Record a checkpoint at each milestone + roll back before re-approaching a failure | A weak model defaults to stacking fixes on a broken state, growing the blast radius; checkpoints let it return to known-good, then bisect or re-plan based on the symptom instead of manually un-doing things from memory (criteria in `ops/judgment-rubrics.md`#4) |
| Review angles listed explicitly | Without listed angles, the reviewer only runs the checks it's naturally good at, and reports a false-negative "looks fine" |
| Reviewer is fresh-context + forbidden from editing | Verification isn't self-verification; the reviewer only reports — whether to accept a finding is the commander's judgment call |
| **"Go back and fix the corresponding output" spelled out as an explicit obligation** | The core of this whole pattern — a weak model defaults to just relaying findings to you and stopping, rather than going back to fix the previous round's results itself |
| "Rejecting requires one line of reasoning" | Guards against two extremes: rubber-stamping everything (the reviewer has false positives) and ignoring everything |
| "Update plan.md recording what got fixed" | Leaves evidence of the revision, so a later session or a second review round can check it |
| "At most two rounds" | Prevents an infinite review↔revise loop burning through budget; same threshold as ops/model-dispatch.md's "retry the same thing at most twice" |
| Definition of done placed on the last line | A weak model weighs the most recently seen explicit definition of "done" most heavily; leave it out, and it calls it quits at the end of phase 2 |

## When to use this, when not to

- **Use it.** Tasks with multiple outputs (half a day of work or more), output meant to be relied on long-term (operating-discipline files, external-facing docs, core code), where the cost of an error outweighs the cost of one review round (one review round runs roughly 35-40k subagent tokens — see the cost section of `ops/review-dispatch.md`).
- **Don't use it.** A small single-file edit, a one-off draft, a question whose answer is already sitting in the conversation. The loop's fixed overhead eats any gain you'd get from it. Just do the work directly, with light verification.

## Worked example: doing this once, start to finish

Say the task is "write three onboarding docs for the project: a setup guide, an architecture tour, and a common-errors troubleshooting guide."

**Step 1 — you paste the filled-in skeleton**:

```
Task: write three onboarding docs (setup guide, architecture tour, common-errors troubleshooting),
for a new engineer's first day, so they can get a dev environment running without asking anyone.

Phase 1 (Plan): First list out the tasks, saved to plan.md for me to review, each doc with an acceptance criterion
(e.g., setup guide — following it should take someone from git clone to all tests passing, with a runnable command at every step).
Don't start work before I confirm.
Phase 2 (Execute): Write each doc in turn, saving and checking it off in plan.md as you finish each one.
Phase 3 (Review): Once all three are done, delegate to a fresh-context agent to review, angles:
whether the commands actually work (simulate following them) / contradictions between the three docs / undefined jargon for a newcomer.
Phase 4 (Revise): Handle each finding, go back and fix the corresponding doc, record what got fixed in plan.md.
Done only once 0 findings remain unhandled; at most two rounds, then ask me.
Definition of done: end of phase 4.
```

**Step 2 — the model replies with plan.md.** Check exactly three things:

1. Is the direction right? (Does its idea of "onboarding" match what you wanted?)
2. Are the acceptance criteria decidable? ("Write it clearly" doesn't count, "following it gets you to all-green tests" does.)
3. Are there any wrong assumptions?

Reply "go ahead" or point out corrections.

**Step 3 — during execution you don't need to watch it closely.** The model saves and checks off each doc as it finishes. If you notice it skipping a step (writing the next doc without saving the current one), drop the trigger phrase: "Follow plan.md item by item — save each one before moving on."

**Step 4 — the review report looks like this, and you only need to look at the disposition column:**

```
findings: 3 (1 high, 2 medium)
- [high] setup-guide:12 — "set environment variables" gives no list of variables → table added (accepted)
- [medium] architecture-tour:40 — the term "aggregator" is used before being defined → definition sentence added (accepted)
- [medium] troubleshooting:8 — suggested adding a Windows section → rejected: team is all-Mac (reasoning recorded in plan.md)
plan.md updated with the revision log.
```

**Step 5 — confirming the completion claim.** Check that plan.md has every item checked off and the revision log is complete. If you have doubts, spot-check one finding against the actual file location it references. Only then does it count as delivered.

Common failure points:
- At step 2, you reply "looks good" without actually reading the acceptance criteria. That throws away this whole pattern's biggest lever.
- At phase 4, the model just relays findings without fixing anything. Tell it: "Phase 4 is revision, not relaying — handle it per WEAK-MODEL-PROMPT-GUIDE.md."

## Shortened version (medium-sized tasks, skips the phase-1 back-and-forth)

```
Task: [goal and motivation]. Acceptance criteria: [itemized].
Once done, delegate to a fresh-context agent to review [list of angles], handle each finding by going back and fixing the output,
and only report back once fixes are done. Report should include: what changed, what the review found, how it was handled.
```

This skips confirming the plan up front (fine for a task with a clear direction), but keeps the "review → go back and fix" obligation — that part can't be cut.
