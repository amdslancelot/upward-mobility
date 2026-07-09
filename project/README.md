# Ops Template Pack — an agent operating discipline weak models can actually follow

This is a reusable, cross-project operating-discipline template for Claude Code (or any similar agent harness). The original was built in a single top-tier-model (Fable 5) session. The goal: externalize senior-model judgment into rules a cheaper model can keep following for a long session.

This directory is also **a live project rooted in itself**:
- `CLAUDE.md` is this directory's actual index (loaded every session).
- `USAGE.md` is the user's operating manual.
- `meta/AUDIT-2026-07-07.md` is Fable 5's own audit of what this pack can and can't do.
- `meta/CLAUDE.template.md` only gets used when porting this pack to another project.

## What's in this pack

| File | Contents | What to do when you adopt it |
|---|---|---|
| `meta/CLAUDE.template.md` | Project index skeleton (≤150 lines, routing only) | Fill in the `{{...}}` placeholders, rename it to `CLAUDE.md` at the new project's root |
| `ops/harness-diagnosis.md` | Environment traps and their fixes (token leaks, the main thread descending, context compounding) | Section 0 has steps for "re-diagnose your own environment" — follow them, then rewrite the environment-specific sections |
| `ops/model-dispatch.md` | Delegation reference table, the three required elements of a delegation brief, escalation ladder, verification isn't self-verification | Re-verify the model names and parameters in the "available resources" section (each is date-stamped) |
| `ops/judgment-rubrics.md` | Six judgment checklists, each with one good example and one bad example | Usable as-is; better still, swap in real examples from your project |
| `ops/prompt-templates.md` | Six delegation templates: search / implement / refactor / research / review / follow-up | Usable as-is |
| `meta/maintenance.md` | Permission tiers, lesson-writing format, trimming threshold, health-check list | Fill in the placeholders |
| `meta/letter-template.md` | "Letter to future sessions" skeleton | Fill it out at the end of every major session |
| `USAGE.md` | User's operating manual: workflow, prompt method, budget allocation | Usable as-is; update the model-alias sections as verification dates roll forward |
| `meta/AUDIT-2026-07-07.md` | Audit of this pack's capabilities: how far it substitutes for senior judgment, weak-commander failure modes | Reference document; optional to carry over when porting |

## Adoption steps (do these in order on a new project)

1. Copy the whole folder (including the `ops/` and `meta/` subdirectories) into the new project — e.g. under `docs/agent-ops/`.
2. Search globally for the two markers `{{` and "this environment," and replace each with the new project's actual values:
   - `{{pack-directory}}` becomes wherever you put it (e.g. `docs/agent-ops` in the example above).
   - Sections marked "this environment" (memory directory paths, environment-specific agent types, always-on plugins) get replaced with values you've actually verified in the new environment.
3. Once `meta/CLAUDE.template.md` is filled in, move it to the project root and rename it `CLAUDE.md`. For the codebase-map section, delegate to a cheap subagent to scan the repo and generate it.
4. Re-diagnose your environment per section 0 of `ops/harness-diagnosis.md` (plugins, hooks, and budget plans may differ) and rewrite the environment-specific sections.
5. Re-verify the model list in `ops/model-dispatch.md` (check official docs or the harness environment itself — don't carry over stale values).
6. Delegate to a fresh-context subagent to read back every file. Have it check: do all the paths exist? are all placeholders filled? do any rules contradict each other?
7. Delete everything in this README from this section up, or delete the whole README — once adopted, you don't need it anymore.

## Design principles (read before changing this pack)

- **The reader is a weak model.** Rules need to be concrete and actionable, with criteria and examples attached. An abstract requirement is the same as no requirement.
- **Separate the index from the content.** CLAUDE.md is routing only (≤150 lines); long content lives in files read on demand. Files loaded every session should total ≤500 lines.
- **Verification isn't self-verification.** Whoever did the work doesn't verify their own output. A completion claim needs execution evidence.
- **Write as you go.** A session can get interrupted at any time — only what's saved to a file counts.
- **This pack exists to save judgment, not to be worshipped.** If a rule gets in the way three times in a row, bring the evidence to the user and ask whether to change it.
