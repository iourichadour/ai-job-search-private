## Purpose
Defines a standalone agentic skill to orchestrate the generation and persistence of an application strategy log (`strategy.md`) for a specific job opportunity without requiring a full CV/cover letter drafting pass.

## ADDED Requirements

### Requirement: Standalone strategy generation skill
The system SHALL provide a `generate-application-strategy` skill that allows the user to generate a strategy log for an opportunity by providing a company name and job description (or a reference to the tracker).

#### Scenario: User requests strategy generation
- **WHEN** the user invokes the `generate-application-strategy` skill with a job description and company name
- **THEN** the skill generates the strategy and writes it to disk

### Requirement: Skill invokes career-advisor and persists output
The skill SHALL invoke the `career-advisor` subagent to perform the underlying positioning evaluation and draft the rationale, bullet diffs, and verdict. The skill SHALL save the raw JSON report to `private/applications/YYYY-MM_Company/strategy.json` and a parsed human-readable version to `strategy.md` in the same directory.

#### Scenario: Output is persisted correctly
- **WHEN** the `career-advisor` returns a passing evaluation for a job at "Acme Corp" in September 2026
- **THEN** the skill formats the output and writes it to `private/applications/2026-09_Acme-Corp/strategy.md` and saves the raw output to `strategy.json`

#### Scenario: Fallback or missing folder
- **WHEN** the output folder does not exist
- **THEN** the skill creates the `private/applications/YYYY-MM_Company` folder before writing `strategy.md` and `strategy.json`

### Requirement: Cross-agent skill support
The system SHALL support Claude for skills and agent delegation to ensure compatibility across the parallel ecosystems.

#### Scenario: Claude runs the skill
- **WHEN** the user invokes the skill via Claude
- **THEN** Claude successfully delegates to the appropriate agents and writes the output files
