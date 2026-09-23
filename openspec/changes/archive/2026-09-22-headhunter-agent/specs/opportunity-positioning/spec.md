## Purpose

Defines how HIGH_FIT/FIT jobs from the existing evaluation pipeline get a second, positioning-specific score and a drafted narrative bridging the candidate's hands-on execution to a C-suite outcome, ready for human review before any resume tailoring is applied.

## ADDED Requirements

### Requirement: Positioning scoring is scoped to HIGH_FIT/FIT jobs only
The system SHALL only run positioning scoring on jobs whose existing `fit_category` (from `data/job_evaluations.json`) is `high` or `medium`. Jobs categorized `low` or `skip` SHALL NOT be scored or drafted for positioning.

#### Scenario: A high-fit job is scored for positioning
- **WHEN** a job in `data/job_evaluations.json` has `fit_category: "high"`
- **THEN** the system produces a positioning score and rationale for that job

#### Scenario: A low-fit job is skipped
- **WHEN** a job in `data/job_evaluations.json` has `fit_category: "low"` or `"skip"`
- **THEN** the system does not produce a positioning score or rationale for that job

### Requirement: Positioning rubric is distinct from the fit-evaluation rubric
The system SHALL score positioning fit using five dimensions distinct from the existing `job-evaluation` capability's rubric: title level, dual-threat fit (strategic ownership plus hands-on technical credibility), domain fit, comp signal, and technology fit. Each dimension SHALL be weighted, with weights summing to 100%, and each SHALL have named anchor descriptions for at least a high, medium, and low score. The system SHALL NOT reuse or overwrite the existing `overall_fit`/`fit_category` fields produced by the `job-evaluation` capability.

#### Scenario: Positioning score is computed independently of the fit-evaluation score
- **WHEN** a job with an existing `overall_fit` score of 82 is scored for positioning
- **THEN** the resulting positioning score is computed from the five positioning dimensions and their weights, and the job's original `overall_fit` and `fit_category` fields are left unchanged

### Requirement: Positioning output includes a bridging rationale
For every job scored, the system SHALL produce a rationale of no more than one paragraph that names at least one specific hands-on execution detail (a named technology, system, or delivered outcome) and connects it explicitly to a C-suite strategic outcome category: cost, risk, revenue, or scale.

#### Scenario: Rationale names both an execution detail and a strategic outcome
- **WHEN** the system drafts a positioning rationale for a scored job
- **THEN** the rationale text names at least one specific technology or delivered outcome from the candidate's background and states which of cost, risk, revenue, or scale it maps to for that role

### Requirement: Resume bullet diffs are proposals, not edits
The system SHALL express resume bullet changes as a diff-style list of proposed replacements (3-5 per scored job) rather than rewriting `data/master_resume.md` or any resume file directly.

#### Scenario: A scored job produces bullet proposals, not a file edit
- **WHEN** a HIGH_FIT job is scored for positioning
- **THEN** the system outputs a list of 3-5 proposed bullet replacements and does not modify any resume file on disk

### Requirement: Every positioning output ends with an unsoftened verdict
Every positioning-scoring run SHALL end with a 2-5 sentence verdict assessing whether and how strongly to pursue the opportunity. The verdict SHALL NOT be a restatement of the score or rationale already given, and SHALL NOT be softened to avoid an unfavorable conclusion.

#### Scenario: Verdict is not a restatement
- **WHEN** the system completes a positioning-scoring run for a job
- **THEN** the run's final output includes a verdict of 2-5 sentences that adds a judgment not already stated in the score or rationale
