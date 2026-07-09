# Delegation prompt templates

> Usage: when the main conversation dispatches a subagent, copy the matching template and fill in the blanks. `[ ]` marks a required field. Skip any required field and you don't dispatch.
> See the delegation reference table in `ops/model-dispatch.md` for how to pick agent type and model.

## Common structure (shared by every template)

```
Background: [one or two sentences: what this repo is, what I'm doing, why this subtask is needed]
Task: [the specific thing to do]
Scope: [which files/directories are in scope; explicitly say what NOT to touch]
Acceptance criteria: [judgable completion standards, itemized]
Report format: [conclusion + file:line; long output goes to a (path), return the path; don't paste raw source/full logs]
```

## 1. Search (investigator/Explore, haiku/sonnet)

```
Background: the repo is at [path], it's [one-sentence description]. I need [motivation].
Task: find [target: definitions/call sites/data flow/conventions]. Start by searching these keywords: [term1, term2, ...].
Scope: [all of src/ | a specific directory]. Read-only, no edits.
Acceptance criteria: every finding carries a file:line; if nothing's found, list the patterns and directories searched (proof you looked, not that you missed it).
Report format: a file:line table, one sentence per row, ≤ 40 lines total. Don't suggest fixes.
```

## 2. Implementation (general-purpose/builder, sonnet)

```
Background: [repo + feature context]. Relevant files: [file list + one-line purpose for each] (you — the subagent taking this on — read these fully before touching anything; the commander doesn't need to read them first).
Task: [the behavior to implement, including inputs/outputs/edge cases].
Scope: expected to touch [file list]. If you need to add a new file, explain why in your report. Do not touch [exclusion list].
Conventions: follow the naming and style of surrounding code; no new dependencies; no out-of-scope refactoring.
Acceptance criteria:
- [build command] passes (0 errors)
- [specific behavior verification: test X green / actually run path Y and confirm output Z]
- the diff contains only task-relevant changes
Report format: which files changed (file:line level), how you verified it and the result, any known limitations left behind. If it fails, report the failure reason and what you already tried — don't hand back unverified code that "should work in theory."
```

## 3. Refactoring (general-purpose, sonnet; use a Plan agent first if scope is large)

```
Background: [why refactor: duplication/coupling/prep for feature X].
Task: change [current shape] into [target shape]. Behavior must not change.
Scope: [file list]. Call sites total [N] (grep to confirm first; if the number doesn't match, stop and report).
Acceptance criteria:
- run [tests/build] once before refactoring to record a baseline; results after must match the baseline
- every call site on the old interface is migrated; grep for [old name] returns 0 hits
- no behavior changes (no drive-by bug fixes, no drive-by formatting changes)
Report format: a migration table (old → new), baseline comparison results, grep evidence.
```

## 4. Research (general-purpose + WebSearch, sonnet)

```
Background: [the decision to be made] needs [what kind of facts] to back it up.
Task: verify the following questions: [question list].
Source requirements: prefer official docs/official repos; every fact carries a source URL; if you can't find it, mark UNVERIFIED — never fill gaps from training memory (especially version numbers, API parameters, prices).
Acceptance criteria: every question has either "answer + source" or "UNVERIFIED + where you looked."
Report format: a fact list, ≤ 2 lines + URL per item. Long quotes go to [scratch path], return the path.
```

## 5. Review (reviewer/fresh-context, sonnet)

See `ops/review-dispatch.md` for type/model selection and prompt add-ons.

```
Background: [what this diff/file is for].
Task: review [diff scope / file list], looking only for [correctness bugs | ambiguous phrasing a weak model would misread | rules that contradict each other | over-engineering] (pick one focus, review one kind at a time).
Acceptance criteria: one line per finding: location + problem + suggested fix + severity. Don't write anything about the parts that are fine (no praise).
Report format: a finding list sorted by severity; if there are 0 findings, say explicitly "checked X/Y/Z dimensions, no findings."
Special focus: [risk points specific to this review]
```

## 6. Appending/pasting content into a file (builder, haiku)

The hardened version, with a hard-won lesson baked in: builders will copy the fence markers themselves into the file unless you tell them not to.

```
Task: append content to the end of [file path] (currently [N] lines).
The content to append = the text between the ```append fences below. The fence markers themselves are not content — they must never end up in the file.
Do not change a single character of, or otherwise touch, the existing content.

```append
[content]
```

Acceptance criteria (all must pass before you report success):
1. Grepping for the fence markers in the target file returns 0 hits.
2. The new content's starting line number > [N] (confirms it landed at the end).
3. The existing lines 1–[N] are byte-identical to before.
Report format: start and end line numbers of the appended content + PASS/FAIL for each of the three acceptance criteria.
```

Good: prompt says "the ```append fences are not content, do not copy them into the file" and lists grep-for-marker as acceptance criterion 1 → builder appends clean, grep returns 0 hits.
Bad: prompt just says "append the text below" with a fence around it → builder pastes the fence lines too, and nothing in the acceptance criteria would have caught it.

## The main conversation's obligations after dispatching

- When the report comes back, check it against acceptance criteria item by item first. Only adopt it once it passes; if it doesn't pass, follow the escalation ladder (`ops/model-dispatch.md`).
- If line numbers/figures in the report contradict each other, the main conversation must read the file itself to verify before reporting to the user.
- When relaying a report's conclusions to the user, restate them in full sentences — don't paste the subagent's compressed output verbatim.
