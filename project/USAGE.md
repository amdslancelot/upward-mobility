# USAGE — how to use this architecture to close the gap on Fable 5

> Reader: you, the user (secondary reader: the main-thread model). Written: 2026-07-07, Fable 5 session.
> For the full assessment of what this pack can and can't substitute for → `meta/AUDIT-2026-07-07.md`.

## 0. The mental model (read this before you use anything else)

Fable 5's edge isn't "smarter at every single step." It comes down to three things:

1. It decomposes problems in the right direction.
2. It catches its own mistakes.
3. It knows when to stop.

This architecture swaps the first for "Opus plans, you audit the plan," and swaps the other two for "checklists + fresh-context verification."

So here's the thing: **your role shifts from "the person giving orders" to "the person auditing acceptance criteria and plans."** Those two extra minutes you spend auditing the plan are exactly where most of the gap between a weak model and Fable 5 lives. Skip those two minutes, and this whole pack is just a pile of files nobody reads.

## 1. The standard flow for every session

**Opening moves**
1. Pick your commander: `/model sonnet` (the everyday default). Task is ambiguous, spans many files architecturally, or requires trade-off calls → `/model opus`.
   Note: which actual version an alias points to (sonnet-4-6 is legacy, sonnet-5 is current) is whatever the `/model` interface shows you. See the "available resources" section of `ops/model-dispatch.md` for details.
   **Never use haiku as commander.** Its delegation judgment and the quality of its acceptance criteria can't carry this system; haiku is subagent-only.
2. New task, unrelated to the last one → `/clear` first (the commander rebuilds itself from the CLAUDE.md index — cheap, and nothing gets lost in the process).

**Midstream** (the commander follows the discipline automatically — you only need to watch two things)
- Is it delegating? Bulk file reads, repo scans, and verification should all be delegated. See it grepping or reading big files itself, repeatedly? Pull it back with a trigger phrase from section 3.
- Does its completion claim have execution evidence behind it? Just "I fixed it," no test output or read-back → say "Verification isn't self-verification — delegate to a fresh-context agent."

**Wrapping up**
- Stopping mid-task → confirm the conclusions are saved to a file, then `/compact keep file paths, line numbers, and unfinished items`.
- Switching to a different task → `/clear`.
- Major session (new discipline established, big decision made) → have the model write a handoff letter following `meta/letter-template.md`.

## 2. Budget allocation: pricier model up front, cheaper model in back

Judgment concentrates in the early part of a task (direction, decomposition, acceptance criteria); execution concentrates in the middle and later parts. So:

| Phase | Model | Where it's spent |
|---|---|---|
| Planning, decomposition, defining acceptance criteria | opus (commander or Plan agent) | The first cut at an ambiguous requirement — the spot a weak model can least make up for |
| Execution | sonnet commander → delegates to sonnet/haiku subagents | Multi-round execution of an already-confirmed plan |
| Verification | haiku (mechanical read-back) / sonnet (semantic review) | Cheap and non-negotiable — don't skip it |

The one-liner version: **spend ten minutes with opus getting the plan right, rather than two hours with sonnet going the wrong way.**

For a one-off task that's due tonight and needs top quality: just run `/model opus` start to finish, skip the whole discipline flow. This system trades money for time, not the other way around.

## 3. How to write the prompt (the core section)

### 3.1 Your prompt needs three things (this mirrors the three required elements of a delegation brief)

1. **Goal and motivation**: what to do, and why. The motivation is what lets the model guess in the right direction at edge cases.
2. **Acceptance criteria**: what counts as good. Can't articulate it? Use the phrasing in 3.2 to have the model propose it first.
3. **Boundaries**: what not to touch, what's already decided and isn't up for re-litigation.

