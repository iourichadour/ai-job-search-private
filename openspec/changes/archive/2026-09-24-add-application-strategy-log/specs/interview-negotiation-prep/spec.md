## ADDED Requirements

### Requirement: Negotiation and interview prep consumes application strategy log
The system SHALL attempt to read `strategy.md` (or `.json`) from the corresponding `private/applications/YYYY-MM_Company/` directory for the tracked opportunity before generating interview simulation questions or negotiation talking points. If the file exists, the system SHALL use the positioning angle, compensation anchors, and identified gaps contained within to ground the adversarial simulation and negotiation prep.

#### Scenario: Prep grounds itself in the existing strategy log
- **WHEN** the candidate requests interview simulation for a tracked opportunity that has a strategy log
- **THEN** the generated simulation questions and negotiation talking points reflect the positioning choices and compensation anchors documented in that log

#### Scenario: Prep falls back gracefully if no log exists
- **WHEN** the candidate requests interview simulation for an opportunity that does not have a strategy log
- **THEN** the system generates simulation questions and talking points by inferring positioning from the job description and candidate profile directly
