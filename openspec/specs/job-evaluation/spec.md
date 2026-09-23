# job-evaluation Specification

## Purpose
Defines how pending jobs in `data/inbox_queue.json` get scored for fit against the candidate profile and persisted as structured evaluation records, across all supported evaluators (interactive agent sessions and the Gemini API fallback).

## Requirements

### Requirement: Interactive-agent evaluation is the primary path
The system SHALL support evaluating pending jobs from within an interactive coding-agent session (Claude Code or Gemini CLI) without requiring an external LLM API key, and this SHALL be the default evaluation path invoked by the inbox-scanning commands and skills in both `.claude/` and `.gemini/`.

#### Scenario: Evaluating pending jobs in an interactive session
- **WHEN** a user runs the `/fetch-inbox` workflow inside an interactive Claude Code or Gemini CLI session
- **THEN** the workflow exports unevaluated jobs from `data/inbox_queue.json`, the interactive agent scores each job itself against `data/profile.md`, and the resulting evaluations are persisted back into `data/inbox_queue.json` and `data/job_evaluations.json` without any call to the Gemini API

### Requirement: Evaluation scoring rubric and record schema
The system SHALL score each job across five dimensions — `skill_match`, `experience_level_match`, `company_fit`, `growth_potential`, `red_flags` (each 0-100) — and compute `overall_fit` as a weighted composite (skills 30%, experience 25%, company 20%, growth 15%, red_flags −10%), assigning `fit_category` from `overall_fit` using thresholds: `high` (80+), `medium` (60-79), `low` (40-59), `skip` (<40). Every evaluation record SHALL include `title`, `company`, the five dimension scores, `overall_fit`, `fit_category`, `key_strengths`, `skill_gaps`, `red_flags_list`, `recommendation`, `reason_summary`, `url`, `evaluated_at`, and `model`, regardless of which evaluator produced it.

#### Scenario: Overall fit computed from weighted dimensions
- **WHEN** an evaluator scores a job's five dimensions
- **THEN** `overall_fit` is computed using the fixed weighting (skills 30%, experience 25%, company 20%, growth 15%, red_flags −10%) and is stored as an integer between 0 and 100

#### Scenario: Fit category assigned from thresholds
- **WHEN** `overall_fit` for a job is computed
- **THEN** `fit_category` is set to `high` for 80+, `medium` for 60-79, `low` for 40-59, or `skip` for below 40

### Requirement: Evaluations are tagged by evaluator provenance
Each persisted evaluation record SHALL identify which evaluator produced it via the `model` field: `claude-agent-session` when scored by an interactive Claude Code session, `gemini-agent-session` when scored by an interactive Gemini CLI session, `antigravity-agent-session` when scored by an interactive Antigravity agent session, or the underlying Gemini model name (e.g. `gemini-2.5-flash`) when scored via the Gemini API fallback.

#### Scenario: Claude Code session evaluation is tagged
- **WHEN** a job is evaluated inside a Claude Code session using the interactive-agent path
- **THEN** the saved evaluation record's `model` field is `claude-agent-session`

#### Scenario: Gemini CLI session evaluation is tagged
- **WHEN** a job is evaluated inside a Gemini CLI session using the interactive-agent path
- **THEN** the saved evaluation record's `model` field is `gemini-agent-session`

#### Scenario: Antigravity agent session evaluation is tagged
- **WHEN** a job is evaluated inside an Antigravity agent session or by its spawned `job-evaluator` subagents
- **THEN** the saved evaluation record's `model` field is `antigravity-agent-session`

### Requirement: Gemini API evaluation remains available as a fallback
The system SHALL retain the existing Gemini API evaluation mode (requiring `GEMINI_API_KEY`) as a fallback evaluation path, unchanged in behavior, for use when interactive-agent evaluation is not available or not desired.

#### Scenario: Falling back to the Gemini API path
- **WHEN** a user or script invokes job evaluation without going through the interactive-agent filter/save round trip (i.e. the existing no-flag invocation)
- **THEN** jobs are evaluated via the Gemini API exactly as before, with evaluation records tagged with the Gemini model name

