## 1. Skill Creation

- [x] 1.1 Create the skill directory `.agents/skills/generate-application-strategy/` and write `SKILL.md` that orchestrates extracting the job, invoking the `career-advisor` subagent with the job description, parsing its JSON output, and writing both `strategy.json` and `strategy.md` to `private/applications/YYYY-MM_Company/`. Verify by manually triggering the skill on a test job and checking that both files are created.
- [x] 1.2 Create the Claude equivalent of the skill (e.g. `.claude/skills/generate-application-strategy.md` or a command) to support Claude for skills and agent delegation. Verify by triggering the skill via Claude. (To be implemented by Claude).

## 2. End-to-End Verification

- [x] 2.1 Run the new `generate-application-strategy` skill on a historical job from `private/job_search_tracker.csv` that does not yet have a strategy log. Verify that both `strategy.json` and `strategy.md` are correctly persisted in the expected folder.
