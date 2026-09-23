## MODIFIED Requirements

### Requirement: Interactive-agent evaluation is the primary path
The system SHALL support evaluating pending jobs from within an interactive coding-agent session (Claude Code or Gemini CLI) without requiring an external LLM API key, and this SHALL be the default evaluation path invoked by the inbox-scanning commands and skills in both `.claude/` and `.gemini/`.

#### Scenario: Evaluating pending jobs in an interactive session
- **WHEN** a user runs the `/fetch-inbox` workflow inside an interactive Claude Code or Gemini CLI session
- **THEN** the workflow exports unevaluated jobs from `data/inbox_queue.json`, the interactive agent scores each job itself against the cached profile extraction (`data/profile.cache.json`, generated from `data/profile.md`), and the resulting evaluations are persisted back into `data/inbox_queue.json` and `data/job_evaluations.json` without any call to the Gemini API

## ADDED Requirements

### Requirement: Profile scoring input is a generated cache, kept fresh relative to the source profile
The system SHALL score jobs against a generated extraction of `data/profile.md` (`data/profile.cache.json`) rather than passing the full profile file to each evaluator invocation, for both the interactive-agent evaluation paths and the Gemini API fallback path. The system SHALL detect when `data/profile.cache.json` is out of date relative to `data/profile.md` (i.e. the profile has been edited since the cache was last generated) and SHALL surface that condition rather than silently evaluating jobs against a stale cache.

#### Scenario: Cache is current
- **WHEN** an evaluator (interactive-agent or Gemini API fallback) begins scoring a batch of jobs and `data/profile.cache.json` was generated from the current contents of `data/profile.md`
- **THEN** the evaluator scores every job in the batch using `data/profile.cache.json`, and no evaluation record in the batch is blocked or delayed by a freshness check

#### Scenario: Profile edited after the cache was last generated
- **WHEN** `data/profile.md` has been modified since `data/profile.cache.json` was last generated
- **THEN** the system surfaces this staleness clearly before any job in the pending batch is scored against the stale cache, rather than silently persisting evaluation records derived from out-of-date profile data

#### Scenario: Cache does not yet exist
- **WHEN** an evaluator is invoked and `data/profile.cache.json` does not exist
- **THEN** the system surfaces that the cache must be generated from `data/profile.md` before evaluation can proceed, rather than falling back to reading `data/profile.md` in full
