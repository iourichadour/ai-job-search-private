## Why

In `interactive-agent-job-evaluation`, evaluation in Claude Code was delegated to a dedicated subagent (`.claude/agents/job-evaluator.md`) pinned to `haiku` to keep evaluation costs low and avoid consuming the main session's context. On the Google Gemini / Antigravity (`agy`) side, evaluation was left running inline in the main session, which wastes interactive session context and burns quota on higher-tier models (e.g. Gemini 3.8 / 2.5 Pro). Furthermore, `.gemini/settings.json` has an invalid string schema for the `model` key that causes `@google/gemini-cli` to fail configuration validation.

Introducing a dedicated `job-evaluator` subagent for Antigravity pinned to `pro` (`gemini-2.5-pro`), fixing the `.gemini/settings.json` schema, and updating the `.agents/` and `.gemini/` skills resolves this asymmetry. For low-to-medium job volume, `pro` provides maximum reasoning quality and executive nuance for distinguishing strategic platform leadership from sales roles, while costing only ~$0.20-$0.25 per 50 jobs with zero main-session context pollution.

## What Changes

- **Define Antigravity Subagent**: Create `.agents/agents/job-evaluator.agent.md` configured for the `agy` runtime, pinned to `Model: pro` (gemini-2.5-pro, with `flash` documented as alternative), containing the fixed 5-dimension rubric, formula, and output schema.
- **Fix Gemini CLI Configuration Schema**: Correct `.gemini/settings.json` so `"model"` is an object (`"model": { "name": "gemini-2.5-pro" }`), satisfying `@google/gemini-cli`'s schema validator.
- **Update Antigravity & Gemini Skills**: Update `.agents/skills/fetch-inbox/SKILL.md`, `.agents/skills/scan-inbox/SKILL.md`, and `.gemini/commands/fetch-inbox.md` to instruct the orchestrating agent to delegate scoring to `job-evaluator` via `invoke_subagent` (model: `pro`) rather than scoring inline.
- **Provenance Tagging**: Confirm Antigravity evaluations are tagged `"model": "antigravity-agent-session"`.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `job-evaluation`: Clarify and extend evaluator provenance to include `antigravity-agent-session` when evaluated in Antigravity (`agy`), and specify that interactive agent runtimes delegate evaluation to dedicated subagents pinned to specialized evaluator models (`haiku` in Claude Code, `pro` in Antigravity).

## Impact

- **Affected files**:
  - `.agents/agents/job-evaluator.agent.md` (new)
  - `.gemini/settings.json` (modified)
  - `.agents/skills/fetch-inbox/SKILL.md` (modified)
  - `.agents/skills/scan-inbox/SKILL.md` (modified)
  - `.gemini/commands/fetch-inbox.md` (modified)
  - `.gemini/commands/scan-inbox.md` (modified)
  - `.gemini/skills/fetch-inbox/SKILL.md` (modified)
  - `.gemini/skills/scan-inbox/SKILL.md` (modified)
- **APIs & dependencies**: No external dependencies added. Uses existing `agy` `invoke_subagent` and `tools/evaluate_jobs_gemini.py` validation.
