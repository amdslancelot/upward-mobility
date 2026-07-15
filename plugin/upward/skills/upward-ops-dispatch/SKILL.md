---
name: upward-ops-dispatch
description: How to dispatch read-only subagents: the two dispatchable kinds, the delegation brief, review dispatch, and prompt templates. Load before any dispatch.
---
# Model Dispatch Rules

> Reader: the main-thread model, any tier. Goal: when a task does leave the main thread, hand it off so the result comes back checkable, at the cheapest tier that can actually do it.

## Verified resources (verified 2026-07-07 against official docs — stale? re-verify via a template #2 research dispatch and re-stamp before use)

- Model aliases: haiku / sonnet / opus / fable. Capability/cost ordering: haiku < sonnet < opus < fable. Which concrete version an alias resolves to varies by harness — check the `/model` picker, don't trust a written-down model ID.
- The Agent tool's `model` parameter accepts the aliases above (confirmed in the sub-agents official docs).
- Agent types available may vary by environment (some ship specialized investigator/reviewer agents with compressed output that saves main-thread context). Check what's actually installed before naming one; fall back to Explore / general-purpose otherwise.

## Dispatch is read-only

The main context does the work; subagents read, run, and report — they never modify project files. Implementation, refactors, and fixes stay in the main context, serially, where the whole contract lives in one head. This line is structural rather than a judgment call because every judgment-shaped exception measured so far was taken and cost more than it saved: per-item builder dispatch paid more in cold-starts (each subagent re-reads the plan, the contract, the tree from zero) than the redundancy it removed, and a "genuinely parallel workstreams" exception got a three-layer build split across three builders that drifted at their shared contract seams — the run's fatal defects sat exactly at the boundaries between them — while costing the most tokens of any run measured. Only two things are worth dispatching:

1. **Fresh-context checks** — the end-of-run consumer-seat review, a read-back, a second opinion. Independence is the product, and it cannot be produced inside the context that did the work. These agents may execute the artifact and its gates (booting it, dry-running a deploy, feeding it real input is their whole job); what they never do is edit it.
2. **Bulk read-and-report** — long log trawls, wide repo scans, research fetches, ingesting material that would flood the main context; the subagent reads a lot and reports back a little. Bulk is measured in time carried as well as size — there is no size threshold, and the working set (plan.md, the files under edit) is exempt: material you consult briefly but would then hold for the rest of the run compounds into a flood even when no single piece feels large — 45K of early web research carried to the end of one measured run cost a third of that run's total tokens in re-reads. If you need the findings but not the source material, dispatch a reader and keep only its digest.

Everything else stays in the main thread. Dispatch in the foreground: every background dispatch wakes the main thread again with a paid notification round, and those wake-ups alone have been measured at a quarter of a run's raw token bill.

## Dispatch cheat sheet

Pick the tier with one question: is the answer already there to be found (Tier 1), is the goal fixed but the path to it not (Tier 2), or is the goal itself still undecided (Tier 3)?

| Tier | What belongs here | Examples | Agent type | Model | Why this model |
|---|---|---|---|---|---|
| **1 — Mechanical retrieval** | The answer already exists; the task is locating, extracting, or restating it, with no judgment call to make. | Find a definition or call site; read-back verification of a file (does it exist, does it cover X/Y/Z, any broken sentences); pulling specific fields out of text. | Explore for repo lookups; for verification, always a freshly spawned general-purpose. A lookup whose answer already sits in this context needs no dispatch — answer it inline (see cost intuition below) | haiku | One right answer either way, so the cheapest model gets there as reliably as any. |
| **2 — Bounded comprehension** | The goal is fixed and decidable, but reaching it takes comprehension or picking a path through the material. | Broad search when you're not sure where to look; a long log or doc trawl that ends in a short summary; research fetches; the consumer-seat reality check. | Explore for searches; general-purpose for everything else | sonnet | Sonnet reasons well enough to pick a path and follow it correctly, at a fraction of opus's cost. |
| **3 — Judgment-heavy** | The goal or shape of the work is itself the question. | Architectural trade-offs; ambiguous requirements. | Main thread makes the call directly, or a read-only Plan agent for a second opinion | opus | This is exactly where a cheaper model tanks quality. |

Two rules that cut across the tiers:

