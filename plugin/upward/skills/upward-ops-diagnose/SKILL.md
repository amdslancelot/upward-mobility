---
name: upward-ops-diagnose
description: Harness diagnosis and context management. Use this when a session loses focus or context blows up — covers the behavior patterns that leak the most tokens and how to fix them, plus the criteria for /compact vs /clear. Use when the session loses focus, context bloats, or you are deciding between /compact and /clear. (Debugging the project itself, including environment/dependency causes, lives in upward-ops-debug.)
---
# Harness diagnosis: where this harness leaks the most tokens and loses focus fastest

> Audience: the smaller model inheriting this project. Every rule ships with a "just do this" fix.
> This file covers the harness (session hygiene, token leaks, context management). Diagnosing the *project* — a bug, a fix that won't take, an environment/dependency suspect — lives in `upward-ops-debug`.
> Traps 1–4 are portable across environments; sections marked "environment-specific" are already filled in for this environment (as of 2026-07-07) — rediagnose and rewrite them when you move this to another project.

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
2. Before touching code, read every file the change will touch, *then* pick the minimal approach. If partway through you find the file count is more than double your estimate, stop, re-read the scope, update the estimate, and only then continue. Still over? Change course or escalate per `upward-ops-judge skill` #4.
3. When the user asks you to turn a mode off, do it immediately — don't drift back to it a few turns later.

## 3. The main conversation doing bulk reads/execution itself (the behavior pattern that leaks the most tokens)

**Symptom**: the main conversation reads large files directly, chains greps, swallows long build logs — all that raw output lands in main context, one big scan eats a quarter of the context window, and judgment quality degrades from there on.

**Fix (just do this)**:
1. Any reconnaissance work that needs "3 or more files (≥3) to answer" or "output over 100 lines" gets dispatched to a subagent (see `upward-ops-dispatch skill`); the main conversation only receives the conclusion plus `file:line`. This threshold and `upward-ops-dispatch skill`'s "≥3–4 rounds of tool calls" are two phrasings of the same rubric — when in doubt, go by round count.
2. Running tests/builds: pipe long output to a file (`... > /tmp/build.log 2>&1`), then only read the last 30 lines or grep for `error`.
3. For every chunk of text about to enter context, ask: is this a **conclusion** or **raw material**? Raw material doesn't belong in the main conversation.

## 4. Context compounds — the criteria for /compact and /clear

**The mechanism, in one line**: the API is stateless, so the whole conversation gets resent every turn; every token that enters main context gets paid again on every remaining turn of the session (caching discounts it, but it's never free).

**Fix (just do this)**:
1. Task delivered, next task is **related** → confirm conclusions are already saved to file, then suggest the user run `/compact` keeping file paths, line numbers, and open items.
2. Next task is **unrelated** → suggest `/clear` (a fresh session rebuilds from the CLAUDE.md index, which is cheaper than compacting and doesn't distort anything).
3. Don't compact mid-task.
4. These two commands are typed by the user — your job is to proactively remind them at task boundaries, and make sure saving to file happens before compacting.

## Minor (below the top four, but worth noting)

- Long-session context compaction drops detail: write important intermediate conclusions to file **as you go**, not after.
- The memory directory (this environment: `~/.claude/projects/-Users-lans-h-Documents-claude-upward-mobility/memory/`; swap in `~/.claude/projects/<project>/memory/` when you port this) loads its index across sessions — cross-session facts belong there; single-session facts don't.
