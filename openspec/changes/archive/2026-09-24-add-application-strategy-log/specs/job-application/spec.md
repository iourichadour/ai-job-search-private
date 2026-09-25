## MODIFIED Requirements

### Requirement: Application files are written to a per-application folder
The system SHALL write the final CV, cover letter, and a strategy log (`strategy.md` or `.json`) for an application to `private/applications/YYYY-MM_Company/`, where `YYYY-MM` is the current year-month and `Company` is the target company name. The strategy log SHALL contain the positioning rationale, highlighted strengths, obfuscated gaps, compensation anchors, and interview probing areas (red flags).

#### Scenario: Final output location
- **WHEN** `/apply` completes drafting and revision for a job at "Acme Corp" in September 2026
- **THEN** the final CV, cover letter, and strategy log markdown files are written under `private/applications/2026-09_Acme-Corp/`

#### Scenario: Strategy log contains required sections
- **WHEN** the strategy log is generated
- **THEN** it explicitly states the positioning angle, strengths, gaps, compensation target, and interview red flags
