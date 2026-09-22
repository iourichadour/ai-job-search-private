## MODIFIED Requirements

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

## ADDED Requirements

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