**Bad example**: "Help me optimize this project's performance."
(Vague goal + no acceptance criteria = a weak commander will work on what it's good at, not what matters.)

**Good example**: "The list page takes 3 seconds to load (target: <1s). First find out whether the bottleneck is frontend or the query, report back the evidence, and then we'll decide what to fix. Don't touch the schema."
(The goal has a number, diagnosis comes before action, boundaries are explicit.)

### 3.2 Important tasks: plan first, execute second (the cheapest quality lever there is)

For ambiguous or high-risk tasks, add this line:

> "Don't touch anything yet. Give me: (1) your understanding of the task (2) a breakdown of steps and who does each one (3) acceptance criteria. I'll confirm before you execute."

When you audit the plan, check exactly three things:

1. Is the direction right?
2. Are the acceptance criteria decidable (numbers or runnable checks, not "make it good")?
3. Are there assumptions it can't fill in on its own?

This step substitutes for Fable 5's "gets the first cut right" — don't skip it.

### 3.3 Trigger phrases (a weak commander drifts — use these to pull it back to the discipline)

| Situation | You say |
|---|---|
| It's scanning files itself, reading big files back to back | "The commander doesn't descend — delegate per ops/model-dispatch.md." |
| It claims done with no evidence | "Per ops/judgment-rubrics.md#2, give me execution evidence — delegate verification to a fresh-context agent." |
| It's spinning on the same error | "Per ops/judgment-rubrics.md#4, check whether it's time to change approach, or escalate with the failure trace." |
| It's stacking a third fix on a broken state, and things are getting messier | "Roll back to the last green checkpoint first — don't stack fixes on a broken state. Per ops/judgment-rubrics.md#4, decide whether to bisect or re-plan." |
| It's asking you about something small that already has a convention | "Per ops/judgment-rubrics.md#3, pick the standard default and keep going — just mention it in one line in the report." |
| Starting a new session to continue old work | "Read the CLAUDE.md index first, then just the file relevant to the task — don't scan the whole pack." |

Naming the file matters. A weak model responds vaguely to "follow the rules," and precisely to "follow section N of file X."

### 3.4 Ambiguous questions and taste calls (a weak model's ceiling — change tactics here)

- **Decomposition direction is unclear.** `/model opus` + the 3.2 phrasing, asking it to "give me two options, each with reasoning and risk, and tell me which you'd recommend." You choose, sonnet executes.
- **Taste / feel** (UI feel, copy tone, animation). Don't let any model freewheel here. Ask for two versions, A and B, and you pick — or first establish a measurable proxy metric (load time in ms, a readability score). See the criteria in `ops/judgment-rubrics.md`#6.
- **High-stakes judgment calls.** Ask for a multi-answer panel: "Have two agents answer this independently, then have a third compare where they diverge and show me." The divergence points are exactly what needs your arbitration. Where they agree, you can trust it.

### 3.5 Delegating large tasks (handing off a whole afternoon of work in one go)

For multi-output tasks that need the full quality loop (list tasks → execute → delegate review → go back and revise), copy the full skeleton from `WEAK-MODEL-PROMPT-GUIDE.md`. It spells out "go back and revise after review" as an explicit obligation, which is the only way a weak model actually does it. First time using it, read the "worked example" section in that file in full. Here's the short version of the skeleton:

> "Task: [goal and motivation].
> Rules: follow the CLAUDE.md discipline — check ops/model-dispatch.md before delegating, copy templates from ops/prompt-templates.md for delegation briefs,
> save after finishing each item before moving to the next, delegate to a fresh-context agent to verify everything once done, then give me a one-page summary.
> Acceptance criteria: [itemized, decidable conditions].
> If you're stuck for two rounds, stop and write up the situation — don't force it."

## 4. What this architecture can't make up for (managing your expectations)

1. **Taste and sensory quality.** The tactics in 3.4 above just hand the choice back to you; they don't make the model tasteful.
2. **"Not knowing what it doesn't know."** A weak commander won't realize it failed to ask a critical question. Mitigation: you're the backstop on the plan review in 3.2.
3. **Consistency over very long spans.** For large projects spanning many sessions, handoff letters and meta/lessons.md carry the baton forward, but every handoff loses something. Break large projects into independently-acceptable segments, one per session.

## 5. Anti-patterns (fix these the moment you spot them)

- Leaving this pack's files sitting unmentioned, expecting the model to read them on its own. CLAUDE.md loads every session, but drift mid-session still needs your trigger phrases.
- Using haiku as commander to save money. Whatever you save gets paid back double in rework.
- Skipping the delegated verification step "because the task is simple." Verification is the one line of defense in this whole system that doesn't depend on the model being honest.
- Using /compact instead of saving to a file. Compact drops line numbers and detail; save first, compaction is secondary.
- Spinning up a new subagent for every tiny question. If the answer's already sitting in the conversation, just ask it directly. See the "cost intuition" section of `ops/model-dispatch.md` for the delegation criteria.
