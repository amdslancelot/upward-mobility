---
name: ops-dispatch
description: Delegation rules and prompt templates. Use this before handing work off to a subagent — covers how to pick agent type and model, the three required elements of a delegation brief, the haiku→sonnet→opus escalation ladder, the verification-isn't-self-verification rule, and six copy-paste prompt templates for search/implementation/refactor/research/review/file-append tasks. Use before delegating any task to a subagent.
---
# Model Dispatch Rules

> Reader: the main-thread model, any tier. Goal: keep the cheap model running the day-to-day, and spend the pricier model's tokens only on judgment calls.
> The "verified resources" section below must be re-verified and re-stamped with today's date before you rely on it — don't just trust the template's values.

## Verified resources (verified 2026-07-07 against official docs — stale? re-verify before use)

- Switch the main thread's model with `/model <alias>`. Aliases: haiku / sonnet / opus / fable. Capability/cost ordering: haiku < sonnet < opus < fable.
- Current model IDs (as of 2026-07-07, platform.claude.com models overview): claude-haiku-4-5-20251001, claude-opus-4-8, and claude-fable-5 are current. claude-sonnet-4-6 is listed as legacy; the official docs list claude-sonnet-5 as the current latest Sonnet. **Which version the `sonnet` alias actually resolves to in your harness hasn't been confirmed per-environment — check the `/model` picker yourself, don't trust this line.**
- The Agent tool's `model` parameter accepts the aliases above (confirmed in the sub-agents official docs).
- Effort: the Agent tool call itself has no effort parameter. You can only set `effort: low|medium|high|xhigh|max` in `.claude/agents/*.md` frontmatter. Note: Sonnet 4.6 / Opus 4.6 have no xhigh tier; Fable 5, Sonnet 5, and Opus 4.8/4.7 have the full five tiers (verified 2026-07-07 against the model-config official docs).
- Thinking controls: `alwaysThinkingEnabled` in settings.json, `MAX_THINKING_TOKENS` env var (Fable 5 can't turn thinking off).
- Agent types specific to this environment (confirmed present as of 2026-07-07): caveman:cavecrew-investigator / cavecrew-builder / cavecrew-reviewer (compressed output that saves main-thread context). Porting this to an environment without the caveman plugin installed? Substitute Explore / general-purpose.

## Hard rule: the commander doesn't descend

The main thread doesn't do: bulk file reading, repo scans, web lookups, batch edits, verification runs. All of that goes to a subagent — the main thread only receives the conclusion. The main thread's job is: break down the task, make the calls, synthesize conclusions, talk to the user.

## Dispatch cheat sheet

| Task | agent type | model | Why |
|---|---|---|---|
| Find a definition/call site/file location | caveman:cavecrew-investigator (fall back to Explore) | haiku | Pure retrieval |
| Broad search, not sure where to look | Explore | sonnet | Needs a bit of reasoning to pick a path |
| Mechanical edit in 1-2 files | caveman:cavecrew-builder (fall back to general-purpose) | sonnet | Scope is known, just execute |
| Cross-file implementation, new feature | general-purpose | sonnet | Needs comprehension + implementation |
| Diff review | /code-review skill or caveman:cavecrew-reviewer (fall back to general-purpose) | sonnet | One finding per line |
| Architectural trade-offs, breaking down ambiguous requirements | Main thread does it directly, or Plan agent | opus | The part where a cheaper model tanks quality |
| Verifying someone else's output | general-purpose (freshly spawned, never the agent that did the work) | haiku/sonnet | See "Verification isn't self-verification" |

## The three required elements of a delegation brief (every dispatch needs all three, or don't dispatch)

1. **Goal and motivation**: what to do, and why. The subagent doesn't have your conversation's context — one sentence of motivation heads off half of the misunderstandings.
2. **Acceptance criteria**: a decidable definition of done ("test X passes," "report includes file:line") — not "do it well."
3. **Report format**: the subagent reports back only a conclusion and `file:line`. Long artifacts (>50 lines) get written to a file, and it reports the path back. Full source dumps and full logs are not allowed to come back in the report.

Good: "Repo at `/x`, a CLI for Y. Add a `--json` flag to `list`. Done when `list --json` emits valid JSON and existing tests pass. Report changed files at file:line + how you verified."
Bad: "Add a `--json` flag to the list command." No motivation, no decidable done, no report format — the subagent guesses at all three and hands back something you can't check.

Templates are below in this skill. When delegating a "paste this content into a file" task: wrap the content boundary in a code fence and state explicitly that the fence itself isn't part of the content; add "grep for the boundary marker in the target file returns 0 hits" to the acceptance criteria. (Hard-won lesson: builders will paste the delimiter marker straight into the file.)

## Escalation ladder

- **Haiku fails once** → escalate to sonnet, re-dispatch the same task with the error output attached.
- **Sonnet fails twice on the same subtask** → escalate to opus with the full failure trace (both prompts and error outputs). Escalating without the trace is just re-rolling the dice.
- **Once opus solves the pattern** → write the solution up as explicit steps and hand it back down to sonnet/haiku for batch application.
- **Rule out environment/dependency root causes before escalating**: escalating the model doesn't fix a broken environment (version mismatch, stale build, missing dependencies) — that kind of root cause stumps opus just as much. For a stubborn error, run the checklist in `ops-diagnose skill`#5 first, then decide whether escalation is even warranted.
- **Retry the same thing at most two rounds** (escalation included). The third round isn't "keep trying" — it's changing course or asking the user (see `ops-judge skill` for the criteria).

## Verification isn't self-verification

The one who did the work doesn't verify their own output. Verification always goes to a freshly spawned subagent (general-purpose, never continued via SendMessage from the agent that did the work — called "fresh-context" below):

- **For files**: read-back — dispatch haiku to read the file and report "Does it exist? Does it cover X/Y/Z? Any broken sentences or gaps?"
- **For code**: run the tests or a real execution. "Looks right" doesn't count.
- **For high-stakes judgment calls**: get a second opinion — dispatch another agent to answer the same question independently and compare for divergence, or have a judge pick the best of multiple answers.

## Cost intuition (for the moments you're not sure whether dispatching is worth it)

- Dispatching has a fixed cost of roughly 20k subagent tokens (cold start: loading the system prompt, reading files to rebuild context, multiple execution rounds). The deciding factor is the task's **number of execution rounds**, not its difficulty: ≥3-4 rounds of tool calls, or it needs to ingest a lot of raw material → dispatch, it's worth it. The answer is already sitting in the main thread's context and it's a one-line question → don't dispatch, just answer it.
- Write the delegation prompt with the full background it needs — don't make it re-discover things you already know.
- Don't spin up a new agent for every small follow-up question in a row: continue the same agent with SendMessage (keeps context, saves the cold-start cost).

# Delegation Prompt Templates

> Usage: when the main thread dispatches a subagent, copy the matching template and fill in the blanks. `[ ]` marks a required field. Missing any required field? Don't dispatch yet.
> For how to pick agent type and model, see the dispatch cheat sheet earlier in `ops-dispatch skill`.

## Common structure (shared by every template)

```
Background: [one or two sentences: what this repo is, what I'm doing, why this subtask is needed]
Task: [the concrete thing to do]
Scope: [which files/directories are in scope; explicitly state what NOT to touch]
Acceptance criteria: [decidable definition of done, itemized]
Report format: [conclusion + file:line; long artifacts get written to (path), report the path back; do not paste full source dumps/full logs]
```

## 1. Search (investigator/Explore, haiku/sonnet)

```
Background: the repo is at [path], it's [one-sentence description]. I need [motivation].
Task: find [target: definition/call sites/data flow/convention]. Start by searching these keywords: [term1, term2, ...].
Scope: [all of src/ | a specific directory]. Read-only, no edits.
Acceptance criteria: every finding comes with file:line; if nothing's found, list the patterns and directories searched (proof of a real search, not a missed one).
Report format: a file:line table, one sentence of explanation per row, total length ≤ 40 lines. Do not suggest fixes.
```

## 2. Implementation (general-purpose/builder, sonnet)

```
Background: [repo + feature context]. Relevant files: [file list + one-sentence function for each] (you — the subagent taking this task — read these fully before touching anything; the commander doesn't need to read them first).
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

## 5. Review (reviewer/fresh-context, sonnet) — for type/model selection and prompt add-ons, see `ops-review skill`

```
Background: [what this diff/file is for].
Task: review [diff scope / file list], looking only for [correctness bugs | ambiguous phrasing a weak model would misread | rules that contradict each other | over-engineering] (pick one focus, review one kind per pass).
Acceptance criteria: one line per finding: location + problem + suggested fix + severity. Do not write up the parts that have no problems (no praise).
Report format: a findings list sorted by severity; 0 findings → explicitly state "checked X/Y/Z aspects, nothing found."
Special focus: [risk points specific to this task]
```

## 6. Appending/pasting content into a file (builder, haiku) — the hard-won-lesson corrected version

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

- When a report comes back, check it against the acceptance criteria item by item before accepting it. If it doesn't pass, handle it per the escalation ladder (`ops-dispatch skill`).
- If line numbers/figures in the report look inconsistent, the main thread must read the file itself to verify before reporting to the user.
- When relaying a report's conclusions to the user, restate them in full sentences — don't paste the subagent's compressed output verbatim.
