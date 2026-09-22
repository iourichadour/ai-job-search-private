## Why

The archived change `2026-09-22-cleanup-stale-fork-artifacts` (SCRUM-17) marked its README.md/SETUP.md rewrite tasks complete, but the actual files still document the original Danish-fork, LaTeX-based workflow: a LaTeX CV/cover-letter compilation pipeline, MiKTeX/TeXLive prerequisites, a fork-clone pointing at `MadsLorentzen/ai-job-search`, and a file structure listing directories that don't exist (`applications/`) or no longer reflect reality. `.claude/commands/apply.md` and the `job-application-assistant` skill still hard-code that same LaTeX pipeline, directly contradicting `CLAUDE.md`'s directive to produce "a tailored markdown resume." This is not a new idea — SCRUM-17 explicitly deferred it "pending user decision" — but it is now actively blocking clarity for the pending `headhunter-agent` change (SCRUM-16), whose new subagents need one unambiguous target resume format to draft bullet diffs against.

## What Changes

- **BREAKING**: Delete the LaTeX CV/cover-letter pipeline entirely: `cv/main_example.tex`, `cover_letters/cover.cls`, `cover_letters/OpenFonts/`, and the LaTeX-specific guidance in `.claude/skills/job-application-assistant/05-cv-templates.md` and `06-cover-letter-templates.md`. The real, already-in-use markdown resumes in `cv/*.md` are preserved untouched.
- **BREAKING**: Rewrite `.claude/commands/apply.md` Steps 2 and 5 to draft and finalize a markdown resume + markdown cover letter in `applications/YYYY-MM_Company/` (per `CLAUDE.md`) instead of `.tex`/PDF output. Removes the mandatory `lualatex`/`xelatex` compile-and-inspect step; replaces it with a markdown-appropriate quality pass (length/format checks appropriate to plain text).
- Rewrite `.claude/skills/job-application-assistant/SKILL.md` Steps 2-3 to reference the markdown workflow, dropping `.tex` file-naming and template instructions.
- Rewrite `README.md`: replace the LaTeX-centric workflow diagram and "How `/apply` works" section with the actual Gmail-alert -> evaluate -> `/apply` (markdown) workflow; fix Prerequisites (drop LaTeX entirely); fix the fork-clone step to point at the correct origin; fix the File Structure section to match what's actually on disk (drop `cover_letters/`, correct `cv/` and `applications/` descriptions); preserve MIT license / Mads Lorentzen attribution.
- Rewrite `SETUP.md`: remove the LaTeX installation section, LaTeX compile steps, and LaTeX-only troubleshooting entries; update "Test the workflow" to describe markdown resume output landing in `applications/YYYY-MM_Company/`.
- **New**: a `job-application` capability spec (`openspec/specs/job-application/spec.md`) documenting the `/apply` drafter-reviewer workflow's expected behavior now that it's formally speced for the first time — output format (markdown), output location (`applications/YYYY-MM_Company/`), the fit-evaluation gate, and the reviewer critique/revision loop. This gives `headhunter-agent` (SCRUM-16) a concrete spec to build resume-bullet-diff requests against instead of inferring behavior from prose docs.

## Capabilities

### New Capabilities
- `job-application`: Defines the `/apply` command's drafter-reviewer workflow — fit evaluation gate, markdown CV + cover letter drafting into `applications/YYYY-MM_Company/`, reviewer critique/revision loop, and the verification checklist. Never previously spec'd; this is the first formal capture of `/apply`'s expected behavior, now aligned with `CLAUDE.md` instead of the legacy LaTeX implementation.

### Modified Capabilities
(none — `job-application` did not exist as a spec'd capability before this change, so there is no existing delta to apply)

## Impact

- **Affected code**:
  - Deleted: `cv/main_example.tex`, `cover_letters/cover.cls`, `cover_letters/OpenFonts/` (fonts), and the now-empty `cover_letters/` directory
  - Rewritten: `.claude/commands/apply.md` (Steps 2 and 5), `.claude/skills/job-application-assistant/SKILL.md` (Steps 2-3), `05-cv-templates.md`, `06-cover-letter-templates.md`
  - Rewritten: `README.md`, `SETUP.md`
  - New: `openspec/specs/job-application/spec.md`
- **User-facing behavior change**: `/apply` will produce markdown CV + cover letter files in `applications/YYYY-MM_Company/` instead of `.tex`/PDF files in `cv/`/`cover_letters/`. Anyone relying on the LaTeX PDF output must regenerate it manually from the old `main_example.tex` template (recoverable via git history) going forward — this workflow no longer produces it automatically.
- **Unblocks**: `headhunter-agent` (SCRUM-16) gets one unambiguous resume format/location to target for its resume-bullet-diff requests.
- **Jira**: Suggested follow-up to SCRUM-17 under epic SCRUM-10 (not created by this change — left for the user to open, e.g. as SCRUM-18, if they want Jira tracking alongside the OpenSpec change).
- **Git history preserved**: all deleted LaTeX files remain recoverable via commit history.
