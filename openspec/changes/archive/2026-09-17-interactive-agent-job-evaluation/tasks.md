## 0. Python Tool: Evaluation Record Validation & Partial Save

- [x] 0.1 Add a new `validate_evaluation_record(record: dict) -> tuple[bool, list[str]]` function to `tools/evaluate_jobs_gemini.py` that checks:
  - **Required fields present**: title, company, skill_match, experience_level_match, company_fit, growth_potential, red_flags, overall_fit, fit_category, key_strengths, skill_gaps, red_flags_list, recommendation, reason_summary, evaluated_at, model
  - **Type checks**: skill_match/experience_level_match/company_fit/growth_potential/red_flags/overall_fit are integers; fit_category is a string; key_strengths/skill_gaps/red_flags_list are non-empty arrays; recommendation/reason_summary are non-empty strings; evaluated_at is a valid ISO 8601 timestamp; model is one of ['claude-agent-session', 'gemini-agent-session', 'antigravity-agent-session'] or a Gemini model name
  - **Range checks**: each dimension score and overall_fit are in range [0, 100]
  - **Enum checks**: fit_category is one of ['high', 'medium', 'low', 'skip']
  - Returns tuple: (is_valid: bool, errors: list of error strings)
  - Verify function catches at least: missing field, type mismatch, out-of-range int, invalid fit_category, empty array

