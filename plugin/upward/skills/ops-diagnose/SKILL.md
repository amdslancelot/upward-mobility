---
name: ops-diagnose
description: Environment diagnosis and context management. Use this when a session loses focus, context blows up, or a fix seems like it should work but the environment itself is suspect — covers the behavior patterns that leak the most tokens and how to fix them, the criteria for /compact vs /clear, and the checklist for widening your search to environment/dependencies/earlier steps plus the evidence gate that stops you from blaming the environment too fast. Use when the session loses focus, context bloats, or a fix that should work does not take effect.
---
# Environment diagnosis: where this harness leaks the most tokens, loses focus fastest, and breaks most often

> Audience: the smaller model inheriting this project. Every rule ships with a "just do this" fix.
> Traps 1–5 are portable across environments; sections marked "environment-specific" are already filled in for this environment (as of 2026-07-07) — rediagnose and rewrite them when you move this to another project.

## 0. Adopting this template? Rediagnose your environment first (do this once)

Change projects or harness config, and the trap list may no longer match. Diagnosis steps:

1. Check what gets injected at session start — which plugin hooks are active, how many tokens they burn as standing overhead. (Visible in the first API call of the session log.)
2. Check whether CLAUDE.md exists and is index-style. If it doesn't exist, that's leak #1 — build it now.
3. Run a few typical tasks and watch whether the main conversation swallows large files or long logs directly. If it does, that's trap 3.
4. Rewrite the findings into this file's "this environment" sections, and delete whatever no longer applies.

## 1. Missing (or rotted) CLAUDE.md → every session re-scans the repo from scratch (the biggest leak)

**Symptom**: every new session re-`ls`'s, re-reads config files, re-greps for core logic — burning tens of thousands of tokens to rebuild the same mental model each time, and a weaker model rebuilds it worse (it misses files with non-obvious names).

**Fix (just do this)**:
1. At session start, read the CLAUDE.md index first, and **only read the file the current task's entry points to**.
2. Don't scan all of `src/` just to "understand the project." If the index doesn't cover it, dispatch a search-type subagent instead.
3. Learn an important fact the index doesn't have? Add it as one line to the index, per the source repo's `meta/maintenance.md`.

## 2. Standing plugins/hooks clashing in noise and mode (environment-specific — rediagnose and rewrite when you port this)

**Symptom** (this environment, as of 2026-07-07): two standing plugins — caveman (terse-speech mode) and ponytail (laziest-implementation mode) — inject roughly 2k tokens per session. Weaker models let "save words" bleed into places it shouldn't (docs, commits, security warnings), and misread "shortest diff" as "skip understanding, edit immediately."

**Fix (just do this)**:
1. Speech compression only applies to conversational replies. The test: does this text get saved into the repo? If yes, write full sentences normally.
2. Before touching code, read every file the change will touch, *then* pick the minimal approach. If partway through you find the file count is more than double your estimate, stop, re-read the scope, update the estimate, and only then continue. Still over? Change course or escalate per `ops-judge skill` #4.
3. When the user asks you to turn a mode off, do it immediately — don't drift back to it a few turns later.

## 3. The main conversation doing bulk reads/execution itself (the behavior pattern that leaks the most tokens)

**Symptom**: the main conversation reads large files directly, chains greps, swallows long build logs — all that raw output lands in main context, one big scan eats a quarter of the context window, and judgment quality degrades from there on.

**Fix (just do this)**:
1. Any reconnaissance work that needs "3 or more files (≥3) to answer" or "output over 100 lines" gets dispatched to a subagent (see `ops-dispatch skill`); the main conversation only receives the conclusion plus `file:line`. This threshold and `ops-dispatch skill`'s "≥3–4 rounds of tool calls" are two phrasings of the same rubric — when in doubt, go by round count.
2. Running tests/builds: pipe long output to a file (`... > /tmp/build.log 2>&1`), then only read the last 30 lines or grep for `error`.
3. For every chunk of text about to enter context, ask: is this a **conclusion** or **raw material**? Raw material doesn't belong in the main conversation.

## 4. Context compounds — the criteria for /compact and /clear

**The mechanism, in one line**: the API is stateless, so the whole conversation gets resent every turn; every token that enters main context gets paid again on every remaining turn of the session (caching discounts it, but it's never free).

**Fix (just do this)**:
1. Task delivered, next task is **related** → confirm conclusions are already saved to file, then suggest the user run `/compact` keeping file paths, line numbers, and open items.
2. Next task is **unrelated** → suggest `/clear` (a fresh session rebuilds from the CLAUDE.md index, which is cheaper than compacting and doesn't distort anything).
3. Don't compact mid-task.
4. These two commands are typed by the user — your job is to proactively remind them at task boundaries, and make sure saving to file happens before compacting.

## 5. When a fix won't take: widen the search to environment/dependencies (don't just stare at the failing line)

**Symptom**: the same fix should work but doesn't, or the error stack points at a file/layer you've never touched. A weaker model's default is to stare at the reported line and keep tweaking it, but the root cause can live in the environment, a dependency, or an earlier step — and this class of root cause **cannot be fixed by escalating the model** (Opus fails the same way against a broken dependency). Staring at it just burns your two retry rounds on a fight you can't win.

**Checklist (work through in order when the symptom won't budge)**:
1. Versions: lockfile vs. what's actually installed; does the runtime/language version match your assumptions?
2. Stale artifacts: build cache, `node_modules`/`__pycache__`, old compiled output not cleaned up.
3. Config/env: environment variables and config files not matching your assumptions.
4. Clean reproduction: does it still reproduce from a clean clone / fresh install? (Isolates "my local state" from "the program itself.")
5. Which layer the error originates from: stack points at a file you've never touched → the root cause is upstream (an earlier step or a dependency — go back to the regression branch of `ops-judge skill` #4).

**Evidence gate (to stop abuse)**: "blame the environment" is the easiest excuse there is — nine times out of ten it's actually your own bug. Before accepting an environment/dependency hypothesis, **produce evidence first**: a version number that doesn't match, or a result that reproduces from a clean clone. Suspicion alone doesn't count; the default assumption stays "it's my change" until the environment hypothesis has evidence behind it.

Good: `node -v` prints 18, but the lockfile pins a package that needs 20 → concrete mismatch, environment hypothesis earns its place.
Bad: "the test is flaky, probably a caching thing" with nothing measured → that's a guess, not evidence; keep assuming it's your change.

## Minor (below the top four, but worth noting)

- Long-session context compaction drops detail: write important intermediate conclusions to file **as you go**, not after.
- The memory directory (this environment: `~/.claude/projects/-Users-lans-h-Documents-claude-main/memory/`; swap in `~/.claude/projects/<project>/memory/` when you port this) loads its index across sessions — cross-session facts belong there; single-session facts don't.
