## Why

The project has evolved from a Danish job-portal scraping workflow to a Gmail-alert-based job sourcing system. However, significant dead code and fork remnants from the original MadsLorentzen/ai-job-search fork remain: Danish job-portal scrapers, outdated `/apply` pipeline components, and legacy onboarding commands. Removing these reduces maintenance burden, clarifies the actual active workflow, and resolves contradictions between code and documentation (CLAUDE.md).

## What Changes

- **Remove Danish job-portal scrapers**: Delete `.agents/skills/{jobbank,jobdanmark,jobindex,jobnet}-search/` directories and any related CLI tools. These portals are no longer referenced in the Gmail-alert workflow.
- **Archive legacy `/apply` components**: The `/apply` command currently implements a full LaTeX CV + cover letter drafter pipeline (`cv/`, `cover_letters/`, `.claude/skills/job-application-assistant/01-07`), which contradicts `CLAUDE.md`'s one-line description of producing "a tailored markdown resume." Clarify and simplify the `/apply` command or deprecate it pending user decision.
- **Rewrite README.md**: Remove Danish job-portal references and the outdated scraping workflow diagram; document the actual Gmail-alert → agent evaluation → application workflow; simplify Prerequisites (drop Bun/LaTeX unless explicitly needed); preserve MIT license attribution to Mads Lorentzen.
- **Update SETUP.md**: Remove Bun and LaTeX setup steps (or mark as optional/legacy); focus Prerequisites on Claude Code and Python; add Gmail OAuth configuration if required.
- **Future cleanup scope** (Phase 2, deferred to a follow-up ticket): Remove `/setup`, `/expand`, `/reset` commands if they are unused; migrate or archive `documents/` folder layout. These require user confirmation before removal.

## Capabilities

### New Capabilities
- None (this is a refactor/cleanup change with no new externally observable behavior).

### Modified Capabilities
- None (removing dead code does not change spec-level behavior).

## Impact

- **Affected code**:
  - Removed: `.agents/skills/{jobbank-search,jobdanmark-search,jobindex-search,jobnet-search}/` (4 directories, ~200 LOC)
  - Clarified: `CLAUDE.md` and `.claude/commands/apply.md` alignment
  - Rewritten: `README.md` (workflow description, Prerequisites)
  - Updated: `SETUP.md` (dependency list, OAuth setup)
- **No API or external behavior changes**: The workflow (fetch from Gmail, evaluate jobs, track applications) is unaffected.
- **Reduced repo size and maintenance**: ~200 lines of dead code and associated documentation removed; docs brought in line with actual workflow.
- **Git history preserved**: Deleted code remains recoverable via commit history.
