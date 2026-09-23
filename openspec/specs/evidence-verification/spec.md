# evidence-verification Specification

## Purpose
Blocks any drafted claim about the candidate's background that cannot be traced to `private/profile.md`, extending this repo's existing rule against hallucinated skills to every text output the headhunter-agent capabilities produce.

## Requirements

### Requirement: Every factual claim in drafted text must trace to the profile
The system SHALL check every factual claim in text drafted by the `opportunity-positioning` and `interview-negotiation-prep` capabilities — including named technologies, systems, metrics, scope, and ownership claims — against `private/profile.md`. A claim with no supporting text in `private/profile.md` SHALL be classified as unmapped.

#### Scenario: A claim backed by the profile passes
- **WHEN** a drafted resume bullet states a claim that appears in `private/profile.md`
- **THEN** the claim is classified as mapped and is not blocked

#### Scenario: A claim not backed by the profile is unmapped
- **WHEN** a drafted positioning rationale or interview answer states a claim with no corresponding text in `private/profile.md`
- **THEN** the claim is classified as unmapped

### Requirement: Unmapped claims block the draft, not just warn
The system SHALL prevent a draft containing one or more unmapped claims from being presented to the user as ready for review. A block SHALL name the specific unmapped claim and SHALL NOT be overridden by re-asserting that the claim is true without adding it to `private/profile.md` first.

#### Scenario: A draft with an unmapped claim is blocked
- **WHEN** a drafted resume bullet contains an unmapped claim
- **THEN** the draft is not presented as ready for review, and the output names the specific unmapped claim

#### Scenario: Re-asserting an unmapped claim does not clear the block
- **WHEN** an unmapped claim is asserted to be true without any corresponding addition to `private/profile.md`
- **THEN** the block on that claim remains in effect

### Requirement: Verification runs on every draft, not on request only
The system SHALL run evidence verification automatically on every draft produced by `opportunity-positioning` or `interview-negotiation-prep`, without requiring the user to separately request a check.

#### Scenario: Verification runs without a separate request
- **WHEN** a positioning rationale or resume bullet diff is drafted
- **THEN** evidence verification runs on that draft before it is presented, without any additional user action
