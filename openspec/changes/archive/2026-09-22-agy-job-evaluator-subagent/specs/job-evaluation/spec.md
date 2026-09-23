## MODIFIED Requirements

### Requirement: Interactive-agent evaluation is the primary path
The system SHALL support evaluating pending jobs from within an interactive coding-agent session (Claude Code or Gemini CLI) without requiring an external LLM API key, and this SHALL be the default evaluation path invoked by the inbox-scanning commands and skills in both `.claude/` and `.gemini/`.

#### Scenario: Evaluating pending jobs in an interactive session
- **WHEN** a user runs the `/fetch-inbox` workflow inside an interactive Claude Code or Gemini CLI session
- **THEN** the workflow exports unevaluated jobs from `data/inbox_queue.json`, the interactive agent scores each job itself against `data/profile.md`, and the resulting evaluations are persisted back into `data/inbox_queue.json` and `data/job_evaluations.json` without any call to the Gemini API

### Requirement: Evaluations are tagged by evaluator provenance
Each persisted evaluation record SHALL identify which evaluator produced it via the `model` field: `claude-agent-session` when scored by an interactive Claude Code session, `gemini-agent-session` when scored by an interactive Gemini CLI session, `antigravity-agent-session` when scored by an interactive Antigravity agent session, or the underlying Gemini model name (e.g. `gemini-2.5-flash`) when scored via the Gemini API fallback.

#### Scenario: Claude Code session evaluation is tagged
- **WHEN** a job is evaluated inside a Claude Code session using the interactive-agent path
- **THEN** the saved evaluation record's `model` field is `claude-agent-session`

#### Scenario: Gemini CLI session evaluation is tagged
- **WHEN** a job is evaluated inside a Gemini CLI session using the interactive-agent path
- **THEN** the saved evaluation record's `model` field is `gemini-agent-session`

#### Scenario: Antigravity agent session evaluation is tagged
- **WHEN** a job is evaluated inside an Antigravity agent session or by its spawned `job-evaluator` subagents
- **THEN** the saved evaluation record's `model` field is `antigravity-agent-session`

## ADDED Requirements

### Requirement: Dedicated evaluator subagents pinned to specialized models
Interactive agent workflows in Claude Code and Antigravity (`agy`) SHALL delegate the evaluation of exported jobs to dedicated subagents pinned to specialized models (`haiku` in Claude Code, `pro` in Antigravity) rather than consuming interactive session context in the main orchestrating session.

#### Scenario: Antigravity workflow delegates to pinned pro subagent
- **WHEN** `/fetch-inbox` or `scan-inbox` is executed in Antigravity (`agy`)
- **THEN** the orchestrating agent invokes the `job-evaluator` subagent with `Model: pro` to score the batch against `data/profile.md`

