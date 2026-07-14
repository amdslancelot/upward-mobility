---
name: upward-ops-plan
description: Turning a large task into a frozen plan.md — brief (goal, acceptance criteria, assumptions, risks) plus a task list with decidable acceptance criteria per item — and then driving the execution workflow that follows it, whose numbered steps load `upward-ops-dispatch` (before the first dispatch), `upward-debug`/`upward-ops-judge` (when blocked), and `upward-ops-review` (after the last item) via the Skill tool as mandatory steps. Use this when starting a task with multiple deliverables, multiple steps, half a day or more of work, or output meant to stick around long-term; skip for single-file or one-off work.
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
- Assumptions: <things you're taking as true in order to proceed — if something breaks, check this first for a wrong assumption. Any assumption about an external format, API, protocol, or third-party behavior must be verified against a primary artifact (a real sample file, actual command output, or official documentation — blogs and community posts don't count) before the plan freezes; one you can't verify stays labeled unverified under Risks, and the code that depends on it must tolerate variance in it>
- Risks / out of scope: <known risks, explicitly excluded scope>

## Task list
- [ ] 1. <task name>
  - Model: <haiku/sonnet/opus> — Reason: <why this tier>
  - Target: <files/scope to touch>   Product: <what it emits: file, diff, report>
  - Dependency: <task #s that must finish first, or —>
  - Acceptance / Review: <decidable done-criterion; the builder runs it and reports execution evidence, the commander accepts by reading the report — no per-item verifier agent; the end-of-run hunt-pass reviewer is the only gate re-executor>
- [ ] 2. ...
- [ ] N. Consumer-seat reality check (always the last item; executed by the fresh-context hunt-pass reviewer — never by the main thread; see "Ground the criteria outside the run" below)
  - Acceptance: <phrased from the consumer's seat: "run deploy.sh and traffic reaches the app," "boot the production build and a real request round-trips" — never the builder's "build green" or "selfcheck passes against the fixture">

## Checkpoints (log one every time a milestone passes its acceptance criteria)
- <milestone> → <git commit: sha or one-sentence description>

