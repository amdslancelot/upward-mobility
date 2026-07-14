---
name: upward-ops-dispatch
description: Delegation rules and prompt templates — how to hand a task off once you've decided dispatching pays (fresh-context reviews, genuinely parallel workstreams, bulk ingestion), the sole "how to hand this off" authority for any task, including reviews. Covers the tiered dispatch cheat sheet (mechanical retrieval / bounded execution / judgment-heavy), the three required elements of a delegation brief, how to dispatch a review task specifically (which tool per review type, fresh-context rationale, model selection, required prompt structure), and six copy-paste prompt templates for search/implementation/refactor/research/review/file-append tasks. (When to escalate the model and the escalation ladder mechanics live in `upward-ops-judge`; judging a completed task's quality lives in `upward-ops-review`.) Use before delegating any task to a subagent.
---
# Model Dispatch Rules

> Reader: the main-thread model, any tier. Goal: when a task does leave the main thread, hand it off so the result comes back checkable, at the cheapest tier that can actually do it.

## Verified resources (verified 2026-07-07 against official docs — stale? re-verify and re-stamp before use)

- Model aliases: haiku / sonnet / opus / fable. Capability/cost ordering: haiku < sonnet < opus < fable. Which concrete version an alias resolves to varies by harness — check the `/model` picker, don't trust a written-down model ID.
- The Agent tool's `model` parameter accepts the aliases above (confirmed in the sub-agents official docs).
- Effort: the Agent tool call itself has no effort parameter; effort can only be set as `effort: low|medium|high|xhigh|max` in `.claude/agents/*.md` frontmatter.
- Agent types available may vary by environment (some ship specialized investigator/builder/reviewer agents with compressed output that saves main-thread context). Check what's actually installed before naming one; fall back to Explore / general-purpose otherwise.

## When dispatching pays (and when it doesn't)

The default executor is the warm main context: doing the work yourself in one continuous context measured both cheaper and higher-quality than fanning task items out to fresh subagents, because every dispatch re-pays a cold-start (the subagent re-reads the plan, the contract, the tree from zero) and a cheaper builder model ends up writing the code the run gets graded on. Dispatch when one of three things is true:

1. **A fresh context is the point** — the end-of-run consumer-seat review, a read-back, a second opinion. Independence is the product, and it cannot be produced inside the context that did the work.
2. **The workstreams are genuinely parallel and independent** — no shared files, no ordering between them; the wall-clock win pays for the cold-starts.
3. **The raw material would flood the main context** — bulk file ingestion, long log trawls, wide repo scans; the subagent reads a lot and reports back a little.

Everything else stays in the main thread. Prefer foreground dispatch: every background dispatch wakes the main thread again with a paid notification round, and those wake-ups alone have been measured at a quarter of a run's raw token bill.

## Dispatch cheat sheet

Pick the tier with one question: is the answer already there to be found (Tier 1), is the goal fixed but the path to it not (Tier 2), or is the goal itself still undecided (Tier 3)?

| Tier | What belongs here | Examples | Agent type | Model | Why this model |
|---|---|---|---|---|---|
| **1 — Mechanical retrieval** | The answer already exists — in the repo, in the text you hand it, or as a fixed set of categories; the task is locating, extracting, classifying, or restating it, with no judgment call to make. | Find a definition, call site, or file location; read-back verification of a file (does it exist, does it cover X/Y/Z, any broken sentences); quick factual Q&A answerable straight from given context; pulling specific fields out of text (error codes, dates, names); simple summarization of a file or report; high-volume classification/tagging against a fixed category set. | Explore for repo lookups; for verification, a freshly spawned general-purpose; otherwise often no dispatch needed at all — answer inline if it's already sitting in context (see cost intuition below) | haiku | One right answer either way — retrieval or classification against fixed rules — so the cheapest model gets there as reliably as any, and cheaply enough to run at volume. |
| **2 — Bounded execution** | The goal is fixed and decidable, but reaching it takes comprehension or picking a path. | Broad search when you're not sure where to look; mechanical edit in 1-2 files; cross-file implementation or new feature; diff review; verifying the meaning (not just the form) of someone else's output. | Explore for searches; general-purpose for everything else | sonnet | Sonnet reasons well enough to pick a path and execute it correctly, at a fraction of opus's cost. |
| **3 — Judgment-heavy** | The goal or shape of the work is itself the question; quality hinges on trade-offs and framing, not execution. | Architectural trade-offs; breaking down ambiguous requirements; choosing between competing designs. | Main thread makes the call directly, or Plan agent | opus | This is exactly where a cheaper model tanks quality, so opus tokens buy the most here. |

Two rules that cut across the tiers:

