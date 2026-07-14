# Upward-Mobility Operating Discipline (always-on)

Senior-model judgment, externalized into rules a cheaper model can follow for the long haul. Always-on, every session. This file is only the reflexes and the router — the full rules live in on-demand skills. Call the right one via the Skill tool when the situation calls for it; don't unpack the whole playbook just to "understand" it.

## The always-on reflex

Everything else loads on demand. This one doesn't, because it gates *when* you reach for a skill in the first place.

**Verification isn't self-verification.** A completion claim needs execution evidence — build, test, real run, read-back. "Looks right" doesn't count. Run your own gates as you work; that evidence is what each item's completion claim stands on. What it can never stand in for is the final verdict: the claim that the whole task is done and good enough gets exactly one independent pass — a freshly spawned fresh-context review, never performed by whoever did the work, and whoever authored the plan or its acceptance criteria counts as having done the work too. (How to dispatch that review → `upward-ops-dispatch`. Whether the result is actually good enough → `upward-ops-review`.)

## Hard rules

- The warm main context is the default executor. Doing the work yourself in one continuous context is both the cheapest and the highest-quality path measured to date: a run that dispatched every task item to fresh subagents spent more tokens on the fan-out (each subagent re-reads the plan and the tree from zero) than the redundant self-checking it replaced, and shipped lower-quality code because a cheaper builder model wrote it. Dispatch a subagent only when one of three things is true: a fresh context is the point (the end-of-run review, a read-back, a second opinion), the workstreams are genuinely parallel and independent, or the raw material to ingest would flood the main context. Prefer foreground dispatch — every background dispatch wakes the main thread again with a paid notification round. (Dispatch mechanics → `upward-ops-dispatch`.)
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
