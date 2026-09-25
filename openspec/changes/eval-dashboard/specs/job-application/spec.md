## ADDED Requirements

### Requirement: Application progress is recorded in the evaluation ledger
After writing application files for a job, `/apply` SHALL upsert `application_status: "applied"` and `application_folder` (the relative path to `private/applications/YYYY-MM_Company/`) into the matching `private/job_evaluations.json` record. If a strategy log was generated or reused as part of this run, `/apply` SHALL also upsert `strategy_path`. This upsert SHALL use the same composite-key matching and merge mechanism defined by the `job-evaluation` capability's lineage-field requirements.

#### Scenario: Ledger is updated after a successful application
- **WHEN** `/apply` completes drafting and revision for a job at "Acme Corp" and writes `cv.md`, `cover_letter.md`, `strategy.md`, and `strategy.json` to `private/applications/2026-09_Acme-Corp/`
- **THEN** the matching record in `private/job_evaluations.json` has `application_status: "applied"`, `application_folder: "private/applications/2026-09_Acme-Corp"`, and `strategy_path` set

#### Scenario: No matching evaluation record exists yet
- **WHEN** `/apply` is run on a job that was never fetched or evaluated through the existing pipeline (no record exists in `private/job_evaluations.json` for it — for example, a posting pasted directly rather than sourced from a LinkedIn/Indeed alert)
- **THEN** `/apply` writes the application files normally and does not attempt to create a partial evaluation record, since every persisted record in `private/job_evaluations.json` must satisfy the `job-evaluation` capability's required-field schema; the job simply has no lineage entry in the dashboard until (if ever) it is evaluated through the normal pipeline
- **AND** drafting is never blocked on the ledger lookup or upsert — a failure to find or update a ledger record SHALL NOT prevent `/apply` from completing and presenting the application files
