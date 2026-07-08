# Skills & Agents Effectiveness Review

**Date:** 2026-07-06
**Scope:** `~/.claude/skills`, `~/.agents/skills`, `~/.claude/plugins/cache` (caveman, ponytail, humanizer), plugin agents. Read-only review — nothing was modified.
**Context:** No project-level `.claude` or `.agents` folders exist in the working directory, and no custom agents exist in `~/.claude/agents`. Everything reviewed is user-global.

---

## Inventory

| Item | Type | Source | Size (entry file) | Loaded by Claude Code? |
|---|---|---|---|---|
| impeccable | skill | npx installer | 20 KB SKILL.md + 28 reference files + scripts | Yes |
| emil-design-eng | skill | emilkowalski/skills | 27 KB | Yes |
| animation-vocabulary | skill | emilkowalski/skills | 13 KB | Yes |
| review-animations | skill | emilkowalski/skills | 8 KB + STANDARDS.md | User-invoke only (`disable-model-invocation: true`) |
| find-skills | skill | vercel-labs/skills | 5.5 KB | Yes |
| stop-slop | skill | git clone | 2.6 KB + references | **No — broken install** |
| caveman (+6 sub-skills) | plugin | marketplace | 0.6–5 KB each | Yes, + SessionStart hook |
| ponytail (+5 sub-skills) | plugin | marketplace | 1.7–6.7 KB each | Yes, + SessionStart hook |
| humanizer | plugin | marketplace | 34 KB | Yes |
| cavecrew-builder / -investigator / -reviewer | agents | caveman plugin | ~50 lines each | Yes |

---

## Problems found

### 1. stop-slop is dead weight (broken install)
`~/.claude/skills/stop-slop/stop-slop/SKILL.md` — the SKILL.md is nested one directory too deep (a git clone landed inside the skill folder), so Claude Code never discovers it. It does not appear in the available-skills list. It also duplicates humanizer's purpose entirely (both remove AI writing tells). **Recommendation: delete it.** Humanizer covers the same ground with a far more thorough rule set.

### 2. impeccable is installed twice, and the copies have diverged
- `~/.claude/skills/impeccable/` (real directory — this is the one Claude Code loads)
- `~/.agents/skills/impeccable/` (the copy other agents like Cursor/Codex would use)

Every reference file differs between the two (mostly path rewrites, but they will drift on updates). If you only use Claude Code, the `.agents` copy is unnecessary maintenance surface. Keep whichever matches how you update it (`npx impeccable`), remove or ignore the other, but know that only the `.claude` one affects Claude Code.

### 3. Four overlapping "review" paths
`caveman-review`, `ponytail-review`, `cavecrew-reviewer` (agent), and the built-in `/code-review`. They compete for the same trigger phrases ("review this PR", "review the diff"), which makes which-one-fires nondeterministic. The built-in `/code-review` is the only one tuned for current Claude models and is the strongest for correctness. `ponytail-review` has a real niche (over-engineering only). `caveman-review` and `cavecrew-reviewer` add compression, not review quality — redundant if you already get terse output from caveman mode itself.

### 4. Four overlapping design skills
`impeccable`, `emil-design-eng`, `animation-vocabulary`, `review-animations` all occupy frontend/design space. This is less harmful than the review overlap because their descriptions are reasonably differentiated, but `emil-design-eng` and `impeccable` will collide on general "polish this UI" requests.

### 5. Two always-on modes stack their costs on every session
Caveman and ponytail both inject full mode instructions via SessionStart hooks (~6–7 KB combined) into every session, whether or not the task benefits. Both also emit a "statusline setup needed" nag each session because the statusline was never configured.

---

## Per-item effectiveness with Claude models

### impeccable — ★★★★☆ (keep, best-engineered skill installed)
This is how a skill should be built for Claude models: a rich trigger description, progressive disclosure (28 per-command reference files loaded only when needed), helper scripts instead of prose instructions, and register-aware guidance (brand vs product UI). The costs: its ~1.4 KB description sits in your context every session, and its mandatory 5-step setup (run context.mjs, read reference files, read project files) makes even small UI tweaks heavyweight. Worth it if you do frontend work regularly; pure overhead if you don't.

### emil-design-eng — ★★☆☆☆ (marginal)
27 KB of design philosophy prose. Two issues for Claude models specifically: (a) the description ("This skill encodes Emil Kowalski's philosophy…") contains no trigger phrases, so Claude will rarely auto-invoke it — you have to call it by name; (b) it's philosophy, not procedure — modern Claude models already internalize most of this ("use ease-out for enter animations", "don't animate everything"). Its scripted initial response is an advertisement for animations.dev. Overlaps impeccable, which turns the same taste into executable workflow. Keep only if you explicitly consult it; otherwise redundant with impeccable.

