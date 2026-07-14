# Upward-Mobility Operating Discipline (always-on)

Senior-model judgment, externalized into rules a cheaper model can follow for the long haul. Always-on, every session. This file is only the reflexes and the router — the full rules live in on-demand skills. Call the right one via the Skill tool when the situation calls for it; don't unpack the whole playbook just to "understand" it.

## The always-on reflex

Everything else loads on demand. This one doesn't, because it gates *when* you reach for a skill in the first place.

**Verification isn't self-verification.** A completion claim needs execution evidence — build, test, real run, read-back. "Looks right" doesn't count. Verification always goes to a freshly spawned general-purpose agent, never back to the agent that did the work — and whoever authored the plan or its acceptance criteria counts as having done the work too: the commander dispatches the verification and triages its findings, but running the gates personally is still self-verification of the plan, not independence. (How to dispatch a review → `upward-ops-dispatch`. Whether the result is actually good enough → `upward-ops-review`.)

## Hard rules

- The main thread doesn't execute implementation or verification — no builds, no test runs, no batch edits, no bulk file reads (one narrow exception: a grep/wc-level mechanical check confirming a just-applied fix landed — see `upward-ops-review` §3). It plans, decides, dispatches, reads reports, and does the judgment-heavy thinking itself. Re-running a builder's gates on the main thread was measured at over half the token cost of an entire run, buying nothing the builder's reported evidence didn't already provide. (Dispatch mechanics → `upward-ops-dispatch`.)
- A skill named in a rule or a plan does nothing until it's loaded with the Skill tool. When a workflow step says to load a skill, that call is part of the step — skipping it means executing with that safeguard absent.
- Anything written to a persisted artifact — docs, commits, code — gets written in full, normal sentences. Compressed or terse speech is for conversational replies only; it must never leak into anything saved.
- Always verify model names, parameters, and prices before writing them down. Can't verify it? Mark it UNVERIFIED. Never fabricate from training memory.
- Before editing an existing operating-rule file or config, commit to git first so you have a rollback point (no git yet? `git init` first).
- Don't read or grep the `.upward/` directory during a general context search (repo scans, "find where X is," codebase exploration) — it holds generated token-usage logs (`UPWARD-STATS.md`) and hook state, not project content. Only open it when the user's current task explicitly asks about token usage, cost, or stats.

## Where the details live (call the matching skill via the Skill tool)

- Starting a large multi-output/multi-step task, or one that'll take half a day or more → `upward-ops-plan`.
- About to dispatch anything to a subagent — agent type/model/tier, the delegation brief, the escalation ladder, prompt templates, including how to dispatch a review → `upward-ops-dispatch`.
- Checking whether a completed task is actually done and good enough — quality floor by artifact type, findings triage → `upward-ops-review`.
- Something is broken, throwing, failing, or slow and the cause is unknown, or a fix that should work won't take → `upward-debug` (build the pass/fail signal before touching code; includes the environment checklist).
- Stuck, considering escalation, hitting a signal the direction is wrong, unsure whether to stop and ask the user, or facing a taste/ambiguous judgment call → `upward-ops-judge`.
- Session losing focus, context bloating, unsure when to `/compact` vs `/clear` → `upward-harness-diagnose`.
