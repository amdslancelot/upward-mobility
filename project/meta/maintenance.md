# Maintenance Protocol

> Operating-discipline files rot. This document specifies who can change what, where lessons get written
> back to, and how long a file has to get before it needs trimming.

## Permission tiers

**A weak model can change these on its own (no need to ask the user)**:
- The CLAUDE.md index: adding a line pointing to a new file, fixing a broken path, updating a one-line description.
- The "Verified Available Resources" section of `ops/model-dispatch.md`: when a model/parameter is found to be stale, verify it first (official docs or an actual test in the harness environment), then update it and change the verification date.
- Status labels in design docs ("design under review" → "implemented").
- Appending a new lesson learned the hard way (format below).

**Must ask the user before touching these**:
- Deleting or rewriting an entire section of any operating-discipline file.
- Changing the rule bodies in `ops/judgment-rubrics.md` (the rubrics are the system's core — a weak model doesn't get to self-edit the rubric; this is the main gate against degradation).
- Changing `.claude/settings.json`, hooks, or plugin config.
- Any "I think this rule is wrong" situation — report it, don't route around it.

For example: finding a broken path in the CLAUDE.md index and fixing it yourself is fine (tier one).
Deciding the escalation ladder in `ops/judgment-rubrics.md` is "too strict" and loosening it yourself is
not — that's a rule-body change, ask first.

## Where lessons learned the hard way get written, and in what format

Trigger: any event where "it took two retries to fix" or "the approach was wrong and we changed course"
(rubric for this: `ops/judgment-rubrics.md`#4).

Write to `meta/lessons.md` (create it if it doesn't exist). Append, never edit existing entries, in this format:

```
## YYYY-MM-DD [one-line title]
- Symptom: [what you observed at the time]
- Wrong path: [what was tried, and why it didn't work]
- Fix: [how it actually got resolved]
- Rule extracted: [one actionable sentence to prevent recurrence; if it's worth keeping loaded at all times, also add a line to the CLAUDE.md index]
```

Cross-session user preferences / project context (things that can't be derived from the repo) go to the
memory directory instead (in this environment: `~/.claude/projects/-Users-lans-h-Documents-claude-main/memory/`),
one file per topic plus a one-line entry in the MEMORY.md index. Don't duplicate into memory anything the
repo already records as fact.

## Size caps and when to trim

- CLAUDE.md itself stays ≤ 150 lines — it's an index only. Over that, pull content out into a referenced file and leave one line in the index.
- The files CLAUDE.md directly references and expects to be loaded together stay ≤ 500 lines combined.
- `meta/lessons.md` past 30 entries → dispatch to Sonnet to merge and trim:
  - Fold repeated themes into a single rule.
  - A "this is stale" determination needs evidence: grep the filenames/symbols the entry mentions and confirm 0 hits in `src/` before deleting it.
  - Commit with git before trimming.
- Any `ops/` file over 200 lines → split it or trim it (again, commit with git first).

## Safety rules for editing files

- Commit with git before editing any existing operating-discipline file (leaves a rollback point; if the project isn't using git yet, `git init` first). New content should preferentially go into new files.
- Save after finishing each item before starting the next one. A session can be interrupted at any time, and only what's saved counts.
- After editing CLAUDE.md or any `ops/` file, dispatch a fresh-context Haiku to do a read-back verification (method in `ops/judgment-rubrics.md`#5).

## Quarterly health-check list (or whenever the user says "check the system")

1. Is the model roster in `ops/model-dispatch.md` still current? (Check the official docs.)
2. Do all the paths the CLAUDE.md index points to still exist? (One shell one-liner verifies every path.)
3. Does `meta/lessons.md` have any repeated lesson that should get promoted into the rubrics? (If so, ask the user whether to update the rubrics.)
4. Is the system actually being followed? Spot-check recent sessions: did delegation briefs carry the three required elements, was verification actually fresh-context. A rule that isn't being followed is either too cumbersome to use (report to the user, consider trimming it) or needs reinforcing (raise its visibility in the CLAUDE.md index).
