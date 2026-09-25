## Why

The `career-advisor` subagent generates a strategic positioning report for opportunities, and the `/apply` workflow natively saves this as `strategy.md` when drafting a full CV and cover letter. However, there is currently no standalone way to generate or update this cache. A standalone skill is needed to backfill strategy logs for existing applications, build caches for externally applied roles without triggering a full CV rewrite, or update an existing strategy mid-stream (e.g., after a recruiter screen changes the positioning).

## What Changes

- Create a new Antigravity skill `generate-application-strategy`.
- The skill will take a company name and job description (or tracker URL), invoke the `career-advisor` subagent to generate the positioning report, and automatically write it to `private/applications/YYYY-MM_Company/strategy.md` and `strategy.json`.
- Add support for Claude for skills and agent delegation (to be implemented by Claude).
- No changes to existing `/apply` workflow or `career-advisor` subagent instructions.

## Capabilities

### New Capabilities
- `application-strategy-generation`: Standalone orchestration skill for invoking the career-advisor and persisting its output to disk.

### Modified Capabilities

## Impact

- **Affected code**: Introduces a new skill in `.agents/skills/generate-application-strategy/SKILL.md`. Adds Claude support for delegation.
- **Storage**: Will write to `private/applications/YYYY-MM_Company/strategy.md` and `strategy.json`.