- [x] 0.2 Add a new `check_evaluation_consistency(record: dict) -> list[str]` function (non-blocking warnings) — only called on records that already passed `validate_evaluation_record()`, so array-non-empty is not re-checked here (it's a blocking schema check, see 0.1):
  - overall_fit approximately matches weighted composite of five dimensions (tolerance ±2)
  - fit_category threshold matches overall_fit (e.g., 75 should be 'medium', not 'high')
  - evaluated_at is not in the future
  - Returns list of warning strings (empty if all checks pass)

- [x] 0.3 Modify `save_evaluations_to_files()` to implement partial-save with failure tracking:
  - Loop through each record, validate with validate_evaluation_record()
  - **Valid records**: merge into `data/inbox_queue.json` and `data/job_evaluations.json` immediately (per existing upsert-by-url logic)
  - **Invalid records**: collect in a separate list with (record, errors) tuples
  - After looping all records:
    - If invalid records exist, append them to `data/job_evaluations.failed.json` with timestamp and error details (format: `{"record": {...}, "errors": [...], "failed_at": "ISO timestamp"}`)
    - Run consistency checks on all valid records, log warnings to stderr
    - Print summary to stderr: "✓ Persisted N jobs | ✗ Failed M jobs (see data/job_evaluations.failed.json)"
  - Return True if any records were saved, False only if all records failed validation

- [x] 0.4 Ensure `data/job_evaluations.failed.json` is created if it doesn't exist and is appended to (not overwritten) on each run, preserving failure history across sessions

- [x] 0.5 Update `tools/README_EVALUATE_JOBS_GEMINI.md` to document the new partial-save behavior: schema validation (blocking), consistency checks (warnings), failed record tracking in `.failed.json`, and the follow-up skill for retrying failed evaluations

## 1. Claude Code side

- [x] 1.1 Create `.claude/agents/job-evaluator.md`, following the frontmatter/style pattern of `.claude/agents/gemini-research-expert.md` (name/description/model), with `model: haiku`, containing the scoring rubric and evaluation-record schema from `specs/job-evaluation/spec.md`; verify the file has valid frontmatter and `model: haiku`
- [x] 1.2 Update `.claude/commands/fetch-inbox.md` step 2 to the 3-step round trip (`--filter-only` export → invoke the `job-evaluator` subagent with the exported jobs and `data/profile.md`, batched as a single call → write scratch JSON from its output → `--save-evaluations`), tagging `model: "claude-agent-session"`; verify by reading the file back and confirming no reference to the old no-flag invocation remains
- [x] 1.3 Apply the same update to `.claude/commands/scan-inbox.md`; verify its content matches the fetch-inbox.md pattern
- [x] 1.4 Update `.claude/skills/fetch-inbox/SKILL.md` so it also persists structured evaluations via the round trip through the `job-evaluator` subagent (currently only summarizes fit in chat), tagging `model: "claude-agent-session"`; verify the skill's steps now include the filter/evaluate/save sequence before the summary step

## 2. Gemini CLI side

- [x] 2.1 Update `.gemini/commands/fetch-inbox.md` step 2 to the same 3-step round trip, tagging `model: "gemini-agent-session"`; verify no reference to the old no-flag invocation remains
- [x] 2.2 Apply the same update to `.gemini/commands/scan-inbox.md`
- [x] 2.3 Update `.gemini/skills/fetch-inbox/SKILL.md` to persist structured evaluations via the round trip, tagging `model: "gemini-agent-session"`
- [x] 2.4 Update `.gemini/skills/scan-inbox/SKILL.md` the same way
- [x] 2.5 Update `.gemini/GEMINI.md` step 2 (currently says "using Gemini 2.5 Flash") to describe the interactive-agent round trip as the default, with the Gemini API mode noted as fallback

## 3. Shared reference docs

- [x] 3.1 Update `prompts/scan_inbox_workflow.md` step 2 to describe the interactive-agent round trip instead of "Execute the Gemini evaluation script"
- [x] 3.2 Update `.gemini/prompts/scan_inbox_workflow.md` the same way
- [x] 3.3 Update `tools/README_EVALUATE_JOBS_GEMINI.md` to present Agent Evaluation Mode as the default for both Claude Code and Gemini CLI, document the `claude-agent-session` / `gemini-agent-session` / Gemini-model-name tagging convention, and reframe the API mode section as the fallback

## 4. Verification

- [x] 4.1 Run `python tools/evaluate_jobs_gemini.py --days 14 --filter-only` and confirm it prints the expected export JSON without requiring `GEMINI_API_KEY` to be set
- [x] 4.2 Run `/fetch-inbox` in a live Claude Code session against real Gmail data end-to-end; confirm evaluated jobs in `data/inbox_queue.json` have `status: "evaluated"` and `evaluation.model: "claude-agent-session"` (verified live: `fetch_inbox.py` polled real Gmail, `--filter-only` exported the real backlog, 6 real pending jobs were scored by the `job-evaluator` subagent and merged in — see notes on task 4.6 for scope-limiting rationale)
- [x] 4.3 Run the equivalent workflow in a live Gemini session; confirm evaluated jobs are tagged `evaluation.model: "gemini-agent-session"` (verified live: evaluated 5 real pending jobs from `data/inbox_queue.json` in-session, validated against rubric and schema, merged via `--save-evaluations`, and confirmed all 5 have `model: "gemini-agent-session"`)
- [x] 4.4 Inspect `data/job_evaluations.json` after both runs: confirm upsert-by-`url` behavior (no duplicate entries) and that pre-existing records are untouched (verified: 423 total records, 0 duplicate URLs, pre-existing 404 `Antigravity-Agent-Session` and 6 `claude-agent-session` records intact, 5 new `gemini-agent-session` records successfully added)
- [x] 4.5 Confirm `job_search_tracker.csv` submission tracking (`--track-applied`) still reads `fit_rating` correctly from a `claude-agent-session`- or `gemini-agent-session`-evaluated job (verified live against the real Dayforce job evaluated in 4.2: tracker row correctly showed `fit_rating: "81%"`; test run then cleanly reverted so no false "applied" status was left on a real job)
- [x] 4.6 During the Claude Code run in 4.2, confirm the `job-evaluator` subagent is actually invoked (visible as an Agent-tool call) to perform the scoring rather than the main session scoring inline, and that it runs on the pinned `haiku` model (confirmed: invoked via the Agent tool with `subagent_type: job-evaluator`, frontmatter pins `model: haiku`; scoped to a 6-job sample of the real backlog rather than the full 374-job/14-day filtered set, since batching an entire historical backlog into one subagent call isn't what the design's "one batched call per session" intends — full backlog catch-up is normal ongoing `/fetch-inbox` usage, not a one-time verification step)
- [x] 4.7 **Partial-save behavior test**: Create a test file `data/.test_mixed_evals.json` with both valid and invalid records:
  - 3 valid records (complete, correct types/ranges)
  - 2 invalid records (one missing 'overall_fit', one with fit_category: "excellent")
  Then run `python tools/evaluate_jobs_gemini.py --save-evaluations data/.test_mixed_evals.json` and confirm:
  - Command returns zero exit code (partial success)
  - 3 valid records are persisted to `data/inbox_queue.json` (status: "evaluated") and `data/job_evaluations.json`
  - 2 invalid records are appended to `data/job_evaluations.failed.json` with error details and timestamp
  - Stderr summary: "✓ Persisted 3 jobs | ✗ Failed 2 jobs (see data/job_evaluations.failed.json)"
  - Neither bad record corrupted the main evaluation files

- [x] 4.8 **All-invalid batch test**: Create `data/.test_all_malformed_evals.json` with only invalid records:
  - Confirm zero valid records are "persisted" status (no new entries in inbox_queue)
  - All records go to `.failed.json` with error details
  - Stderr summary reports all as failed
  - Command returns zero (no exception), since partial-save doesn't error on all-invalid — just reports them

- [x] 4.9 **Consistency checks (warnings) test**: Create `data/.test_consistency_evals.json` with valid records (schema-valid, including non-empty arrays) that have consistency issues:
  - overall_fit: 75 but consistency check computes to 62 (outside ±2 tolerance)
  - fit_category: "high" but overall_fit: 55 (should be "low")
  - evaluated_at: a timestamp in the future
  Confirm:
  - Records are still persisted (not blocked by warnings)
  - Stderr prints warnings: "Record X: overall_fit mismatch" / "Record Y: fit_category inconsistent" / "Record Z: evaluated_at in the future"
  - `.failed.json` is NOT used (these are valid enough to save; warnings are informational)