- Independent review — the end-of-run consumer-seat pass, a read-back, a second opinion — always goes to a freshly spawned agent, never anyone who touched the work (concrete recipes in `upward-ops-review skill`#2). Tier it by what is being checked: form is Tier 1 (haiku), meaning is Tier 2 (sonnet).
- When a check straddles form and meaning, round up to the higher tier rather than splitting hairs — a cheap model's false-negative "all PASS" costs more than the tier difference.

## The three required elements of a delegation brief (every dispatch needs all three, or don't dispatch)

1. **Goal and motivation**: what to do, and why. The subagent doesn't have your conversation's context — one sentence of motivation heads off half of the misunderstandings.
2. **Acceptance criteria**: a decidable definition of done ("test X passes," "report includes file:line") — not "do it well."
3. **Report format**: the subagent reports back only a conclusion and `file:line`. Long artifacts (>50 lines) get written to a file, and it reports the path back. Full source dumps and full logs are not allowed to come back in the report.

Good: "Repo at `/x`, a CLI for Y; I just added a `--json` flag to `list` in this context. Fresh-context check: run `list --json` against a real repo, confirm the output is valid JSON, then hunt for inputs the flag mishandles. Done when every finding has file:line + severity, or you state 'ran it on X/Y/Z, no findings.' Report ≤ 40 lines; do not modify any files."
Bad: "Check the `--json` flag." No motivation, no decidable done, no report format — the subagent guesses at all three and hands back something you can't check.

Templates are below in this skill.

## Escalation ladder

When and how far to escalate the model — including the haiku→sonnet→opus mechanics, the environment-check-first rule, and the two-round retry cap — lives in `upward-ops-judge skill`#1, right next to the criteria for *when* to escalate in the first place. The two questions are judged together, since you only care about the ladder once you've already decided to climb it.

## Verification isn't self-verification

The principle itself is one of this plugin's two always-on reflexes (see `core.md`). The concrete recipes — which agent to dispatch to check a file, code, or a high-stakes judgment call — live in `upward-ops-review skill`#2, right alongside the quality-floor rubric they support.

## Dispatching a review task

"Review" isn't one task. State the one focus explicitly in the prompt, because a reviewer only checks what it's pointed at. The common types are below; any other single focus (correctness of a diff, over-engineering, …) goes to a general-purpose agent with template #3 and that focus stated:

| Review type | What it's checking | Correct tool |
|---|---|---|
| Document consistency | Cross-file contradictions, placeholders, broken cross-references, ambiguous sentences a weaker model would misread | general-purpose agent + template #3 below |
| Mechanical read-back | Does the file exist? Is the content complete? Are sentences unbroken? | general-purpose agent, Haiku is enough |
| Reality check (consumer-seat smoke) | Does the artifact work when used the way its real consumer uses it — boot it, deploy it, feed it a real input, run any repeatable path twice | general-purpose agent that actually runs the artifact; a real run is required, "it builds" doesn't qualify — but it does not re-run install/build/test gates the worker already logged with execution evidence |

**Fresh-context isn't a formality, it's a test condition.** Reviews always spin up a new agent (never `SendMessage` to continue any prior agent), for two reasons:

1. **Verification isn't self-verification**: whoever did the work (or any agent that watched the work happen) carries the author's point of view, and will mentally fill in context the document never actually states — so it can't see the ambiguity.
2. **A cold start *is* the reader simulation**: the target reader for operating-rule files and docs is exactly "a weaker model with no prior context." Wherever a fresh-context agent gets confused, future sessions will get confused too. Its confusion is data, not noise.

Real example: one review caught "the README describes five templates, but there are actually six files" — the author had just added the sixth one, and from their point of view it was "obviously known," so self-review would never have caught that bug.

**Model selection: Haiku verifies form, Sonnet verifies meaning.**

- **Haiku**: when the checklist can be fully mechanized — file exists, line count, a grep returns 0 hits, all headings present.
- **Sonnet**: when a finding requires reasoning — "this sentence has two readings," "this number looks generic but is actually leftover project-specific cruft," "these two rules conflict in an edge case."
- **Opus**: only when the thing under review is itself a high-stakes judgment call (architectural decisions, security boundaries) that needs a second opinion.

The cost of picking wrong is asymmetric — Haiku on a semantic check returns a false-negative "all PASS" that guts the review, while Sonnet on a mechanical check merely costs a little more — so **when unsure, round up** (same rule as the cheat sheet above).

**The required structure of a review prompt** (start from template #3 below, then add this):

1. **State the reviewer's identity explicitly**: "You are a fresh-context reviewer; your ignorance is an asset" — anything confusing should get reported, not skipped past.
2. **List every check dimension explicitly**, each with an actionable starting move (e.g., "project-specific leftovers: grep for these terms: [list]") — if you don't list the dimensions, the agent only checks the kind it's naturally good at.
3. **Give a rule for telling "the rule itself" apart from "example context"** — without it, the agent will report a legitimate example as a bug, and false positives will drown out the real findings.
4. **Require it to state explicitly when a dimension has no findings**: "checked X/Y/Z, no findings" and "didn't check" are two different things.
5. **Require it to simulate actually following N of the rules** (specific to document review): reading isn't enough — the places where it gets stuck are the actionable bugs.
6. **Report format + total length cap + "don't modify any files"**: the reviewer only reports; whether to fix something is the commander's call.
7. **Attach the original user request verbatim, and declare the acceptance criteria suspect**: the reviewer's job includes checking the criteria against the request and against reality, not only the work against the criteria. Criteria authored inside the run inherit the author's misunderstandings — a reviewer given only the checklist will dutifully verify a wrong plan and come back all green.

Once the review runs and findings come back, judging and acting on them is `upward-ops-review skill`'s job, not this one's.

## Cost intuition (for the moments you're not sure whether dispatching is worth it)

Don't trust a stamped token figure — cold-start cost depends entirely on what's actually loaded in the *current* environment (standing plugin/hook injections at session start, the system prompt, any skill files a task pulls in), and that shifts as the environment changes. Estimate it yourself instead: check what showed up in the first API call of a session log, sum it, and treat that as your fixed-cost floor before dispatching.

- The deciding factor is whether one of the two dispatch cases applies (fresh context as the product, bulk read-and-report) — not the task's difficulty or length. Work does not get cheaper by moving to a subagent: the warm context already has the plan and the tree loaded, and the subagent pays to reload them. The answer is already sitting in the main thread's context and it's a one-line question → don't dispatch, just answer it.
- Reviewing a batch of documents typically costs noticeably more than a normal dispatch — a semantic pass needs more reasoning rounds than a mechanical read-back does. Always worth it for output meant to stick around long-term; for one-off intermediate artifacts, it's fine to skip.
- Write the delegation prompt with the full background it needs — don't make it re-discover things you already know.

# Delegation Prompt Templates

> Usage: when the main thread dispatches a subagent, copy the matching template and fill in the blanks. `[ ]` marks a required field. Missing any required field? Don't dispatch yet.
> For how to pick agent type and model, see the dispatch cheat sheet earlier in `upward-ops-dispatch skill`.

## Common structure (shared by every template)

```
Background: [one or two sentences: what this repo is, what I'm doing, why this subtask is needed]
Task: [the concrete thing to do]
Scope: [which files/directories are in scope; explicitly state what NOT to touch. Always exclude the .upward/ directory — it's generated tooling state (token-usage logs, hook caches), not project content]
Acceptance criteria: [decidable definition of done, itemized]
Report format: [conclusion + file:line; long artifacts get written to (path), report the path back; do not paste full source dumps/full logs]
```

## 1. Search (investigator/Explore, haiku/sonnet)

```
Background: the repo is at [path], it's [one-sentence description]. I need [motivation].
Task: find [target: definition/call sites/data flow/convention]. Start by searching these keywords: [term1, term2, ...].
Scope: [all of src/ | a specific directory]. Read-only, no edits. Ignore the .upward/ directory — generated token-usage logs, not project content.
Acceptance criteria: every finding comes with file:line; if nothing's found, list the patterns and directories searched (proof of a real search, not a missed one).
Report format: a file:line table, one sentence of explanation per row, total length ≤ 40 lines. Do not suggest fixes.
```

## 2. Research (general-purpose + WebSearch, sonnet)

```
Background: [the decision to be made] needs [what kind of facts] to back it up.
Task: verify the following questions: [question list].
Source requirements: primary sources only — official docs, official repos, real sample artifacts; every fact needs a source URL. A fact backed only by secondary sources (blogs, forums, third-party tool sites) or not found at all → mark UNVERIFIED; filling gaps from training memory is forbidden (especially for version numbers, API parameters, prices).
Acceptance criteria: every question has either "answer + source" or "UNVERIFIED + where it was checked."
Report format: a fact list, ≤ 2 lines + URL per item. Long quotes get saved to [scratch path], report the path back.
```

## 3. Review (reviewer/fresh-context, sonnet) — for type/model selection and prompt add-ons, see "Dispatching a review task" above. The end-of-run consumer-seat pass counts as ONE focus: its boot-and-exercise half and its criteria-attack half travel in the same single dispatch, never two.

```
Background: [what this diff/file is for]. Original request, verbatim: [paste the user's original request — the acceptance criteria below were authored inside this run and may themselves be wrong; checking them against the request and against reality is part of your job].
Task: review [diff scope / file list], looking only for [correctness bugs | ambiguous phrasing a weak model would misread | rules that contradict each other | over-engineering | what breaks in real use that the criteria don't cover] (pick one focus, review one kind per pass).
Acceptance criteria: one line per finding: location + problem + suggested fix + severity. Do not write up the parts that have no problems (no praise).
Report format: a findings list sorted by severity; 0 findings → explicitly state "checked X/Y/Z aspects, nothing found." Do not modify any files — you report; whether to fix is the commander's call.
Special focus: [risk points specific to this task]
```

## Main thread's obligations after dispatching

- When a report comes back, check it against the acceptance criteria item by item before accepting it. Checking means reading the report's execution evidence against the criteria — the end-of-run consumer-seat review (see `upward-ops-review`) remains the only independent pass over the finished work. If the report doesn't pass, handle it per `upward-ops-judge skill`#1 (when and how far to escalate).
- If line numbers/figures in the report look inconsistent, the main thread must read the file itself to verify before reporting to the user.
- When relaying a report's conclusions to the user, restate them in full sentences — don't paste the subagent's compressed output verbatim.
