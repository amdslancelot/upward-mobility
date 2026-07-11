---
name: upward-ops-review
description: How to dispatch a review task. Use this when you're about to review or verify a batch of outputs — covers which of the four review types (diff correctness, over-engineering, document consistency, mechanical read-back) needs which tool, the model-selection rule (Haiku verifies form, Sonnet verifies meaning), the required structure of a review prompt, and your obligations once findings come back. Use when about to dispatch a code or document review or verification.
---
# How to dispatch a review task: types, models, prompt structure, findings triage

> Audience: the main-conversation model. This answers "when reviewing a batch of outputs, which agent, which model, what prompt, and what to do once findings come back."
> This complements `upward-ops-dispatch skill`: that file covers whether to dispatch at all; this one covers how to dispatch review-shaped tasks specifically. Consolidated from the 2026-07-06 Fable 5 session transcript.
> For the full plan → execute → review → revise task-loop skeleton, see the source repo's WEAK-MODEL-PROMPT-GUIDE.md.

## 1. Sort out the review type first — the tool follows the type

"Review" isn't one task, it's four. Pick the wrong tool and the review looks done but doesn't actually cover the risk:

| Review type | What it's checking | Correct tool (this environment, 2026-07-07; re-verify when you port this) |
|---|---|---|
| Diff/PR correctness | Does this change have bugs | `/code-review` skill or caveman:cavecrew-reviewer (consumes a git diff) |
| Over-engineering | Abstractions/dependencies that shouldn't exist | `/ponytail-review` skill (hunts complexity only; if not installed, use general-purpose with that focus) |
| Document consistency | Cross-file contradictions, placeholders, broken cross-references, ambiguous sentences a weaker model would misread | general-purpose agent + `upward-ops-dispatch skill` #5 template |
| Mechanical read-back | Does the file exist? Is the content complete? Are sentences unbroken? | general-purpose agent, Haiku is enough |

The rubric in one line: **use a diff tool to review a diff, use general-purpose with custom-defined checks to review content.** A specialized tool's field of view is hardcoded — any risk outside that view, it stays silent on. Silence isn't the same as "no problem."

## 2. fresh-context isn't a formality, it's a test condition

Reviews always spin up a new agent (never `SendMessage` to continue any prior agent), for two reasons:

1. **Verification isn't self-verification**: whoever did the work (or any agent that watched the work happen) carries the author's point of view, and will mentally fill in context the document never actually states — so it can't see the ambiguity.
2. **A cold start *is* the reader simulation**: the target reader for operating-rule files and docs is exactly "a weaker model with no prior context." Wherever a fresh-context agent gets confused, future sessions will get confused too. Its confusion is data, not noise.

Real example: one review caught "the README describes five templates, but there are actually six files" — the author had just added the sixth one, and from their point of view it was "obviously known," so self-review would never have caught that bug.

## 3. Model selection: Haiku verifies form, Sonnet verifies meaning

- **Haiku**: when the checklist can be fully mechanized — file exists, line count, a grep returns 0 hits, all headings present.
- **Sonnet**: when a finding requires reasoning — "this sentence has two readings," "this number looks generic but is actually leftover project-specific cruft," "these two rules conflict in an edge case."
- **Opus**: only when the thing under review is itself a high-stakes judgment call (architectural decisions, security boundaries) that needs a second opinion.

The cost of picking wrong is asymmetric: Sonnet reviewing mechanical items costs about 1.5x more — a minor loss. Haiku reviewing semantic items comes back with a false-negative "all PASS," which guts the entire point of the review. **When unsure, round up.**

Good: "do rules 3 and 7 contradict each other in an edge case?" → Sonnet; it needs reasoning.
Bad: sending "do rules 3 and 7 contradict?" to Haiku → it returns "all PASS," the contradiction ships, and the review bought you nothing.

## 4. The required structure of a review prompt (start from `upward-ops-dispatch skill` #5, then add this)

1. **State the reviewer's identity explicitly**: "You are a fresh-context reviewer; your ignorance is an asset" — anything confusing should get reported, not skipped past.
2. **List every check dimension explicitly**, each with an actionable starting move (e.g., "project-specific leftovers: grep for these terms: [list]") — if you don't list the dimensions, the agent only checks the kind it's naturally good at.
3. **Give a rule for telling "the rule itself" apart from "example context"** — without it, the agent will report a legitimate example as a bug, and false positives will drown out the real findings.
4. **Require it to state explicitly when a dimension has no findings**: "checked X/Y/Z, no findings" and "didn't check" are two different things.
5. **Require it to simulate actually following N of the rules** (specific to document review): reading isn't enough — the places where it gets stuck are the actionable bugs.
6. **Report format + total length cap + "don't modify any files"**: the reviewer only reports; whether to fix something is the commander's call.

## 5. Obligations once findings come back (same playbook as phase four of the source repo's WEAK-MODEL-PROMPT-GUIDE.md)

1. Judge each finding individually — accept or reject. Reviewers produce false positives; accepting everything blindly is just as negligent as ignoring everything. Attach one reason when rejecting.
2. Accepted findings get **applied back to the actual output** — relaying them to the user isn't the same as handling them.
3. After fixing, do a lightweight verification (grep/`wc`-level checks are fine to do yourself — mechanical confirmation doesn't count as bulk reading, no need to dispatch another round for it).
4. Report back to the user with numbers: how many findings, how many high/low severity, what got fixed, what got rejected — "review passed" carries zero information.

## 6. Cost reference (single measurement from 2026-07, re-weigh for your environment)

Semantic review runs about 35–40k subagent tokens; mechanical read-back runs about 25–27k. Reviewing a batch of documents costs roughly 1.5–2x a normal dispatch — always worth it for "output meant to stick around long-term"; for one-off intermediate artifacts, it's fine to skip depending on context (see the "when to use this" section of the source repo's WEAK-MODEL-PROMPT-GUIDE.md for the rubric).
