## ADDED Requirements

### Requirement: Evaluation records carry optional lineage fields
The persisted evaluation record schema (`private/job_evaluations.json`) SHALL support the following optional fields in addition to its required evaluator-output fields: `application_status` (string, one of `applied`, `interviewing`, `final_round`, `offer`, `rejected`, `withdrawn`), `application_folder` (string, relative path), `strategy_path` (string, relative path), `positioning_score` (integer 0-100), `interview_prep_last_run_at` (ISO 8601 timestamp string). None of these fields are required for a record to validate — a record with none of them present remains a valid, unapplied evaluation.

#### Scenario: A record with no lineage fields is still valid
- **WHEN** an evaluation record contains only the required evaluator-output fields and none of the optional lineage fields
- **THEN** the record passes schema validation exactly as it does today

#### Scenario: A record with lineage fields is still valid
- **WHEN** an evaluation record contains all required evaluator-output fields plus `application_status: "applied"` and `application_folder: "private/applications/2026-08_Trace3"`
- **THEN** the record passes schema validation and both lineage fields are preserved on persistence

### Requirement: Lineage fields are upserted via the same merge mechanism, keyed by composite job identity
The system SHALL persist updates to a record's lineage fields only through the same merge-and-upsert mechanism used for evaluation results (never by directly overwriting `private/job_evaluations.json`), matching the target record by a vendor+canonical-id composite key derived from the job's URL (the same derivation used for cross-artifact matching elsewhere in this system), falling back to raw `url` equality only when composite-key derivation is not possible (e.g. an unrecognized vendor). A lineage-field upsert SHALL modify only the fields it owns and SHALL NOT alter the record's evaluator-output fields (`skill_match`, `overall_fit`, `fit_category`, etc.) or other stages' lineage fields.

#### Scenario: Upserting application_status does not alter evaluator fields
- **WHEN** `/apply` upserts `application_status: "applied"` and `application_folder` for a job whose evaluator-output fields were previously persisted
- **THEN** the record's `skill_match`, `overall_fit`, `fit_category`, and other evaluator-output fields are unchanged after the upsert

#### Scenario: Matching by composite key avoids duplicate records from URL drift
- **WHEN** a job was originally evaluated from a URL containing LinkedIn tracking parameters, and a later stage upserts a lineage field using a differently-tracked URL for the same posting
- **THEN** the system matches both URLs to the same record via their shared vendor+canonical-id composite key and updates that single record, rather than creating a second record

#### Scenario: Two stages upsert different lineage fields independently
- **WHEN** `generate-application-strategy` upserts `strategy_path` and `positioning_score` for a job, and later `/apply` upserts `application_status` and `application_folder` for the same job
- **THEN** the final record contains all four lineage fields, with neither upsert having erased the other's fields
