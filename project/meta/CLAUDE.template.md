# {{project name}} — CLAUDE.md (index)

{{One to three lines: what this project is, who it's for, the core tech stack. Example: "E-commerce
back office: product management + order lookup, used by internal ops staff. React + PostgreSQL."}}

**This file is just an index. Read only the file your task points to — don't scan the whole `src/` tree just to "understand the project."**

## Start of session (in order)

1. Read this index, find the file relevant to your task.
2. Index doesn't cover it → delegate to a cheap search-type subagent (don't grep it yourself ten times).
3. Delegation, escalation, verification rules → `{{system directory}}/ops/model-dispatch.md`.
4. Need a delegation prompt to copy → `{{system directory}}/ops/prompt-templates.md`.

## Three core rules (details in the ops files)

- **The commander doesn't descend.** Bulk reading, scanning, batch edits, and verification always get delegated to a subagent. The main thread only receives conclusions.
- **Verification isn't self-verification.** A completion claim needs execution evidence: build, test, actual run, or read-back. Verification goes to a freshly-spawned general-purpose agent, never the one that did the work.
- **The stuck-point rubric.** When to escalate the model, when something actually counts as done, when to ask the user, when to change approach → `{{system directory}}/ops/judgment-rubrics.md`.

## Codebase map (verified {{verification date}})

{{Delegate to a cheap subagent to scan the repo and generate this table. Format: | Area | Location | One-line description |.
List only "the stuff a task will need to find": routes, core logic, types, schema, config.
Keep it under 10 lines.

Important "what's absent" also belongs here (e.g. no test framework, no API routes) — it saves the weak
model from hunting for things that don't exist.}}

| Area | Location | Description |
|---|---|---|
| {{...}} | {{...}} | {{...}} |

## Design docs (read as needed)

{{Only list these if they exist. Format: - `path` — one line + when it's a must-read.}}

## Operating-discipline files (read as needed)

- `{{system directory}}/ops/harness-diagnosis.md` — this environment's traps and how to fix them.
- `{{system directory}}/ops/model-dispatch.md` — delegation reference table, the three required elements, escalation ladder, verification isn't self-verification.
- `{{system directory}}/ops/judgment-rubrics.md` — judgment checklists (each with a good and a bad example).
- `{{system directory}}/ops/prompt-templates.md` — six delegation templates (search / implement / refactor / research / review / follow-up).
- `{{system directory}}/meta/maintenance.md` — who can change what, lessons get written back to `{{system directory}}/meta/lessons.md` (create it as needed if it doesn't exist), when to trim.
- `{{system directory}}/meta/letter-to-future-sessions.md` — the handoff letter (if it doesn't exist, create it from the skeleton in `{{system directory}}/meta/letter-template.md`).

## Hard rules

- Anything written into a file (code/docs/commit) is always full, normal sentences; compressed phrasing is for conversation only.
- Commit with git before editing any operating-discipline file; new content goes in new files; this index stays ≤150 lines.
- Model names/parameters/prices always get verified before being written down; if you can't verify, mark UNVERIFIED — never make it up.
{{Project-specific hard rules — delete this line if there are none.}}
