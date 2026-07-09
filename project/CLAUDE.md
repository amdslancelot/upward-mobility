# project — CLAUDE.md (index)

An agent operating-discipline pack. It externalizes senior-model (Fable 5) judgment into rules a cheaper model (Haiku/Sonnet/Opus) can follow for a long agent session without a human re-explaining anything. This directory is both a portable template (copy it into other projects) and a live project rooted in itself.

**This file is just an index. Read only the file your task points to — don't scan the whole directory just to "understand the project."**

## Start of session (in order)

1. Read this index, find the file relevant to your task.
2. First time using this pack → read `USAGE.md` first (workflow and prompt method).
3. Delegation, escalation, verification rules → `ops/model-dispatch.md`.
4. Need a delegation prompt to copy → `ops/prompt-templates.md`.

## Three core rules (details in each file)

- **The commander doesn't descend.** Bulk reading, scanning, batch edits, and verification always get delegated to a subagent. The main thread only receives conclusions.
- **Verification isn't self-verification.** A completion claim needs execution evidence: build, test, actual run, or read-back. Verification goes to a freshly-spawned general-purpose agent, never the one that did the work.
- **The stuck-point rubric.** When to escalate the model, when something actually counts as done, when to ask the user, when to change approach → `ops/judgment-rubrics.md`.

## File map (verified 2026-07-07)

| File | Contents | When to read it |
|---|---|---|
| `USAGE.md` | User's operating manual: workflow, how to write prompts, model budget allocation | When the user asks "how do I use this," or when planning a session |
| `WEAK-MODEL-PROMPT-GUIDE.md` | The plan→execute→review→revise loop's prompt skeleton, plus a worked teaching example (the user-driven, manually-prompted version; the model-self-driven version is `ops/plan-lifecycle.md` — edit one, check the other) | Delegating a large multi-output task, demanding a quality loop |
| `ops/model-dispatch.md` | Delegation reference table, the three required elements of a delegation brief, escalation ladder, verification isn't self-verification | Before every delegation |
| `ops/prompt-templates.md` | Six delegation templates (search / implement / refactor / research / review / follow-up) | Copy from it every time you delegate |
| `ops/judgment-rubrics.md` | Six judgment checklists, each with one good example and one bad example | When stuck, unsure if something's done, considering escalation |
| `ops/review-dispatch.md` | How to delegate a review: four review types, model choice, the six elements a review prompt needs, how to handle findings | Before delegating any review/verification |
| `ops/plan-lifecycle.md` | Large-task lifecycle (brief→plan→execute→review→revise), the model-self-driven version, plus a plan.md template (brief folded into the opening) | Starting a multi-output task or one that'll take half a day or more |
| `ops/harness-diagnosis.md` | This harness's token leaks and how to fix them | Session loses focus, context balloons |
| `meta/maintenance.md` | Who can change what, where lessons get written back to (`meta/lessons.md`), the threshold for trimming | Want to change an operating-discipline file, or just got burned |
| `meta/letter-template.md` | Handoff-letter skeleton | Write one following this skeleton at the end of any major session |
| `meta/letter-to-future-sessions.md` | The actual handoff letter (includes a list of lowest-confidence outputs) | Taking over someone else's work, want to know which numbers are unverified |
| `meta/AUDIT-2026-07-07.md` | Fable 5's audit of this pack: how far it substitutes for senior-model judgment, and remaining gaps | Want to know this pack's limits, planning improvements |
| `meta/CLAUDE.template.md` | Index skeleton (for porting to other projects — this project doesn't read it) | Only when porting |
| `README.md` | Contents list and porting steps for this pack | Only when porting |

An important "does NOT have": this project has no code, no tests, no build. Every output is markdown. Quality verification means fresh-context read-back and adversarial review (`ops/judgment-rubrics.md`#5).

## Hard rules

- Anything written into a file (docs/commit) is always full, normal sentences. Compressed phrasing is for conversation only.
- Commit with git before editing any operating-discipline file, so there's a rollback point (if the project isn't using git yet, `git init` first). New content goes in new files. This index stays ≤150 lines.
- Directory convention:
  - Root directory holds only the entry files the user copies directly (this file, USAGE, README, WEAK-MODEL-PROMPT-GUIDE).
  - Working rules go in `ops/`.
  - Governance and history go in `meta/`.
  - Every path referenced inside any file is written relative to the project root (e.g. `ops/model-dispatch.md`), never relative to itself with `../`.
- Model names/parameters/prices always get verified before being written down. Can't verify it? Mark it UNVERIFIED — never make it up.
- Ask the user before touching either of these: the rule bodies in `ops/judgment-rubrics.md`, or the `.claude/` settings. See the permission tiers in `meta/maintenance.md`.
