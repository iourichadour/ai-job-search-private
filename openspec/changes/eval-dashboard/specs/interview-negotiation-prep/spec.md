## ADDED Requirements

### Requirement: Interview prep names the ledger update for the invoking session to record
`deal-architect` has no dedicated wrapper command, so it SHALL NOT write to `private/job_evaluations.json` itself, consistent with its existing behavior of never modifying any file. Instead, whenever `deal-architect` completes a three-lens simulation for a tracked job, its presented output SHALL explicitly name the ledger update the invoking session should make: upserting `interview_prep_last_run_at` (the current timestamp) into the matching `private/job_evaluations.json` record via the composite-key merge mechanism defined by the `job-evaluation` capability. This is an advisory instruction, not a guarantee — the dashboard SHALL treat `interview_prep_last_run_at` as best-effort and SHALL NOT imply that its absence means prep never happened.

#### Scenario: deal-architect names the ledger update in its output
- **WHEN** `deal-architect` completes a three-lens interview simulation for a tracked job
- **THEN** its presented report includes an explicit note that the invoking session should record `interview_prep_last_run_at` for that job

#### Scenario: Absence of the timestamp is not treated as "never prepped"
- **WHEN** the dashboard displays a job with no `interview_prep_last_run_at` set
- **THEN** it presents this as "no recorded prep" rather than asserting that interview prep was never done for that job
