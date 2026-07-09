# Model dispatch discipline

> Reader: the main-conversation model, at any tier. Goal: let the cheaper model run the daily grind, and spend the pricier model only on judgment calls.
> The "verified available resources" section must be re-verified and re-dated whenever you adopt this file. Don't just carry over the template's stale values.

## Verified available resources (verified 2026-07-07 against official docs — reverify before use if this looks stale)

- Switch model in the main conversation: `/model <alias>`. Aliases: haiku / sonnet / opus / fable. Capability/cost ordering: haiku < sonnet < opus < fable.
- Current model IDs (2026-07-07, platform.claude.com models overview):
  - Current: claude-haiku-4-5-20251001, claude-opus-4-8, claude-fable-5.
  - Legacy: claude-sonnet-4-6. Official docs list the current latest Sonnet as claude-sonnet-5.
  - Which version the `sonnet` alias actually maps to in your harness hasn't been confirmed per-environment. Check the `/model` UI, don't carry over this line as-is.
- The Agent tool's `model` parameter accepts the aliases above (confirmed in the sub-agents official docs).
- Effort: the Agent tool call itself has no effort parameter. Effort can only be set via `effort: low|medium|high|xhigh|max` in `.claude/agents/*.md` frontmatter. Sonnet 4.6 / Opus 4.6 have no xhigh; Fable 5, Sonnet 5, and Opus 4.8/4.7 have the full five levels (verified 2026-07-07 against the model-config official docs).
- Thinking controls: `alwaysThinkingEnabled` in settings.json, the `MAX_THINKING_TOKENS` env var (Fable 5 can't turn thinking off).
- Agent types specific to this environment (confirmed present by testing, 2026-07-07): caveman:cavecrew-investigator / cavecrew-builder / cavecrew-reviewer (compressed output saves main-context tokens). Porting to an environment without the caveman plugin installed? Substitute Explore / general-purpose.

## Hard rule: the commander doesn't descend

The main conversation does not do: bulk file reading, scanning the repo, checking the web, batch file edits, running verification. All of that gets dispatched to a subagent — the main conversation only receives conclusions. The main conversation only does: breaking down tasks, making judgment calls, synthesizing conclusions, and talking to the user.

## Delegation reference table

| Task | agent type | model | Rationale |
|---|---|---|---|
| Find a definition/call site/file location | caveman:cavecrew-investigator (Explore if unavailable) | haiku | pure retrieval |
| Broad search, unsure where the thing lives | Explore | sonnet | needs a bit of reasoning to pick a path |
| Mechanical edit to 1-2 files | caveman:cavecrew-builder (general-purpose if unavailable) | sonnet | scope known, just execute |
| Cross-file implementation, new feature | general-purpose | sonnet | needs comprehension + implementation |
| Diff review | `/code-review` skill or caveman:cavecrew-reviewer (general-purpose if unavailable) | sonnet | one finding per line |
| Architectural tradeoffs, decomposing an ambiguous requirement | the main conversation itself, or a Plan agent | opus | this is where quality drops if you cheap out on the model |
| Verifying someone else's output | general-purpose (freshly opened, never the one that did the work) | haiku/sonnet | see "verification isn't self-verification" |

## The three required elements of a delegation brief

Every dispatch needs all three. Missing one means don't dispatch.

1. **Goal and motivation**: what to do, and why. The subagent doesn't have your conversation's context — one sentence of motivation heads off half of all misunderstandings.
2. **Acceptance criteria**: a judgable completion standard ("test X passes," "report includes file:line"), not "do it well."
3. **Report format**: the subagent reports only conclusions and `file:line`. Long output (>50 lines) goes to a file; return the path. Full source dumps and complete logs are never allowed to be pasted back.

Good: "Repo is at `/x`, a CLI for Y. Add a `--json` flag to `list`. Done when `list --json` emits valid JSON and existing tests pass. Report changed files at file:line + how you verified."
Bad: "Add a `--json` flag to the list command." No motivation, no judgable done, no report format — the subagent guesses at all three and hands back something you can't check.

Templates are in `ops/prompt-templates.md`. When delegating a "paste content into a file" task: wrap the content boundary in a code fence and state explicitly that the fence itself isn't content, and add "grep for the boundary marker in the target file returns 0 hits" to the acceptance criteria. Hard-won lesson: builders will paste the delimiter markers straight into the file.

## Escalation ladder

- **haiku fails once** → re-dispatch the same task to sonnet, with the error output attached to the prompt.
- **sonnet fails the same subtask twice in a row** → escalate to opus with the full failure trail attached (both prompts + both error outputs). Escalating without the trail is just re-rolling the dice.
- **Once opus cracks the pattern** → turn the solution into explicit steps and hand it back down to sonnet/haiku for batch application.
- **Rule out environment/dependency root causes before escalating**: escalating the model cannot fix a broken environment (version mismatch, stale build, missing dependency) — opus gets stuck on these too. If an error is being stubborn, run the checklist in `ops/harness-diagnosis.md`#5 first, then decide whether to escalate.
- **Max two retry rounds on the same thing** (escalation included). A third round isn't "keep trying," it's "change course or ask the user" (rubric in `ops/judgment-rubrics.md`).

## Verification isn't self-verification

Whoever did the work doesn't verify their own output. Verification always goes to a freshly-opened subagent (general-purpose, never SendMessage to continue the one that did the work — shortened to "fresh-context" below):

- **Files**: read-back. Dispatch haiku to read the file and report: does it exist? Does it cover X/Y/Z? Any broken or missing sentences?
- **Code**: run the tests or run it for real. "Looks right" isn't acceptable.
- **High-risk judgment calls**: get a second opinion. Dispatch a separate agent to independently answer the same question and compare where they diverge, or run multiple answers through a reviewer and pick the best.

## Cost instincts

For the moments you're unsure whether dispatching is worth it:

- Dispatch has a fixed cost of roughly 20k subagent tokens (cold start: loading the system prompt, reading files to rebuild context, multiple execution rounds). The rubric is the task's **number of execution rounds**, not its difficulty.
  - ≥3-4 rounds of tool calls, or needing to swallow a lot of raw material → dispatch, it pays off.
  - A one-liner whose answer is already sitting in the main conversation's context → don't dispatch, just answer.
- Write the delegation prompt with the full background it needs. Don't make it re-discover what you already know.
- Don't open a new agent for every small follow-up question in a row: use SendMessage to continue the same agent (keeps context, saves the cold start).