### animation-vocabulary — ★★★☆☆ (well-built, niche)
Well-scoped, excellent trigger-rich description (the best-written description of your installs), small. But it's a glossary of standard motion terms (stagger, rubber-banding, FLIP…) that Claude models already know. Its real value is output *format* consistency, not knowledge. Harmless to keep; low ceiling.

### review-animations — ★★★☆☆ (fine, know its limits)
Solid structure: non-negotiable standards, a STANDARDS.md loaded on demand, explicit approval criteria. `disable-model-invocation: true` means it never fires automatically — you must invoke it yourself, which you should know (it's easy to assume it reviews animations in the background; it doesn't). Overlaps impeccable's `animate` reference. Keep if you review motion PRs; otherwise skippable.

### find-skills — ★★★★☆ (keep)
Small, cheap, does one useful thing (skill discovery/install from the open ecosystem). No overlap, no downside.

### humanizer — ★★★★☆ (keep, delete stop-slop)
34 KB but only loaded when invoked, so the standing cost is one description line. Based on the Wikipedia "signs of AI writing" catalog — genuinely useful with Claude models because it targets exactly the patterns Claude produces (rule of three, em-dash overuse, negative parallelism). The winner of the two de-AI-writing skills.

### caveman plugin — ★★☆☆☆ (questionable value on current Claude models)
The premise — compress Claude's chat output ~75% — matters most on older, chattier models. Current Claude Code models are already instructed toward concise, outcome-first output, so the marginal saving is smaller than advertised, and it's *output* tokens (cheap) bought with *input* tokens (the mode prompt re-injected every session, every turn of every conversation, including ones about recipes). It also actively fights Claude Code's own communication guidance, which prioritizes readability over brevity — fragments like "Bug in auth middleware. Fix:" save you tokens but cost you comprehension on anything non-trivial. Sub-skill quality varies: `caveman-stats` (hook-computed, honest numbers) and `caveman-compress` (compressing CLAUDE.md files genuinely saves input tokens every session) are the two with real, measurable value. `caveman-commit`/`caveman-review` duplicate built-ins. If you keep one thing from this plugin, keep `caveman-compress`.

### cavecrew agents — ★★★☆☆ (investigator good, other two redundant)
- **cavecrew-investigator**: the best of the three. Read-only, runs on Haiku (cheap), returns a compact `file:line` table, and the compressed hand-back genuinely reduces what lands in your main context versus vanilla Explore. Sound design.
- **cavecrew-builder**: hard-capped at 1–2 file edits. On current models, edits this small are faster done inline by the main thread — spawning an agent costs a cold start to save nothing. Redundant.
- **cavecrew-reviewer**: fourth review path (see problem #3). Redundant with `/code-review`.

### ponytail plugin — ★★★☆☆ (philosophically right, partially redundant)
YAGNI-enforcement aligns with how you'd want any model to code, and the ladder (does it need to exist → reuse → stdlib → native → one line) is a good forcing function. But current Claude Code guidance already pushes minimal diffs and reuse, so the always-on mode partially re-states defaults at the cost of ~4 KB per session. The distinct value is in the sub-skills: `ponytail-audit` (whole-repo bloat scan) and `ponytail-debt` (harvest `ponytail:` deferral comments into a ledger) do things nothing built-in does. `ponytail-gain` and `ponytail-help` are display cards — harmless. `ponytail-review` overlaps `/code-review` but its complexity-only focus is a legitimate complement.

---

## Standing context cost

Every installed skill's description is loaded into every session whether used or not. Your current roster puts roughly 4–5 KB of skill descriptions plus ~6–7 KB of caveman+ponytail hook injections into every conversation before you type anything — call it ~3,000 tokens of permanent overhead per session. The two mode plugins are the majority of it, which is ironic for plugins sold on token savings.

---

## Recommendations, in order of impact

1. **Delete stop-slop** — broken, undiscovered, fully redundant with humanizer.
2. **Resolve the impeccable duplicate** — keep `~/.claude/skills/impeccable` (the one Claude Code loads); remove the `.agents` copy unless you use other coding agents.
3. **Pick one review path** — suggest built-in `/code-review` for correctness + `ponytail-review` for bloat; retire `caveman-review` and stop using `cavecrew-reviewer`.
4. **Decide if caveman mode earns its keep** — if you keep it, keep it for `caveman-compress` and `caveman-stats`; the always-on chat compression fights the model's communication guidance and costs more input than it saves output.
5. **Retire or consciously keep emil-design-eng** — impeccable subsumes it for actual work; keep only if you consult the philosophy directly.
6. **Configure or dismiss the statusline** — both mode plugins nag about it every session start.

Keep as-is: impeccable, find-skills, humanizer, animation-vocabulary, review-animations (knowing it's manual-invoke only), cavecrew-investigator, ponytail-audit/debt.
