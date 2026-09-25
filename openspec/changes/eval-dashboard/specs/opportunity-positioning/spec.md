## ADDED Requirements

### Requirement: Positioning results are recorded in the evaluation ledger
Whichever orchestrator invokes `career-advisor` for a tracked job (`/apply`, `generate-application-strategy`) SHALL upsert `positioning_score` into the matching `private/job_evaluations.json` record once `career-advisor`'s output passes `evidence-verifier`. If a `strategy.json` was written as part of the same run, the orchestrator SHALL also upsert `strategy_path`. This upsert SHALL use the same composite-key matching and merge mechanism defined by the `job-evaluation` capability's lineage-field requirements, and SHALL NOT alter the record's fit-evaluation fields.

#### Scenario: Positioning score is recorded after a verified draft
- **WHEN** `career-advisor` produces a positioning report for a job and `evidence-verifier` returns PASS
- **THEN** the orchestrator upserts that job's `positioning_score` into the matching `job_evaluations.json` record

#### Scenario: career-advisor itself never writes the ledger
- **WHEN** `career-advisor` completes and presents its report
- **THEN** the ledger upsert is performed by the orchestrating skill/command that invoked it, not by `career-advisor` itself, consistent with `career-advisor` never modifying any file directly