- Independent review — the end-of-run consumer-seat pass, a read-back, a second opinion — always goes to a freshly spawned agent, never anyone who touched the work (concrete recipes in `upward-ops-review skill`#2). Tier it by what is being checked: form is Tier 1 (haiku), meaning is Tier 2 (sonnet).
- When a task straddles two tiers, split it: send the judgment part up (Tier 3) and the execution part down (Tier 2), rather than sending the whole thing to the expensive model.

## The three required elements of a delegation brief (every dispatch needs all three, or don't dispatch)

1. **Goal and motivation**: what to do, and why. The subagent doesn't have your conversation's context — one sentence of motivation heads off half of the misunderstandings.
2. **Acceptance criteria**: a decidable definition of done ("test X passes," "report includes file:line") — not "do it well."
3. **Report format**: the subagent reports back only a conclusion and `file:line`. Long artifacts (>50 lines) get written to a file, and it reports the path back. Full source dumps and full logs are not allowed to come back in the report.

Good: "Repo at `/x`, a CLI for Y. Add a `--json` flag to `list`. Done when `list --json` emits valid JSON and existing tests pass. Report changed files at file:line + how you verified."
Bad: "Add a `--json` flag to the list command." No motivation, no decidable done, no report format — the subagent guesses at all three and hands back something you can't check.

Templates are below in this skill. When delegating a "paste this content into a file" task: wrap the content boundary in a code fence and state explicitly that the fence itself isn't part of the content; add "grep for the boundary marker in the target file returns 0 hits" to the acceptance criteria. (Hard-won lesson: builders will paste the delimiter marker straight into the file.)

## Escalation ladder

When and how far to escalate the model — including the haiku→sonnet→opus mechanics, the environment-check-first rule, and the two-round retry cap — lives in `upward-ops-judge skill`#1, right next to the criteria for *when* to escalate in the first place. The two questions are judged together, since you only care about the ladder once you've already decided to climb it.

## Verification isn't self-verification

The principle itself is one of this plugin's two always-on reflexes (see `core.md`). The concrete recipes — which agent to dispatch to check a file, code, or a high-stakes judgment call — live in `upward-ops-review skill`#2, right alongside the quality-floor rubric they support.

## Dispatching a review task

"Review" isn't one task, it's five. Pick the wrong tool and the review looks done but doesn't actually cover the risk:

| Review type | What it's checking | Correct tool |
|---|---|---|
| Diff/PR correctness | Does this change have bugs | general-purpose agent given the git diff and a correctness-only focus |
| Over-engineering | Abstractions/dependencies that shouldn't exist | general-purpose agent with that focus explicitly stated in the prompt |
| Document consistency | Cross-file contradictions, placeholders, broken cross-references, ambiguous sentences a weaker model would misread | general-purpose agent + template #5 below |
| Mechanical read-back | Does the file exist? Is the content complete? Are sentences unbroken? | general-purpose agent, Haiku is enough |
| Reality check (consumer-seat smoke) | Does the artifact work when used the way its real consumer uses it — boot it, deploy it, feed it a real input, run any repeatable path twice | general-purpose agent that actually runs the artifact; a real run is required, "it builds" doesn't qualify — but it does not re-run install/build/test gates the worker already logged with execution evidence |

The rubric in one line: **use a diff tool to review a diff, use general-purpose with custom-defined checks to review content.** A specialized tool's field of view is hardcoded — any risk outside that view, it stays silent on. Silence isn't the same as "no problem."

**Fresh-context isn't a formality, it's a test condition.** Reviews always spin up a new agent (never `SendMessage` to continue any prior agent), for two reasons:

1. **Verification isn't self-verification**: whoever did the work (or any agent that watched the work happen) carries the author's point of view, and will mentally fill in context the document never actually states — so it can't see the ambiguity.
2. **A cold start *is* the reader simulation**: the target reader for operating-rule files and docs is exactly "a weaker model with no prior context." Wherever a fresh-context agent gets confused, future sessions will get confused too. Its confusion is data, not noise.

Real example: one review caught "the README describes five templates, but there are actually six files" — the author had just added the sixth one, and from their point of view it was "obviously known," so self-review would never have caught that bug.

**Model selection: Haiku verifies form, Sonnet verifies meaning.**

- **Haiku**: when the checklist can be fully mechanized — file exists, line count, a grep returns 0 hits, all headings present.
- **Sonnet**: when a finding requires reasoning — "this sentence has two readings," "this number looks generic but is actually leftover project-specific cruft," "these two rules conflict in an edge case."
- **Opus**: only when the thing under review is itself a high-stakes judgment call (architectural decisions, security boundaries) that needs a second opinion.

The cost of picking wrong is asymmetric: Sonnet reviewing mechanical items costs about 1.5x more — a minor loss. Haiku reviewing semantic items comes back with a false-negative "all PASS," which guts the entire point of the review. **When unsure, round up.**

Good: "do rules 3 and 7 contradict each other in an edge case?" → Sonnet; it needs reasoning.
Bad: sending "do rules 3 and 7 contradict?" to Haiku → it returns "all PASS," the contradiction ships, and the review bought you nothing.

**The required structure of a review prompt** (start from template #5 below, then add this):

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

- The deciding factor is whether one of the three dispatch cases applies (fresh context as the product, real parallelism, bulk ingestion) — not the task's difficulty or length. A task you would execute serially in this context anyway does not get cheaper by moving to a subagent: the warm context already has the plan and the tree loaded, and the subagent pays to reload them. The answer is already sitting in the main thread's context and it's a one-line question → don't dispatch, just answer it.
- Reviewing a batch of documents typically costs noticeably more than a normal dispatch — a semantic pass needs more reasoning rounds than a mechanical read-back does. Always worth it for output meant to stick around long-term; for one-off intermediate artifacts, it's fine to skip depending on context (see `upward-ops-plan skill`'s "when to use this" section for the rubric).
- Write the delegation prompt with the full background it needs — don't make it re-discover things you already know.
- Don't spin up a new agent for every small follow-up question in a row: continue the same agent with SendMessage (keeps context, saves the cold-start cost).

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

## 2. Implementation (general-purpose — or an installed builder agent type if one exists, sonnet)

```
Background: [repo + feature context]. Relevant files: [file list + one-sentence function for each] (you — the subagent taking this task — read these fully before touching anything).
Task: [the behavior to implement, including inputs/outputs/edge cases].
Scope: expected to touch [file list]. If a new file is needed, explain why in the report. Do not touch [exclusion list].
Conventions: follow the naming and style of the surrounding code; don't add new dependencies; don't do out-of-scope refactoring.
Acceptance criteria:
- [build command] passes (0 errors)
- [specific behavior verification: test X is green / real run of path Y outputs Z]
- the diff contains only task-relevant changes
Report format: which files changed (at file:line granularity), how verification was run and the result, any known limitations left behind. On failure, report the failure reason and what was already tried — do not hand back "should work in theory" unverified code.
```

## 3. Refactor (general-purpose, sonnet; dispatch a Plan agent first if scope is large)

```
Background: [why refactor: duplication/coupling/prep for feature X].
Task: turn [current shape] into [target shape]. Behavior must not change.
Scope: [file list]. Call sites total [N] locations (confirm with grep first — if the number doesn't match, stop and report back).
Acceptance criteria:
- run [test/build] once before refactoring to record a baseline; results after refactoring must match the baseline
- every call site of the old interface is migrated; grep for [old name] returns 0 hits
- no behavior changes (no drive-by bug fixes, no drive-by formatting changes)
Report format: a migration map (old → new), baseline comparison result, grep evidence.
```

## 4. Research (general-purpose + WebSearch, sonnet)

```
Background: [the decision to be made] needs [what kind of facts] to back it up.
Task: verify the following questions: [question list].
Source requirements: prefer official docs/official repos; every fact needs a source URL; can't find it → mark UNVERIFIED, filling gaps from training memory is forbidden (especially for version numbers, API parameters, prices).
Acceptance criteria: every question has either "answer + source" or "UNVERIFIED + where it was checked."
Report format: a fact list, ≤ 2 lines + URL per item. Long quotes get saved to [scratch path], report the path back.
```

## 5. Review (reviewer/fresh-context, sonnet) — for type/model selection and prompt add-ons, see "Dispatching a review task" above

```
Background: [what this diff/file is for]. Original request, verbatim: [paste the user's original request — the acceptance criteria below were authored inside this run and may themselves be wrong; checking them against the request and against reality is part of your job].
Task: review [diff scope / file list], looking only for [correctness bugs | ambiguous phrasing a weak model would misread | rules that contradict each other | over-engineering | what breaks in real use that the criteria don't cover] (pick one focus, review one kind per pass).
Acceptance criteria: one line per finding: location + problem + suggested fix + severity. Do not write up the parts that have no problems (no praise).
Report format: a findings list sorted by severity; 0 findings → explicitly state "checked X/Y/Z aspects, nothing found."
Special focus: [risk points specific to this task]
```

## 6. Appending/pasting content into a file (general-purpose — or an installed builder agent type if one exists, haiku)

```
Task: append content to the end of [file path] (currently [N] lines).
The content to append = the text between the ```append fences below. The fence markers themselves are not content — they must not end up in the file. Do not alter a single character, do not touch existing content.

```append
[content]
```

Acceptance criteria (all must pass before reporting success):
1. grep for the fence marker in the target file returns 0 hits.
2. the new content's starting line number > [N] (confirms it's actually at the end).
3. existing lines 1-[N] are byte-for-byte unchanged.
Report format: start and end line numbers of the appended content + PASS/FAIL for each of the three acceptance criteria.
```

## Main thread's obligations after dispatching

- When a report comes back, check it against the acceptance criteria item by item before accepting it. Checking means reading the report's execution evidence against the criteria — the end-of-run consumer-seat review (see `upward-ops-review`) remains the only independent pass over the finished work. If the report doesn't pass, handle it per `upward-ops-judge skill`#1 (when and how far to escalate).
- If line numbers/figures in the report look inconsistent, the main thread must read the file itself to verify before reporting to the user.
- When relaying a report's conclusions to the user, restate them in full sentences — don't paste the subagent's compressed output verbatim.