### Requirement: Evaluation results are persisted only via merge
The system SHALL persist evaluation results into `data/inbox_queue.json` and `data/job_evaluations.json` only through the existing merge mechanism, which upserts by `url` (falling back to `title`+`company`) and marks matched jobs as `status: "evaluated"`. Evaluation results SHALL NOT be written by directly overwriting either file.

#### Scenario: Merging new evaluations preserves existing records
- **WHEN** a new batch of evaluation records is saved
- **THEN** jobs already present in `data/job_evaluations.json` are updated in place if re-evaluated, new jobs are appended, and no duplicate entries are created for the same `url`

### Requirement: Evaluation records are validated before persistence
The system SHALL validate every evaluation record against a schema before persisting it to `data/inbox_queue.json` or `data/job_evaluations.json`. Validation is performed per record, not per batch: records that pass validation SHALL be persisted immediately via the merge mechanism, even when other records in the same batch fail. Records that fail validation SHALL NOT be persisted to `data/inbox_queue.json` or `data/job_evaluations.json`; instead they SHALL be appended, together with clear error messages identifying which field(s) failed and why, to `data/job_evaluations.failed.json` for later review or retry.

#### Evaluation Record JSON Schema

Each evaluation record MUST have ALL of the following fields with the specified types and constraints:

```json
{
  "title": "string (required, non-empty)",
  "company": "string (required, non-empty)",
  "url": "string (required if available, used for deduplication)",
  "skill_match": "integer, 0-100 (required)",
  "experience_level_match": "integer, 0-100 (required)",
  "company_fit": "integer, 0-100 (required)",
  "growth_potential": "integer, 0-100 (required)",
  "red_flags": "integer, 0-100 (required)",
  "overall_fit": "integer, 0-100 (required, computed from weighted dimensions, clamped to [0, 100])",
  "fit_category": "string, one of ['high', 'medium', 'low', 'skip'] (required)",
  "key_strengths": "array of strings (required, non-empty)",
  "skill_gaps": "array of strings (required, non-empty)",
  "red_flags_list": "array of strings (required, non-empty)",
  "recommendation": "string (required, non-empty)",
  "reason_summary": "string (required, non-empty)",
  "evaluated_at": "ISO 8601 timestamp string (required)",
  "model": "string, one of ['claude-agent-session', 'gemini-agent-session', 'antigravity-agent-session', or Gemini model name] (required)"
}
```

#### Scenario: Missing required fields are rejected
- **WHEN** an evaluator produces a record missing any required field
- **THEN** that record is rejected and appended to `data/job_evaluations.failed.json` with an error message naming the missing field(s), while other valid records in the same batch are still persisted to `data/inbox_queue.json` and `data/job_evaluations.json`

#### Scenario: Type mismatches are rejected
- **WHEN** an evaluator produces a record where `overall_fit` is a string (e.g. `"85"`) instead of an integer
- **THEN** that record is rejected and appended to `data/job_evaluations.failed.json` with an error message describing the type mismatch, while other valid records in the same batch are still persisted

#### Scenario: Out-of-range values are rejected
- **WHEN** an evaluator produces `skill_match: 150` or `overall_fit: 120`
- **THEN** that record is rejected and appended to `data/job_evaluations.failed.json` with an error message indicating the value is outside the valid 0-100 range, while other valid records in the same batch are still persisted

#### Scenario: Negative overall_fit from red flag deduction is auto-clamped
- **WHEN** an evaluator computes `overall_fit` below 0 due to red flag penalties (e.g. `overall_fit: -10`) on an irrelevant posting
- **THEN** the validation and persistence pipeline automatically clamps the score to `0` and assigns `fit_category: "skip"`, allowing the record to be cleanly persisted without failure

#### Scenario: Invalid fit_category is rejected
- **WHEN** an evaluator produces `fit_category: "excellent"` (not one of the four allowed values)
- **THEN** that record is rejected and appended to `data/job_evaluations.failed.json` with an error message listing the allowed values, while other valid records in the same batch are still persisted

