# Environment diagnosis: where this harness leaks the most tokens, loses focus fastest, and breaks most easily

> Reader: a smaller model taking over this project. Every item ships with a "just follow these steps" fix.
> Traps 1–5 are universal across environments; sections marked "environment-specific" are already filled in for this environment (2026-07-07) — rediagnose and rewrite them when porting to another project.

## 0. When adopting this template: rediagnose your environment (do this once)

Change projects or harness settings, and the trap list may change. Diagnosis steps:

1. Look at what gets injected at session start: which plugin hooks are active, how many tokens the standing injection costs (visible in the first API call of the session log).
2. Check whether CLAUDE.md exists and is index-style. If it doesn't exist, that's the biggest leak — build it first.
3. Run a few typical tasks and watch whether the main conversation directly swallows big files or long logs. If it does, that's trap 3.
4. Rewrite the diagnosis results into this file's "this environment" sections, and delete whatever doesn't apply.

## 1. Missing (or rotted) CLAUDE.md → every session re-scans the repo from scratch (the biggest leak)

**Symptom**: every new session re-runs ls, re-reads config files, greps for core logic — burning tens of thousands of tokens every time to rebuild the same understanding, and a weaker model rebuilds it worse (it'll miss non-obviously-named files).

**Fix (just follow this)**:
1. At session start, read the CLAUDE.md index first, and **only read the files the task actually points to**.
2. Don't scan all of src/ just to "understand the project." If the index doesn't cover it, dispatch a search subagent.
3. Learn an important fact the index is missing? Add it to the index in one line, per `meta/maintenance.md`.

## 2. Standing plugins/hooks: noise, and clashing with the model's own patterns (environment-specific — rediagnose and rewrite when porting)

**Symptom** (this environment, 2026-07-07): two standing plugins — caveman (ultra-terse phrasing) and ponytail (laziest-possible implementation) — inject about 2k tokens every session. A weak model will let "say less" bleed into places it shouldn't (documents, commits, security warnings), and misread "shortest diff" as "skip understanding and just edit."

**Fix (just follow this)**:
1. Compressed phrasing is for conversational replies only. Rubric: will this text get saved into the repo? If yes, write it out in full, normal sentences.
2. Before touching code, read every file the change will touch first, then pick the smallest viable approach. If partway through you find the number of files to touch has more than doubled your estimate, stop, reread the scope, update your estimate, then continue. Still over-budget? Change course or escalate per `ops/judgment-rubrics.md`#4.
3. When the user asks you to turn off a mode, comply immediately — don't slide back into it a few rounds later.

## 3. The main conversation doing bulk reads/execution itself (the behavior pattern that leaks the most tokens)

**Symptom**: the main conversation directly reads large files, runs grep after grep, swallows long build logs — all of that raw output lands straight in the main context, one big scan eats a quarter of the context budget, and judgment quality degrades from there on.

**Fix (just follow this)**:
1. Any investigative work that needs 3+ files read to answer, or will produce over 100 lines of output, gets dispatched to a subagent (see `ops/model-dispatch.md`); the main conversation only receives conclusions + `file:line`. This threshold and `ops/model-dispatch.md`'s "≥3–4 rounds of tool calls" are two phrasings of the same rubric — go by rounds at the margin.
2. Running tests/builds: pipe long output to a file (`... > /tmp/build.log 2>&1`), read only the last 30 lines or grep for error.
3. Ask, of every chunk of text about to enter context: is this a conclusion or raw material? Raw material doesn't belong in the main conversation.

## 4. Context compounding, and the rubric for `/compact` vs `/clear`

**The mechanism in one sentence**: the API is stateless — the entire conversation gets resent every turn; every token that enters the main context gets re-paid on every remaining turn of the session (caching discounts it, doesn't make it free).

**Fix (just follow this)**:
1. Current task delivered, next task is **related** → confirm the conclusions are already saved to files, then suggest the user run `/compact keep file paths, line numbers, unfinished items`.
2. Next task is **unrelated** → suggest `/clear` (a new session rebuilds from the CLAUDE.md index, which is cheaper than compacting and doesn't lose fidelity).
3. Don't compact mid-task.
4. These two commands are typed by the user; your obligation is to proactively remind them at task boundaries, and make sure saving happens before compacting.

## 5. When a fix won't take: widen the search to environment/dependencies (don't just stare at the failing line)

**Symptom**: the same fix should work but doesn't, or the error stack points at a file/layer you've never touched. A weak model's default is to stare at the error line and keep tweaking it, but the root cause might be the environment, a dependency, or an earlier step — and this class of root cause **escalating the model cannot fix** (opus fails just as hard against a broken dependency). Staring at it just burns your two retry rounds on a fight you can't win.

**Checklist (work through in order when a symptom is being stubborn)**:
1. Versions: lockfile vs. what's actually installed; does the runtime/language version match your assumptions?
2. Stale artifacts: build cache, `node_modules`/`__pycache__`, old compiled output not cleaned up.
3. Config/env: environment variables and config files not matching your assumptions.
4. Clean reproduction: does it still reproduce from a clean clone / fresh install? (Isolates "my local state" from "the program itself.")
5. Which layer the error originates from: stack points at a file you've never touched → the root cause is upstream (an earlier step or a dependency — go handle it as the regression branch of `ops/judgment-rubrics.md`#4).

**Evidence gate (against abuse)**: "blame the environment" is the easiest excuse there is — nine times out of ten it's actually your own bug. Before accepting an environment/dependency hypothesis, **produce actual evidence first**: a version number that doesn't match, a result reproducible from a clean clone. Suspicion alone doesn't count; the default stance stays "it's my change" until the environment theory has evidence behind it.

**Good example**: `node -v` prints 18, but the lockfile pins a package that needs 20 → concrete mismatch, environment hypothesis earns its place. ✅
**Bad example**: "the test is flaky, probably a caching thing" with nothing measured → that's a guess, not evidence; keep assuming it's your change. ❌

## Minor (below the top four, but worth noting)

- Context compaction on long sessions can drop details: write important intermediate conclusions into files as you go, not after.
- The memory directory (this environment: `~/.claude/projects/-Users-lans-h-Documents-claude-main/memory/`; swap in `~/.claude/projects/<project>/memory/` when porting) loads its index across sessions — write cross-session facts there; don't write single-session facts there.
