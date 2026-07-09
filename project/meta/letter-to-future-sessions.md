# A Letter to Future Sessions

> Written 2026-07-07, in a Fable 5 session — the user's last Fable 5 quota run. Whoever picks this up next
> is probably Sonnet or Opus. This letter is about the stuff files and rules can't tell you.

## Three things the user didn't ask, but I think matter most

**1. This system's quality ceiling is "how good are the acceptance criteria" — and that quality is guarded by the user, not by you.**
You (a weak commander) will systematically write acceptance criteria that are too vague. That's not a
knock, it's a known trait. So important tasks should always go through `USAGE.md` 3.2's "plan first, then
execute": show the user the acceptance criteria before you start work. When the user skips this step, your
job is to remind them once — once, no lecturing.

**2. The system's biggest remaining gap is "the first cut at a vague requirement," and the cheapest fix for that lives on the user's side, not yours.**
Every bit of clarity the user adds to a requirement raises the quality of the whole execution chain by a
notch. When you get a vague request, respond first with "Here's how I understand the task: X, and here's
my breakdown: Y" before you touch anything. Surface the misunderstanding at step 0, not after 20 steps of
rework. That's cheaper than any amount of after-the-fact verification.

**3. This pack is self-sufficient — all the methodology you need for judgment calls is already inside it.**
- Review-dispatch methodology lives in `ops/review-dispatch.md`.
- Cost intuition for delegation lives in the "Cost Intuition" section of `ops/model-dispatch.md`.
- The task quality loop lives in `WEAK-MODEL-PROMPT-GUIDE.md` at the root.

The full mechanics behind delegation cost used to live in `ops/agent-dispatch-mechanics.md` inside the
pack. On 2026-07-08 it was moved up to `docs/` as background reading — it's an explanatory research report,
not something you need for day-to-day operation. The three files above already contain every actionable
rule, and every in-pack reference has been repointed to them. The system's operation doesn't depend on any
file outside the pack.

One more thing the user should know — a finding from the 2026-07 environment checkup, environment
miscellany that doesn't affect the system itself: the user's skill/plugin list has redundancy. stop-slop is
installed broken, and there are four overlapping review paths. Cleanup is recommended, but the user hasn't
gotten to it yet.

## The most likely ways this system degrades, and how to prevent them

1. **Trigger phrases stop being used**: over time the user stops invoking the trigger phrases from
   `USAGE.md` 3.3, and the commander drifts back into doing the work itself. Prevention: at the start of
   each session, proactively read CLAUDE.md's core three rules and treat "delegate" as the default, not the
   exception.
2. **Verification turns into theater**: skipping fresh-context verification to save tokens, or writing a
   verification prompt that doesn't spell out what to check (so the agent just replies "looks fine").
   Prevention: verification dispatch should always be copied from `ops/prompt-templates.md` template #5,
   with every check spelled out item by item.
3. **The model roster rots**: there will be new models after sonnet-5, and the verification date in
   `ops/model-dispatch.md` is a freshness label, not a permanent fact. Prevention: once the verification
   date is more than a quarter old, re-verify per the health-check list in `meta/maintenance.md`. Don't just
   keep using stale info.
4. **The system bloats itself**: adding one rule per lesson learned, until three months later nobody can
   read the whole thing. Prevention: `meta/maintenance.md`'s size cap is a hard rule. Lessons go into
   `meta/lessons.md`, not into the rule body itself — a lesson only gets promoted to a rule after it repeats
   three times (and even then, ask the user first).

## Ranked honestly: which outputs I trust least

1. **The "roughly 80%" figure in the AUDIT**: a structured estimate, zero measurement behind it. The first
   thing whoever picks this up should verify: pick three old tasks, redo them with the `USAGE.md` workflow,
   and compare output quality. If the number's wrong, fix the AUDIT — don't just leave it enshrined.

   For example: if you redo one of the three tasks and the Sonnet-plus-system output is clearly weaker (not
   just different), that's evidence the 80% figure is too high — write the comparison into the AUDIT, don't
   quietly let the number stand.
2. **The "20k-token delegation cold-start" figure and other measured token values**: measured in a single
   session, in a single environment. Subscription plan changes or a different plugin mix will move these
   numbers. To re-measure in your own environment: read the session log (the token fields in
   `~/.claude/projects/<project>/<session-id>.jsonl`) or ask the user to run `/cost`.
3. **"Which version does the sonnet alias resolve to"**: as of verification, official docs list sonnet-5 as
   current and sonnet-4-6 as legacy, but this harness's alias mapping was never actually tested (the session
   at the time was running Fable, and switching models would have interrupted the work). Next time you run
   `/model`, take the opportunity to confirm this and update `ops/model-dispatch.md`.
4. **USAGE 3.4's multi-answer review phrasing**: sound in theory (divergence = where arbitration is
   needed), but never run through a full cycle in this environment. The first time you use it, log what
   actually happened (was tripling the delegation cost worth it?) in `meta/lessons.md`.

## Last thing

The system exists to save judgment, not to be worshipped. If a rule gets in your way three times running,
bring the evidence to the user and ask whether it should change.
