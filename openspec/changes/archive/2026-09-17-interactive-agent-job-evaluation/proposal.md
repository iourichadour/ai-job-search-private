## Why

Job evaluation currently defaults to calling the Gemini API (`python tools/evaluate_jobs_gemini.py` with no flags) from every inbox-scanning entry point in both the Claude Code and Gemini CLI sides of this repo. This requires a `GEMINI_API_KEY` and has been unreliable for the user (Gemini 2.5 had problems running). The user is on a Claude Pro plan and does not process high volumes of applications, so there is no need for unattended/batch API evaluation — evaluation should happen live, in whichever interactive coding-agent session (Claude Code or Google's Gemini CLI) is already running against this repo. `tools/evaluate_jobs_gemini.py` already ships an agent-mode round trip (`--filter-only` / `--save-evaluations`) built for exactly this, but no command or skill in the repo uses it yet — every entry point still calls the API path.

## What Changes

- Every job-evaluation entry point on both the Claude Code side (`.claude/commands/fetch-inbox.md`, `.claude/commands/scan-inbox.md`, `.claude/skills/fetch-inbox/SKILL.md`) and the Gemini CLI side (`.gemini/commands/fetch-inbox.md`, `.gemini/commands/scan-inbox.md`, `.gemini/skills/fetch-inbox/SKILL.md`, `.gemini/skills/scan-inbox/SKILL.md`, `.gemini/GEMINI.md`) switches from calling `python tools/evaluate_jobs_gemini.py` (no flags = Gemini API mode) to a 3-step interactive-agent round trip:
  1. `python tools/evaluate_jobs_gemini.py --days 14 --filter-only` to export unevaluated jobs.
  2. The exported jobs are scored against `data/profile.md` using the existing 5-dimension rubric, producing the same evaluation JSON schema already used in `data/job_evaluations.json`. On the Claude Code side, scoring is delegated to a new dedicated subagent, `.claude/agents/job-evaluator.md` (pinned `model: haiku`), invoked by the command/skill rather than done inline in the main session. On the Gemini CLI side, scoring happens inline in the CLI session itself, using whatever model `.gemini/settings.json` specifies — Gemini CLI has no equivalent per-task model-pinning mechanism in this repo.
  3. The agent writes its evaluations to a scratch JSON file and runs `python tools/evaluate_jobs_gemini.py --save-evaluations <path>` to merge them back into `data/inbox_queue.json` and `data/job_evaluations.json`.
- Evaluations are tagged by provenance: `"model": "claude-agent-session"` when produced in Claude Code, `"model": "gemini-agent-session"` when produced in Gemini CLI — distinct from the existing `"gemini-2.5-flash"` API tag.
- Shared reference docs (`prompts/scan_inbox_workflow.md`, `.gemini/prompts/scan_inbox_workflow.md`, `tools/README_EVALUATE_JOBS_GEMINI.md`) are updated to describe interactive-agent evaluation as the default path for both agents and document the new model tags.
- The existing Gemini API mode (`evaluate_job_api()`, `GEMINI_API_KEY`, the no-flag CLI path in `tools/evaluate_jobs_gemini.py`) is kept **completely unchanged** and documented as a fallback (e.g. for headless/unattended runs) — not removed, not the default anymore.
- No changes to `tools/evaluate_jobs_gemini.py` itself, and no changes to the `data/inbox_queue.json` / `data/job_evaluations.json` schemas — `save_evaluations_to_files()`'s existing upsert-by-url logic is reused as-is.

## Capabilities

### New Capabilities
- `job-evaluation`: How pending jobs in `data/inbox_queue.json` get scored against `data/profile.md` and persisted to `data/inbox_queue.json` / `data/job_evaluations.json` — covering the interactive-agent evaluation path (primary, for both Claude Code and Gemini CLI sessions) and the Gemini API path (fallback), the shared scoring rubric, and the evaluation-record schema/provenance tagging.

### Modified Capabilities
(none — no existing `openspec/specs/` capabilities exist yet in this repo)

## Impact

- **Affected files**: `.claude/commands/fetch-inbox.md`, `.claude/commands/scan-inbox.md`, `.claude/skills/fetch-inbox/SKILL.md`, `.gemini/commands/fetch-inbox.md`, `.gemini/commands/scan-inbox.md`, `.gemini/skills/fetch-inbox/SKILL.md`, `.gemini/skills/scan-inbox/SKILL.md`, `.gemini/GEMINI.md`, `prompts/scan_inbox_workflow.md`, `.gemini/prompts/scan_inbox_workflow.md`, `tools/README_EVALUATE_JOBS_GEMINI.md`, plus one new file: `.claude/agents/job-evaluator.md` (the pinned-model scoring subagent). All are markdown/prompt wiring changes; no Python source changes.
- **Downstream consumers to keep working unchanged**: `job_search_tracker.csv`'s `fit_rating` column (populated from `evaluation.overall_fit` via `track_submission()`) and the `upskill` skill's gap-weighting math, both of which depend on `overall_fit` remaining a 0-100 int and `fit_category` remaining one of `high`/`medium`/`low`/`skip`, regardless of which agent or mode produced the evaluation.
- **No new dependencies**: reuses the existing `--filter-only` / `--save-evaluations` CLI flags and `save_evaluations_to_files()` merge logic already present in `tools/evaluate_jobs_gemini.py`.
