## Context

See proposal.md - Why. The repository maintains parallel environments for Claude Code (`.claude/`), Google Gemini CLI (`.gemini/`), and Antigravity (`.agents/`). While Claude Code delegates job evaluation to a dedicated `haiku` subagent, the Antigravity and Gemini CLI workflows were left scoring inline in the orchestrating session. Furthermore, `@google/gemini-cli` fails on startup due to an invalid `"model"` string in `.gemini/settings.json`.

## Goals / Non-Goals

**Goals:**
- Provide a dedicated `job-evaluator` subagent for Antigravity (`agy`) in `.agents/agents/job-evaluator.agent.md`.
- Pin the subagent's evaluation model to `pro` (`gemini-2.5-pro`) for maximum domain and executive nuance at modest cost (~$0.20-$0.25 per 50 jobs), with `flash` documented as an option for bulk sweeps.
- Fix `.gemini/settings.json` so `@google/gemini-cli` passes schema validation with `"name": "gemini-2.5-pro"`.
- Update `.agents/` and `.gemini/` skills and commands to delegate scoring to `job-evaluator` via `invoke_subagent` instead of scoring inline.

**Non-Goals:**
- No changes to `tools/evaluate_jobs_gemini.py` Python validation or rubric formula.
- No changes to Claude Code side (`.claude/`), which is already working cleanly with `job-evaluator.md` pinned to `haiku`.

## Decisions

1. **Pin subagent to `pro` (`gemini-2.5-pro`) rather than `flash` or `flash_lite` by default.**
   - *Rationale*: At typical alert volumes (10–30 jobs/batch), `pro` costs ~$0.05 to $0.15 per session, which is completely negligible. In return, `gemini-2.5-pro` provides superior discernment on executive title inflation, distinguishing core modern data platform leadership (Fabric, Snowflake, data mesh) from pre-sales or commercial distribution roles, and identifying subtle legacy stack red flags. `flash` remains documented as an alternative if large backlog sweeps are needed.
   - *Alternatives considered*: `flash` (very cheap, but slightly less discerning on executive subtleties), `flash_lite` (too coarse for executive role discernment).

2. **Place the Antigravity agent definition at `.agents/agents/job-evaluator.agent.md`.**
   - *Rationale*: Follows Antigravity's standard workspace agent discovery convention (`.agents/agents/*.agent.md`). Mirrors the Claude Code pattern (`.claude/agents/job-evaluator.md`).

3. **Fix `.gemini/settings.json` model schema to match `@google/gemini-cli` expectations.**
   - *Rationale*: The CLI schema requires `"model": { "name": "gemini-2.5-pro" }`. Passing a raw string causes `Expected object, received string` errors in `gemini` v0.57.0.
   - *Alternatives considered*: Deleting `settings.json` (rejected: needed for project-level tool configuration).

4. **Retain the 3-step round trip via scratch file (`data/.tmp_agent_evals.json`).**
   - *Rationale*: `--filter-only` exports jobs -> subagent scores batch -> writes scratch file -> `--save-evaluations` merges and validates. This keeps persistence strictly deterministic and validated.

## Risks / Trade-offs

- **Standalone Gemini CLI vs Antigravity runtime** → In standalone `gemini` CLI, custom subagent discovery may behave differently than inside Antigravity (`agy`).
  *Mitigation*: The skill instructions document delegating via `invoke_subagent` in Antigravity while retaining inline scoring with the configured model as a fallback in standalone Gemini CLI.
- **Model name changes over time** → Google model naming evolves (e.g. 2.5 vs 3.0).
  *Mitigation*: The subagent definition and `settings.json` specify current stable models (`gemini-2.5-flash` / `flash`), easily updated when newer versions reach GA.

## Migration Plan

1. Create `.agents/agents/job-evaluator.agent.md`.
2. Fix `.gemini/settings.json` model property.
3. Update `.agents/skills/fetch-inbox/SKILL.md`, `scan-inbox/SKILL.md`, and `.gemini/commands/`.
4. Validate live with a test batch in `agy`.
