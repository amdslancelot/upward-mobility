# A Letter to Future Sessions — Skeleton

> How to use this: at the end of any major session (standing up a system, a big architectural decision, a
> long deep-dive on some problem), write a `meta/letter-to-future-sessions.md` (in this directory; if one
> already exists, append a new section, labeled with date and model) following this skeleton. The value of
> this letter is writing down "the stuff files and code can't tell you": your confidence level on judgment
> calls, roads not taken, expected ways things will degrade.

---

# A Letter to Future Sessions

> Written {{date}}, in a {{model}} session. Whoever picks this up next is probably {{expected next model}}.

## Three things the user didn't ask, but I think matter most

{{One paragraph each. The test: what's something that, "if I don't say it now, a future session will burn a
lot of quota rediscovering it"? Common categories: where the real bottleneck actually is (vs. the surface
task), a cheap experiment worth running before starting work, the user's unstated working philosophy.}}

**1. {{...}}**

**2. {{...}}**

**3. {{...}}**

## The most likely ways this system/decision degrades, and how to prevent them

{{List 3–4. Each: one sentence for the degradation scenario + one sentence for the prevention (the
prevention has to point at a specific file/rule, not just "be careful"). Common degradations: an index path
rots → trust collapses, rules get skipped under time pressure, the lessons file turns into a junk drawer,
the system bloats itself.}}

1. **{{degradation mode}}**: {{scenario}}. Prevention: {{concrete mechanism}}.

## Ranked honestly: which outputs I trust least

{{This section matters most — it cannot be empty. Each item: the output + why confidence is low + the
first thing whoever takes over should verify. Unmeasured numbers, single-source verification, advice that
might be over-engineered — all of that belongs here.

Example of the level of concreteness expected: "The '80% recoverable' figure — a structured estimate, zero
measurement. Verify by redoing three past tasks with the new workflow and comparing output quality." A
vague entry like "some numbers might be off" doesn't meet the bar — name the specific output and the
specific check.}}

1. **{{output}}**: {{why confidence is low + how to verify it}}.

## Last thing

The system exists to save judgment, not to be worshipped. If a rule gets in your way three times running,
bring the evidence to the user and ask whether it should change.
