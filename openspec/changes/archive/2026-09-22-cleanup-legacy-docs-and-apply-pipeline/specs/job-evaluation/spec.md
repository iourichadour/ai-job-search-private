## MODIFIED Requirements

### Requirement: Interactive-agent evaluation is the primary path
The system SHALL support evaluating pending jobs from within an interactive coding-agent session (Claude Code or Gemini CLI) without requiring an external LLM API key, and this SHALL be the default evaluation path invoked by the inbox-scanning commands and skills in both `.claude/` and `.gemini/`.

#### Scenario: Evaluating pending jobs in an interactive session
- **WHEN** a user runs the `/fetch-inbox` workflow inside an interactive Claude Code or Gemini CLI session
- **THEN** the workflow exports unevaluated jobs from `data/inbox_queue.json`, the interactive agent scores each job itself against `data/profile.md`, and the resulting evaluations are persisted back into `data/inbox_queue.json` and `data/job_evaluations.json` without any call to the Gemini API
