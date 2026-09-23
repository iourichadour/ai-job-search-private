## Why

Personal/sensitive data in this repo is currently protected by ad-hoc, per-path `.gitignore` rules scattered across the tree (`data/token.json`, `data/profile.md`... wait — actually `data/profile.md` is currently *not* gitignored at all, despite carrying the candidate's real name/email/background; `cv/main_*.tex`, `documents/cv/**`, `job_search_tracker.csv`, `salary_data.json`, and more, each a separate line in `.gitignore`). Every new personal-data-bearing file a future script creates needs its own new `.gitignore` line to stay private — nothing enforces that happening, which is exactly how `data/profile.md` ended up untracked-by-omission rather than by design. Separately, every Python tool under `tools/` hardcodes its own relative file paths (`'data/inbox_queue.json'`, `'credentials.json'`, `'job_search_tracker.csv'`, etc.) rather than reading them from one place, and (per the sibling `cleanup-legacy-docs-and-apply-pipeline` change) at least one of those hardcoded values was the maintainer's literal personal email address baked into query logic.

This change consolidates both problems: one gitignored `private/` directory holds every artifact that carries real personal data (the folder already exists in this repo, currently just holding a redundant duplicate `credentials.json`), and one shared Python config module is the single place every tool resolves paths and settings from — so a new script never has to choose a path convention or remember a `.gitignore` line, it just imports the config.

## What Changes

- **BREAKING**: Move personal-data-bearing files into `private/`: `data/profile.md` -> `private/profile.md`, `cv/*.md` (tailored resumes) -> `private/cv/*.md`, `job_search_tracker.csv` -> `private/job_search_tracker.csv`, `credentials.json` -> `private/credentials.json` (root duplicate already deleted by the sibling change), `data/token.json` -> `private/token.json`. The future `/apply` output directory (`applications/YYYY-MM_Company/`, defined by the sibling change's `job-application` spec) becomes `private/applications/YYYY-MM_Company/`.
- **New**: `tools/config.py` — a shared config module every kept Python tool imports for file paths and settings (job-search email, base data directory, etc.), reading from `private/config.json` (gitignored) with a tracked `config.example.json` template at repo root. Supersedes the narrower `config.local.json` fix scoped into the sibling change's task 2.8 — see Impact.
- **Updated**: every surviving `tools/*.py` script (`fetch_inbox.py`, `evaluate_jobs_gemini.py`, `generate_mockup.py`, `convert_salary_excel.py`, `salary_lookup.py`) reads paths from `tools/config.py` instead of hardcoded relative-string literals.
- **This change owns `tools/build_job_scout.py`'s keep/delete decision** (2026-09-22 scoping clarification): the sibling change explicitly defers it here rather than deciding it itself, so this change is where its fate, its hardcoded-email fix, and its config/path wiring (if kept) all get resolved.
- **Simplified**: `.gitignore` collapses most of its per-file personal-data rules into the single `private/` entry it already has; rules that aren't about personal data (`.vscode/`, `skills-lock.json`, `*.pyc`, etc.) are untouched.
- **Decision needed from user before implementation** (see design.md - Open Questions): whether `data/job_evaluations.json` (reveals real target companies/roles, not classic identity PII) and `documents/`'s personal subfolders (already privacy-protected today via granular `.gitignore`, not via a single folder) also move into `private/`, or stay where they are under their current protection.

## Capabilities

### New Capabilities
- None — this is an infrastructure/organization change with no new externally observable capability of the product itself.

### Modified Capabilities
- `job-application` (defined by the sibling `cleanup-legacy-docs-and-apply-pipeline` change, not yet archived into `openspec/specs/`): its "Application files are written to a per-application folder" requirement currently specifies `applications/YYYY-MM_Company/`; this change updates that path to `private/applications/YYYY-MM_Company/`. Because the sibling change hasn't been archived yet, this is coordinated directly in that change's still-open delta spec rather than as a formal spec delta here — see design.md - Sequencing.

## Impact

- **Affected code**: new `tools/config.py`; edits to every kept `tools/*.py` script's path handling; `.gitignore` simplification; file moves (`data/profile.md`, `cv/*.md`, `job_search_tracker.csv`, `credentials.json`, `data/token.json`, future `applications/`).
- **Depends on** `cleanup-legacy-docs-and-apply-pipeline` (not yet implemented): that change deletes the confirmed-dead `tools/*.py` scripts this change would otherwise have to also update, and introduces the narrower `config.local.json` (task 2.8, `tools/fetch_inbox.py` only) that this change's `tools/config.py` supersedes. `tools/build_job_scout.py`'s keep/delete status is explicitly **not** resolved by the sibling change — it's this change's own decision to make. **Sequencing: implement the sibling change first.**
- **User-facing behavior change**: none for the actual job-search workflow (fit evaluation, drafting, tracking all behave the same) — only file locations and internal config wiring change. Anyone with local scripts or muscle memory pointing at the old paths (`data/profile.md`, `cv/main_*.md`, root `job_search_tracker.csv`) needs to know they moved.
- **Open-source safety**: directly extends the goal already raised in the sibling change — after this change, "don't leak personal data if you publish your fork" becomes "don't publish the `private/` folder," a single, memorable, greppable rule instead of a `.gitignore`-line-by-line audit.
- **Jira**: no ticket created by this change; suggested as a follow-up under epic SCRUM-10, sequenced after SCRUM-17's follow-up.