## Revision log (fill in after review)
- <finding> → fixed at <file:line> | or rejected: <one-sentence reason>
```

## The two phases this skill owns

**Phase 0 — brief (before starting work)**: write the goal, acceptance criteria, assumptions, and risks into the top of plan.md. If the direction is uncertain (requirements are vague, or you're guessing at the user's preferences or business context) → stop and confirm before starting work; see `upward-ops-judge` skill#2 for the criteria. Don't skip this step: flawless execution in the wrong direction is the most expensive failure there is.

**Phase 1 — plan**: break the task into a list, attach decidable acceptance criteria to each item, freeze it into plan.md. When filling in each item's `Model:` and `Target:` fields, load `upward-ops-dispatch` via the Skill tool and use its tiered dispatch cheat sheet to pick the model and agent type — a task list that doesn't know what each item costs to execute isn't a real plan. If you drift mid-task or hit a `/compact`, this file is the anchor that gets you back to your task list.

## Ground the criteria outside the run

You are writing the exam you will later be graded on: any misunderstanding you hold now gets baked into the acceptance criteria, and every later review will verify the work against that misunderstanding instead of catching it. Three rules keep the criteria anchored to reality rather than to your own beliefs:

1. **External evidence rule**: every load-bearing assumption about an external format, API, protocol, or third-party behavior gets verified against a primary artifact — a real sample file, actual command output, or official documentation fetched now — before the plan freezes. Never from memory, and never from secondary sources: blogs, forum threads, and third-party tool sites can suggest what a format looks like, but they can never upgrade an assumption to "verified." An assumption resting only on secondary sources stays labeled unverified. Can't reach a primary artifact? The assumption goes under Risks as unverified, and rule 2 governs the code built on it.
2. **Unverified means tolerant**: code that depends on an assumption still unverified at plan freeze must tolerate variance in that detail — parse defensively, accept extra or missing fields, degrade with a clear warning that names the assumption — never hard-fail on an exact match of the unverified detail. A strict validator encoding an unverified belief turns "our guess was slightly off" into total failure on first real use; a wrong belief with a "verified" stamp fails harder than a wrong belief alone.
3. **Fixture provenance rule**: a test fixture you author from the same belief as the code can only confirm the belief, never test it. Any fixture that validates an external-format assumption must derive from a real external sample. No real sample obtainable in principle (the source is an arbitrary end user, not a nameable system)? Ask the user for a sample when a user is available; otherwise the fixture gets authored from the best evidence at hand, the assumption stays labeled unverified, and rule 2 still applies to the code. A self-authored fixture is a build gate — it never counts as consumer-seat evidence and never satisfies rule 4.
4. **Mandatory final task**: every plan ends with a consumer-seat reality check — run the finished artifact the way its real consumer would and watch it work. Its criterion is phrased from the consumer's seat ("run `deploy.sh` and traffic reaches the app," "upload a real export and rows appear"), never the builder's ("build green," "selfcheck passes against the fixture"). When the real consumer path is infeasible in the current environment (no credentials, no cloud account), step down this ladder and take the highest rung that runs: real deploy → boot the built artifact locally and exercise its real entrypoints (real HTTP requests against the production build from a fresh state, a rendered manifest, a real CLI invocation) → if nothing is runnable at all, report the check as NOT DONE rather than substituting a fixture selfcheck. This task is executed by the fresh-context hunt-pass reviewer in the execution workflow below, never by the plan's author.

**Good**: the plan assumes Takeout "Saved" exports are GeoJSON → before freezing, download a real Takeout export and look. (They're CSV — the plan just avoided shipping a parser for a format that never arrives.) ✅
**Bad**: write a GeoJSON parser, author a GeoJSON fixture from the same belief, set the criterion to "selfcheck passes against the fixture." Every box goes green; a real export imports nothing. ❌
**Bad**: "verified the CSV header via web search" against blogs and forum posts, then a parser that hard-throws on any other header. The sources were wrong, the "verified" label justified strictness, and a parser that would have mostly worked became one that rejects every real export. ❌

## Once plan.md is frozen: the execution workflow

Planning stops here. The rest of the run follows the loop below. The Skill-tool calls in it are mandatory steps of the workflow, not reading suggestions — a prose mention of a skill loads nothing; only calling the Skill tool puts its rules in front of you, and a run that skips these calls executes with the safeguards missing.

1. **Load `upward-ops-dispatch` via the Skill tool now, before dispatching item 1.** Every task item is executed by a dispatched subagent. The main thread does not build, edit, run tests, or bulk-read files itself — and that includes "just verifying": a main thread that re-runs its builders' gates was measured at more than half the token cost of an entire run, while adding no assurance the builders' reported evidence didn't already provide.
2. **For each item**: dispatch a builder carrying the item's acceptance criteria in its brief. The builder runs its own gates and reports execution evidence (the command and its real output). The commander judges the report against the criteria by reading it — not by re-running the gates — and either accepts the item or bounces it back with the failing criterion named.
3. **When an item fails twice, a fix won't take, or something breaks for an unknown reason** → load `upward-debug` via the Skill tool and follow its signal-first loop. **When stuck on direction, weighing a model escalation, or facing a call only the user can make** → load `upward-ops-judge` via the Skill tool.
4. **After the last item, load `upward-ops-review` via the Skill tool**, then dispatch exactly one fresh-context hunt-pass review per the review-dispatch section of `upward-ops-dispatch`. This single dispatch does two jobs at once: it executes the consumer-seat reality check (task N of the plan), and it attacks the acceptance criteria against the original request, which travels verbatim in its prompt. It is the only actor in the whole run that re-executes build and test gates the builders already ran (this constrains gate re-runs only — docs read-backs and architectural second opinions per `upward-ops-review` §2 are separate dispatches and remain allowed). The plan's author never performs this review — authoring the criteria counts as doing the work, and the author verifying against their own criteria is the Goodhart loop this workflow exists to break.
5. **When findings come back**: triage each one per `upward-ops-review`, dispatch accepted fixes back to builders rather than fixing inline, confirm each applied fix with a grep- or read-back-level mechanical check (the one narrow exception to step 1, per `upward-ops-review` §3 — confirming a line changed, never re-running build or test gates), check the item off, and commit the checkpoint.

Save progress in plan.md as you go — one line per checkpoint, and a revision log that records finding → fix, not narrative. If the session is interactive, tell the user `plan.md` is frozen and wait for a go before executing item 1; in an autonomous run with no user to ask, proceed directly into the workflow above.

## What each design choice guards against in a weaker model

| Design | Guards against |
|---|---|
| Pin the brief first + stop when direction is uncertain | Getting the first cut wrong — the biggest gap in a weaker commander |
| Assumptions written into their own field | A rollback point when things break: check whether an earlier assumption was wrong, instead of staring at the line that threw the error |
| Plan frozen into plan.md | An anchor against mid-task drift; survives `/compact` |
| Criteria grounded in primary artifacts before freezing | The plan inheriting the planner's own misunderstanding — criteria written from a wrong belief verify the belief, not the work |
| Unverified assumptions produce tolerant code | A wrong belief with a "verified" stamp shipping as a strict validator that hard-fails on every real input |
| Consumer-seat reality check as the mandatory last task, run by the hunt-pass reviewer | Goodharting: every checklist box green while the artifact fails on its first real use — and the plan's author grading their own exam |
| Skill loads written into the workflow as numbered steps | The execution-stage safeguards silently never entering the session — prose references load nothing |
| One hunt-pass reviewer as the only re-executor of gates | Token burn from the same build/test gates being run three times by three different actors |

## When to use this, and when not to

- **Use it**: tasks with multiple deliverables (half a day or more of work), output meant to stick around long-term (operating-rule files, external-facing docs, core code), or when the cost of a mistake exceeds the cost of one review round (see the cost-intuition section of `upward-ops-dispatch` skill for how to estimate that for your environment).
- **Don't use it**: a small single-file edit, a one-off draft, a question whose answer is already sitting in the conversation — the fixed cost of a brief and a plan eats the benefit; just do the work plus a lightweight check instead.
- **Scaled-down version (medium-sized, direction already clear)**: skip phase 0/1's back-and-forth entirely, but still dispatch a fresh-context review when the work is done (per `upward-ops-dispatch` skill) and work through every finding by fixing the source (per `upward-ops-review` skill) before reporting back.
