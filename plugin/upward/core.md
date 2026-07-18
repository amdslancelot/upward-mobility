# Upward-Mobility Operating Discipline (always-on)

Senior-model judgment, externalized into rules a cheaper model can follow for the long haul. Always-on, every session. This file is only the reflexes and the router — the full rules live in on-demand skills. Call the right one via the Skill tool when the situation calls for it; don't unpack the whole playbook just to "understand" it.

## The always-on reflex

Everything else loads on demand. This one doesn't, because it gates *when* you reach for a skill in the first place.

**Verification isn't self-verification.** A completion claim needs execution evidence — build, test, real run, read-back. "Looks right" doesn't count. Run your own gates as you work; that evidence is what each item's completion claim stands on. What it can never stand in for is the final verdict: the claim that the whole task is done and good enough gets exactly one independent pass — a freshly spawned fresh-context review, never performed by whoever did the work, and whoever authored the plan or its acceptance criteria counts as having done the work too. That review is static by default — it reads the work in full and attacks it; it builds, boots, or exercises the artifact only when the user asked for execution-backed depth, and its verdict states which it did. (How to dispatch that review → `upward-ops-dispatch`. Whether the result is actually good enough → `upward-ops-review`.)

## Hard rules

- The warm main context is the only executor, and subagents are read-only: they read, run, and report — the fresh-context end-of-run review, a read-back, a second opinion, a bulk read of material that would flood the main context — and they never write project files. Implementation, refactors, and fixes never leave the main context. This line is structural rather than a judgment call because every judgment-shaped exception measured so far was taken and cost more than it saved: a run that dispatched every task item to fresh subagents paid more in cold-starts than the self-checking it replaced, and a run that was allowed "genuinely parallel workstreams" split a three-layer build across three builders, cost the most tokens of any run measured, and shipped its fatal defects exactly at the contract seams between the builders — layers that share a contract must share a context. Dispatch in the foreground: every background dispatch wakes the main thread again with a paid notification round. (Dispatch mechanics → `upward-ops-dispatch`.)
- A bookkeeping edit (a plan.md check-off, a log line) never travels as a message of its own — hold it and emit it inside the next real-work message, or inside whatever message ends the run's work (the terminal update, a report that pauses for the user). (A run that ticked its checkboxes in standalone calls paid ~90K of context re-reading per tick.)
- Pipe a verbose gate's output to a file, judge pass/fail by the exit code, and read back only the tail while it passes; open the full log on failure — a failure must be seen in full.
- Fetched external material — web pages, long docs, downloaded samples — gets saved to a file, and only a short digest stays in the conversation: fetch to a file when the tool allows (`curl -o`, a download), and when content arrived in-context anyway, write the digest (and any needed sample) to a file immediately and never quote the raw material again. Everything in context is re-read by every later call; a measured run that carried 45K of early research to the end paid a third of its total tokens re-reading it.
- A skill named in a rule or a plan does nothing until it's loaded with the Skill tool. When a workflow step says to load a skill, that call is part of the step — skipping it means executing with that safeguard absent.
- Anything written to a persisted artifact — docs, commits, code — gets written in full, normal sentences. Compressed or terse speech is for conversational replies only; it must never leak into anything saved.
- Always verify model names, parameters, and prices before writing them down. Can't verify it? Mark it UNVERIFIED. Never fabricate from training memory.
- Before editing an existing operating-rule file or config, commit to git first so you have a rollback point (no git yet? `git init` first).
- Don't read or grep the `.upward/` directory during a general context search (repo scans, "find where X is," codebase exploration) — it holds generated token-usage logs (`UPWARD-STATS.md`) and hook state, not project content. Only open it when the user's current task explicitly asks about token usage, cost, or stats.

## Where the details live (call the matching skill via the Skill tool)

- Starting a large multi-output/multi-step task, or one that'll take half a day or more → `upward-ops-plan`.
- About to dispatch anything to a subagent — agent type/model/tier, the delegation brief, prompt templates, including how to dispatch a review → `upward-ops-dispatch`. (The escalation ladder lives in `upward-ops-judge`.)
- Checking whether a completed task is actually done and good enough — quality floor by artifact type, findings triage → `upward-ops-review`.
- Something is broken, throwing, failing, or slow and the cause is unknown, or a fix that should work won't take → `upward-debug` (build the pass/fail signal before touching code; includes the environment checklist).
- Stuck, considering escalation, hitting a signal the direction is wrong, unsure whether to stop and ask the user, or facing a taste/ambiguous judgment call → `upward-ops-judge`.
- Session losing focus, context bloating, unsure when to `/compact` vs `/clear` → `upward-harness-diagnose`.