#### Scenario: Valid records persist despite other records failing in the same batch
- **WHEN** a batch of evaluation records contains a mix of valid and invalid records
- **THEN** all valid records are persisted to `data/inbox_queue.json` (status: `evaluated`) and `data/job_evaluations.json`, all invalid records are appended to `data/job_evaluations.failed.json`, and a summary reporting counts of persisted and failed records is printed to stderr

### Requirement: Additional validation checks (recommended beyond schema validation)

The following validation checks are RECOMMENDED to catch subtle evaluation errors. These are distinct from the array-non-empty check on `key_strengths`/`skill_gaps`/`red_flags_list`, which is part of the blocking schema validation above, not a warning-level check.

1. **Overall fit consistency check**: Verify that `overall_fit` is approximately equal to the weighted composite of the five dimension scores. Tolerating ±2 points for rounding, flag if the computed value differs materially (e.g., `overall_fit: 85` but weighted dimensions compute to 62).
2. **Fit category consistency check**: Verify that `fit_category` matches the thresholds for the given `overall_fit`. Flag mismatches (e.g., `overall_fit: 75` but `fit_category: "high"`).
3. **Timestamp validity check**: Verify that `evaluated_at` parses as a valid ISO 8601 timestamp and is not a future date.
4. **Model tag validity check**: Verify that the `model` field is one of the expected values for the current evaluation run (e.g., during Claude Code runs, all records should be tagged `claude-agent-session`).

These checks are defensive and help catch evaluator hallucinations or instruction misunderstandings. Failure on any of these RECOMMENDED checks SHOULD warn but MAY allow persistence with a log message (not blocking), unlike schema validation (which MUST block).

#### Scenario: Consistency warnings are logged without blocking persistence
- **WHEN** an evaluation record passes schema validation but has a consistency mismatch (e.g. `overall_fit` deviates from weighted dimensions, `fit_category` threshold mismatch, or future `evaluated_at`)
- **THEN** a warning message is logged to stderr, the record is NOT added to `data/job_evaluations.failed.json`, and it is successfully persisted to `data/inbox_queue.json` and `data/job_evaluations.json`

### Requirement: Automated batch preparation orchestration
The system SHALL support partitioning pending unevaluated jobs from `data/inbox_queue.json` into configured batch files on disk via a CLI command, enabling efficient subagent evaluation without ad-hoc chunking scripts.

#### Scenario: Preparing batches with custom batch size
- **WHEN** a user runs `python tools/evaluate_jobs_gemini.py --prepare-batches --days 30 --batch-size 60`
- **THEN** the system filters pending jobs from the past 30 days, splits them into slices of up to 60 jobs each, writes them to `data/eval_batches/batch_XX.json`, and outputs the batch manifest with file paths

### Requirement: Multi-file and glob evaluation persistence
The system SHALL support passing file globs or directories to `--save-evaluations` so that multiple completed subagent evaluation files can be merged and validated in a single execution.

#### Scenario: Saving evaluations from glob pattern
- **WHEN** a user or agent runs `python tools/evaluate_jobs_gemini.py --save-evaluations "data/eval_batches/*.evaluated.json"`
- **THEN** the system loads and merges evaluation records across all matching files, performing unified validation and deduplication into `data/job_evaluations.json` and `data/inbox_queue.json`

### Requirement: Backlog continuation without silent date cutoff
The system SHALL export all pending unevaluated jobs across all dates when `--filter-only` or `--prepare-batches` is invoked without explicit `--days`, `--start-date`, or `--end-date` flags, rather than silently injecting a 14-day cutoff. Explicit date filtering SHALL apply only when date parameters are explicitly provided by the user or agent.

#### Scenario: Exporting unevaluated backlog defaults to all dates
- **WHEN** a user or agent runs `python tools/evaluate_jobs_gemini.py --filter-only` without specifying `--days` or `--start-date`
- **THEN** the system exports all jobs in `data/inbox_queue.json` whose evaluation is not yet complete (`status: "pending_evaluation"` or missing evaluation), regardless of how many days ago they were fetched

#### Scenario: Explicit date filtering respects user parameter
- **WHEN** a user or agent specifies `--days 30` or `--days 14`
- **THEN** the system restricts the candidate jobs to those fetched within the specified number of days
