## MODIFIED Requirements

### Requirement: Application files are written to a per-application folder
The system SHALL write the final CV and cover letter for an application to `private/applications/YYYY-MM_Company/`, where `YYYY-MM` is the current year-month and `Company` is the target company name. For the strategy log, the system SHALL delegate generation to the `generate-application-strategy` skill (which invokes `career-advisor` and `evidence-verifier`) rather than drafting it ad hoc, producing both `strategy.json` and `strategy.md` in the same folder. Before delegating, the system SHALL check whether `strategy.json` already exists in the target folder; if it does, the system SHALL reuse the existing file instead of regenerating it, unless the user explicitly asks to refresh it. The strategy log SHALL contain the positioning rationale, highlighted strengths, obfuscated gaps, compensation anchors, and interview probing areas (red flags). When the job posting's URL is known (the user supplied a URL rather than pasted text), the system SHALL pass it through to the delegated generation call so that `strategy.json`'s `url` field is populated.

#### Scenario: Final output location
- **WHEN** `/apply` completes drafting and revision for a job at "Acme Corp" in September 2026
- **THEN** the final CV, cover letter, and strategy log files (`strategy.md` and `strategy.json`) are written under `private/applications/2026-09_Acme-Corp/`

#### Scenario: Strategy log contains required sections
- **WHEN** the strategy log is generated
- **THEN** it explicitly states the positioning angle, strengths, gaps, compensation target, and interview red flags

#### Scenario: Existing strategy log is reused, not regenerated
- **WHEN** `/apply` reaches the strategy log step and `private/applications/YYYY-MM_Company/strategy.json` already exists for the target company (for example, previously created by the standalone `generate-application-strategy` skill)
- **THEN** the system reuses that file as the application's strategy log instead of invoking `career-advisor` and `evidence-verifier` again

#### Scenario: User explicitly requests a refresh
- **WHEN** the user asks `/apply` to refresh or update the strategy log for an application that already has one
- **THEN** the system regenerates it via `career-advisor` and `evidence-verifier`, overwriting the existing `strategy.json` and `strategy.md`

#### Scenario: URL is carried through into the strategy log
- **WHEN** `/apply` is invoked with a job posting URL and generates a new strategy log
- **THEN** the written `strategy.json`'s `url` field contains that URL, not an empty string

#### Scenario: No URL was ever available
- **WHEN** `/apply` is invoked with pasted job posting text and no URL
- **THEN** `strategy.json`'s `url` field may remain empty, since no URL exists to carry through
