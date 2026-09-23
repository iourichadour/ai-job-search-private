## 1. Antigravity Subagent Definition

- [x] 1.1 Create `.agents/agents/job-evaluator.agent.md` with YAML frontmatter (`name: job-evaluator`, `model: pro`, description), prompt instructions containing candidate profile ground truth requirement, 5-dimension rubric, formula, output schema, and `"model": "antigravity-agent-session"` tag; verify valid markdown and frontmatter.

## 2. Gemini Configuration Fix

- [x] 2.1 Update `.gemini/settings.json` to change `"model": "gemini-2.5-flash"` to `"model": { "name": "gemini-2.5-pro" }`; verify by running `gemini --help` and confirming no `Error in: model` configuration error appears (verified: `gemini --version` returns 0.57.0 with zero errors).

## 3. Skill & Command Updates

- [x] 3.1 Update `.agents/skills/fetch-inbox/SKILL.md` step 2 to instruct the agent to export via `--filter-only`, delegate scoring to `job-evaluator` subagent with `Model: pro`, write output to `data/.tmp_agent_evals.json`, and merge with `--save-evaluations`; verify instructions.
- [x] 3.2 Update `.agents/skills/scan-inbox/SKILL.md` to follow the same subagent delegation pattern; verify instructions.
- [x] 3.3 Update `.gemini/commands/fetch-inbox.md` and `.gemini/commands/scan-inbox.md` to document subagent delegation for `agy` and inline scoring for standalone CLI; verify instructions.
- [x] 3.4 Update `.gemini/skills/fetch-inbox/SKILL.md` and `.gemini/skills/scan-inbox/SKILL.md` accordingly; verify instructions.

## 4. Verification

- [x] 4.1 Run a verification evaluation of pending jobs in an `agy` session using the subagent delegation pattern; confirm evaluations pass schema validation and are saved with `"model": "antigravity-agent-session"` (verified live: 2 real pending jobs for Apollo Global Management and S&P Global evaluated via subagent on `pro`, passed validation with 0 errors/warnings, merged cleanly).
- [x] 4.2 Verify `data/job_evaluations.json` deduplication and database integrity (verified: 423 total evaluations, 0 duplicate URLs, historical records intact).

