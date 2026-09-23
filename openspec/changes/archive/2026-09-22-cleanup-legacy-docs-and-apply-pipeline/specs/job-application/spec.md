## Purpose
Defines the `/apply` drafter-reviewer workflow's behavior: evaluating a job posting for fit, drafting a tailored markdown CV and cover letter, having a second agent critique and revise them, and writing the final files to a predictable location — replacing the undocumented, contradictory LaTeX pipeline `/apply` previously implemented.

## ADDED Requirements

### Requirement: Fit evaluation gates drafting
The system SHALL evaluate the job posting against `data/profile.md` before drafting any application materials, present the evaluation (skills match, experience match, behavioral/culture match, salary benchmark if available, overall fit recommendation) to the user, and SHALL NOT proceed to drafting unless the user confirms.

#### Scenario: User declines to proceed after evaluation
- **WHEN** `/apply <job>` presents its fit evaluation and the user answers no to drafting
- **THEN** the workflow stops without writing any CV or cover letter files

#### Scenario: User confirms and drafting proceeds
- **WHEN** `/apply <job>` presents its fit evaluation and the user answers yes
- **THEN** the workflow proceeds to draft a CV and cover letter

### Requirement: Application output is markdown, not LaTeX
The system SHALL draft the CV and cover letter as markdown files (`.md`), never as `.tex` source or compiled PDF output. No step of the workflow SHALL require a LaTeX distribution, `lualatex`, or `xelatex`.

#### Scenario: Drafting produces markdown files
- **WHEN** the drafter step writes the CV and cover letter to disk
- **THEN** both files have a `.md` extension and contain no LaTeX markup or compilation instructions

### Requirement: Application files are written to a per-application folder
The system SHALL write the final CV and cover letter for an application to `applications/YYYY-MM_Company/`, where `YYYY-MM` is the current year-month and `Company` is the target company name, consistent with `CLAUDE.md`'s directive for where application artifacts live.

#### Scenario: Final output location
- **WHEN** `/apply` completes drafting and revision for a job at "Acme Corp" in September 2026
- **THEN** the final CV and cover letter markdown files are written under `applications/2026-09_Acme-Corp/`

### Requirement: Reviewer critique and revision loop
The system SHALL spawn a second agent, with the job posting and both drafts passed inline, to research the target company and critique the drafts for missed keywords, company-specific angles, weak framing, and tone/style issues, and the drafter SHALL revise the drafts based on that critique before presenting final output.

#### Scenario: Reviewer feedback is applied before final presentation
- **WHEN** the reviewer agent returns structured edits and narrative suggestions
- **THEN** the drafter applies applicable edits to the markdown drafts and the revised files are what gets presented to the user, not the pre-review draft

### Requirement: No fabricated claims
The system SHALL NOT include any skill, experience, or achievement in the CV, cover letter, or reviewer suggestions that is not grounded in `data/profile.md`. A posting requirement the candidate does not meet SHALL be acknowledged honestly or bridged via adjacent real experience, never invented.

#### Scenario: Reviewer flags an unmet requirement
- **WHEN** the job posting requires a skill absent from `data/profile.md`
- **THEN** the final application materials either omit a claim of that skill or reframe genuinely adjacent experience, and do not assert the candidate has it
