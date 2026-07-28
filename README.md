# upward-mobility

**Goal: make a lower-tier model smarter.**

A capable model already carries the reflexes that make a long session go well — it verifies before claiming done, it doesn't re-read what it already knows, it notices when the direction is wrong and backs out instead of stacking another fix. A cheaper model has the raw ability to do all of that; what it lacks is the habit of doing it unprompted, and the habit is what decays first over a long run.

This repo externalizes those reflexes into durable operating rules a cheaper model can follow for hours without a human re-explaining them. The rules are the deliverable. Everything else here is the apparatus for finding out which rules actually earn their place.

> Older documents in `docs/` and `project/` frame this differently — as "if the top-tier model isn't available or affordable, can a cheaper one reach parity on its own?" That framing has been retired. The target isn't parity with a specific model; it's raising the floor of what a lower-tier model does on a long, unsupervised run.

## What's here

| Path | What it is |
|---|---|
| `plugin/upward/` | The plugin (0.6.0). A small always-on core injected at session start, plus six on-demand skills holding the detailed playbooks. |
| `plugin/upward-stats/` | Standalone token-usage tracker. A `Stop`/`SubagentStop` hook logs per-prompt (or per-call) usage to `.upward/UPWARD-STATS.md`. Works with or without `upward`. |
| `plugin/.claude-plugin/marketplace.json` | Marketplace manifest listing both plugins. |
| `project/` | The original cross-project "ops template pack" — the same discipline as plain Markdown files you copy into a repo, for harnesses that can't load a plugin. Predates the plugin. |
| `docs/` | Lab notes: dispatch mechanics, cost breakdowns, model comparisons, and the lessons that produced specific rule changes. |

## Install

```
/plugin marketplace add amdslancelot/upward-mobility --path plugin
/plugin install upward@upward-mobility
```

Or from a local clone:

```
/plugin marketplace add /path/to/upward-mobility/plugin
/plugin install upward@upward-mobility
```

Then `/reload-plugins` (or restart Claude Code) and check `/plugin` — `upward` should show as installed and enabled. `upward-stats` installs the same way and is independent of `upward`.

Per-plugin detail lives in `plugin/upward/README.md` and `plugin/upward-stats/README.md`.

## What the rules actually say

The always-on core (`plugin/upward/core.md`, ~1.3K tokens) is deliberately small — reflexes and a router, not the whole playbook:

- **Verification isn't self-verification.** A completion claim needs execution evidence — build, test, real run, read-back. The final verdict gets exactly one independent pass from a fresh context, never from whoever did the work, and authoring the plan counts as having done the work.
- **The warm main context is the only executor.** Subagents read, run, and report; they never write project files. Every measured exception cost more than it saved — per-item builder dispatch lost to cold starts, and a three-builder split shipped its fatal defects exactly at the seams between builders.
- **Bookkeeping never travels alone.** A check-off or log line rides inside the next real-work message. A run that ticked its boxes in standalone calls paid ~90K of context re-reading per tick.
- **Quiet gates.** Pipe verbose output to a file, judge by exit code, read the tail while green — and read the whole log the moment it fails.
- **Fetched material goes to a file.** Only a short digest stays in the conversation. A run that carried 45K of early research to the end spent a third of its tokens re-reading it.

The six skills (`upward-ops-plan`, `-dispatch`, `-review`, `-judge`, `upward-debug`, `upward-harness-diagnose`) load on demand via the Skill tool, so the detailed playbook only enters context when the situation calls for it.

## What this buys, and what it doesn't

Worth being direct about, since the repo contains enough measurement to say:

**Solved:** the cost mechanics. The current chassis runs at a predictable per-call rate with no cache-miss lottery, and the always-on text costs about a cent over a long run. The rules that cut re-reads (quiet gates, digest-don't-carry, bookkeeping ride-along) more than pay for the rules that don't.

**Not solved:** quality. Across a long benchmark series, no generic-discipline variant reliably produced a *delivering* build on its own. The runs that did deliver had domain-specific defect memory available to them — which is exactly what a general-purpose plugin must not ship, because it makes the plugin useless for building anything else. Project-side defect memory that the plugin reads when present is the open design question.

So: adopt this for the cost structure and the long-run discipline. Don't adopt it expecting it to substitute for knowing your own domain's failure modes.

## Notes

The skills carry date-stamped sections that are specific to the environment they were written in — model aliases, available agent types, installed review tools. If you port this to another repo or harness, re-verify those rather than trusting the stamped values; each skill says where to look.

`upward-checklist` is a preserved branch holding the 0.4.5 rule set, the last version that shipped an app-type-specific defect checklist inside the plugin. It's kept for reference, not for use.
