# interview-negotiation-prep Specification

## Purpose
Defines adversarial interview simulation and compensation negotiation support for tracked opportunities that reach an advanced pipeline stage, so the candidate walks into a final-round or offer conversation having already been pressure-tested.

## Requirements

### Requirement: Interview simulation uses three independent lenses
The system SHALL simulate interview questioning from three independent perspectives — hiring manager, peer engineer, and bar raiser — each producing its own verdict. The system SHALL NOT collapse the three perspectives into a single averaged or blended verdict.

#### Scenario: Three lenses produce independent verdicts
- **WHEN** the candidate requests interview simulation for a tracked opportunity
- **THEN** the output includes a separate verdict from each of the hiring-manager, peer-engineer, and bar-raiser lenses, and the lenses are allowed to disagree with each other

### Requirement: Every simulated question has a follow-up that exposes a gap
For every interview question simulated, the system SHALL generate the follow-up question most likely to expose a weakness in the candidate's draft answer, and SHALL explicitly state which follow-up the candidate is not currently prepared to answer well.

#### Scenario: Simulation names an unprepared follow-up
- **WHEN** the system simulates a question and the candidate's draft answer is evaluated
- **THEN** the output names at least one specific follow-up question the candidate's current answer does not adequately address

### Requirement: Interview simulation covers required topics
The system SHALL generate at least three adversarial questions drawn from the target opportunity's job description, covering at minimum: 90-day roadmap ownership, budget or resource ownership, and operational/organizational scaling.

#### Scenario: Minimum topic coverage is met
- **WHEN** the candidate requests interview simulation for a specific tracked opportunity
- **THEN** the generated questions include at least one question each covering roadmap ownership, budget/resource ownership, and operational scaling

### Requirement: Negotiation prep is gated on pipeline stage
The system SHALL only produce a compensation range and negotiation talking points when the opportunity's status in `private/job_search_tracker.csv` is `OFFER` or `FINAL_ROUND`. For opportunities at any earlier stage, the system SHALL NOT produce a compensation range.

#### Scenario: Negotiation prep runs at OFFER stage
- **WHEN** a tracked opportunity's status is updated to `OFFER`
- **THEN** the system produces a target compensation range with supporting rationale and at least two negotiation talking points

#### Scenario: Negotiation prep does not run before OFFER or FINAL_ROUND
- **WHEN** a tracked opportunity's status is `APPLIED` or `INTERVIEWING`
- **THEN** the system does not produce a compensation range or negotiation talking points for that opportunity

### Requirement: Negotiation prep requires an explicit target compensation band
The system SHALL require a target compensation band to be present in the candidate's profile data before producing a compensation range or negotiation talking points. The system SHALL NOT infer, estimate, or invent a target compensation band on the candidate's behalf when none is present.

#### Scenario: Negotiation prep is blocked when no target band is set
- **WHEN** an opportunity reaches `OFFER` status and no target compensation band is present in the candidate's profile data
- **THEN** the system does not produce a compensation range, and instead reports that a target compensation band must be supplied before negotiation prep can run
