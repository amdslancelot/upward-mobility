# Lesson 2026-07-13: Gelp benchmark — the scaffold Goodharted itself

> **Status (updated 2026-07-27): the scores below are superseded; the mechanism is not.**
>
> **Superseded — the numbers.** Every score here was produced on the v1 craft
> scale at *shallow* review depth (source read, artifact never booted), one run
> per condition. The same-standard re-grade of 2026-07-19 measured what that
> costs: on the same artifact, shallow and live-demonstrated scores diverged by
> up to **5.6 points**, and not uniformly — a shallow board mostly ranks how
> thoroughly a run polished its *source-visible* defects while leaving runtime
> ones intact. Treat the 7.0 / 7.7 / 4.5 / 5.8 / 9.0 ordering below as
> unreliable, including the "bare Fable shipped the only production-viable build"
> claim.
>
> **Stands — the mechanism.** Self-authored acceptance criteria inheriting their
> author's blind spots was confirmed, then generalised. The Known-killers
> checklist that later versions leaned on turned out to be distilled from defects
> that had shipped in *earlier rounds of this same fixed task* — the scaffold
> memorising its own benchmark, which raised the score while narrowing the plugin
> to one app shape and inflating its cost. The "Testable prediction" below became
> a standing protocol rule, and a held-out second task was added as the only
> check that detects this class of failure.
>
> **Provenance.** This experiment was the cross-sectional first cut: one plugin
> version, five parallel conditions, one day. It later grew into a fifteen-round
> longitudinal lab in the sibling `token_test3` repo, where the plugin version —
> not the model — is the variable. The Opus+scaffold session here appears to be
> that lab's Round 1 (matching USD 5.77 and legacy craft 7.0).
>
> **Read next:** `token_test3/docs/benchmark-validity.md` — the five ways this
> style of benchmark invalidates itself and which of them can be repaired after
> the fact; `token_test3/docs/UPWARD-ROUNDS-STORY.md` — the fifteen-round
> narrative and the re-grade table.

## Verdict

Five fresh headless sessions built the same deploy-ready three-layer app (Next.js + k8s + Terraform). Dollar cost was flat across every condition ($5.77–$6.89), but shipped quality was not: **both ops-plan-scaffolded runs ranked below their bare counterparts** in a side-by-side code review (Opus 7.0 scaffolded vs 7.7 bare; Sonnet 4.5 scaffolded vs 5.8 bare). Bare Fable shipped the only production-viable build (9.0/10). The scaffold's extra raw tokens (3–4x) were almost entirely cheap cache reads, so cost is no longer the concern — correctness is.

## Mechanism: process substituted for judgment (Goodhart's law inside the agent)

1. **Self-authored acceptance criteria inherit the author's misunderstanding.** The Sonnet-scaffolded run believed Takeout "Saved" exports are GeoJSON, so it wrote a GeoJSON parser, a GeoJSON fixture, and a criterion of "selfcheck passes against the fixture." Every box went green; a real Takeout zip imports nothing. The fixture could only confirm the belief, never test it.
2. **Verification narrowed to confirming the checklist.** The Opus-scaffolded run performed a ceremonially rigorous clean-room rebuild — and still shipped an ingress hardcoded to `gelp.example.com`, because nobody asked "would traffic actually reach the app?" The process specified what to check, and the model stopped checking beyond it.
3. **The bare runs answered "is it done?" with judgment applied to reality.** Bare Fable booted the production build and threw real HTTP requests at it unprompted; bare Opus re-verified on its own initiative. Both outscored their scaffolded twins.

## Caveat

One run per condition. This is a strong hypothesis the pattern suggests, not a proven law.

## Testable prediction

Scaffolds should help when acceptance criteria come from **outside the run** (a real spec, real sample data, an independent author) and hurt when the run authors its own, because self-authored criteria cannot see their author's blind spots.

## Rules changed in response (plugin skills only; `project/ops/` mirrors intentionally not yet synced — a later pass owes them the same changes)

- `plugin/upward/skills/upward-ops-plan/SKILL.md`: new "Ground the criteria outside the run" section (external evidence rule, fixture provenance rule, mandatory consumer-seat reality check as the final plan task), plus template and design-guards updates.
- `plugin/upward/skills/upward-ops-review/SKILL.md`: done rubric grew a fourth criterion (self-authored criteria are a floor, not the definition of done); "run for real" now means from the consumer's seat; a required open-ended hunt pass was added.
- `plugin/upward/skills/upward-ops-dispatch/SKILL.md`: new "Reality check (consumer-seat smoke)" review type; review prompts must attach the original user request verbatim and declare the acceptance criteria suspect; template #5 updated to match.
- `plugin/upward/core.md`: deliberately unchanged (always-on token cost).
