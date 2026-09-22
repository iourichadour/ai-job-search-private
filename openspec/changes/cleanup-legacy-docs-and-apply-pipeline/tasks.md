## 1. Repo-Wide Audit and README Checkpoint

- [x] 1.1 Scan `.claude/`, `.gemini/`, `.agents/`, and all top-level directories; cross-reference every skill/command/tool script against live usage via grep. Findings recorded in `design.md` - Repo-Wide Audit Findings (done 2026-09-22).
- [x] 1.2 Rewrite `README.md`'s workflow diagram as a Mermaid diagram of the real, current-intended process (Gmail alerts → evaluate → `/apply` markdown draft → reviewer critique → revise → present); fix Prerequisites (drop LaTeX), fix "Fork and clone" origin (`iourichadour/ai-job-search-private`), fix File Structure to match what's actually on disk, rewrite "How `/apply` works" for the markdown workflow
- [ ] 1.3 **CHECKPOINT — user review required**: present the rewritten `README.md` and the full Audit Findings (confirmed-orphaned + needs-a-decision buckets) to the user. Do not proceed to Section 2 until the user confirms which findings to delete.

## 2. Delete Confirmed-Dead Artifacts (post-checkpoint)

- [ ] 2.1 Delete `job_scraper/` (top-level; `.gitkeep` + gitignored `seen_jobs.json` only) and verify via `ls job_scraper 2>&1` reporting it's gone
- [x] 2.2 ~~Delete `_brief/`~~ **REVERSED 2026-09-22**: `_brief/mockup.html` + `_brief/report-spec.md` are kept — see `design.md` Decision 4. Not deleted.
- [x] 2.3 Delete `tools/evaluate_jobs.py`, `tools/evaluate_past_week.py`, `tools/print_data_ai_roles.py`, `tools/refetch_jobs_browser.py`, `tools/summarize_evals.py` and verify via `ls tools/` that only referenced scripts remain. **`tools/generate_mockup.py` REMOVED from this deletion list 2026-09-22** — kept and fixed (real KPIs computed from `data/job_evaluations.json`/`job_search_tracker.csv`, verified rendering correctly in-browser across all 3 tabs with 0 console errors; see `design.md` Decision 4 and `eval-dashboard/design.md` - Interim Artifact).
- [ ] 2.4 Resolve the duplicate `credentials.json`: root is confirmed live (`tools/fetch_inbox.py` reads it by relative path via `InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)`) — delete `private/credentials.json` and verify `python tools/fetch_inbox.py` still authenticates successfully afterward
- [ ] 2.5 Delete stale `data/` scratch/backup artifacts: `data/inbox_queue.json.bkp.json`, all `data/scratch_*.json`, `data/evaluated_jobs_summary.md`
- [ ] 2.6 Delete top-level `prompts/scan_inbox_workflow.md` (the still-live copy is `.gemini/prompts/scan_inbox_workflow.md` — do not touch that one)
- [ ] 2.7 For each "needs a decision" audit item EXCEPT `tools/build_job_scout.py` (scan-inbox consolidation, `job-scraper` Danish-era text, `data/master_resume.md`) apply exactly what the user confirmed at the checkpoint — no unconfirmed deletions. **`tools/build_job_scout.py` is explicitly deferred, not decided here** (2026-09-22 scoping clarification) — its keep/delete decision, its hardcoded-email fix, and its path/config handling all move to the `centralize-config-and-private-store` change instead. Leave the file untouched by this change.
- [ ] 2.8 **New (2026-09-22, user-requested — security/open-source hygiene)**: De-hardcode the personal Gmail address literal out of `tools/fetch_inbox.py:344` only — `tools/build_job_scout.py:153` has the same issue but is explicitly out of scope here per 2.7's deferral, handled instead by `centralize-config-and-private-store`. Replace the `fetch_inbox.py` literal with a value read from a new gitignored `config.local.json` at repo root (matches the existing `*.local.json` `.gitignore` pattern — no gitignore change needed), e.g. `{"job_search_email": "..."}`, loaded via a small helper (raise a clear error naming the missing file/key if absent, don't silently default to empty). Commit a tracked `config.local.example.json` showing the expected shape. Verify via `grep -n "iouri.chadour@gmail.com" tools/fetch_inbox.py` reporting zero hits (build_job_scout.py is expected to still have it until the follow-up change).

## 3. Delete the LaTeX Pipeline

- [ ] 3.1 Delete `cv/main_example.tex` and verify it no longer exists via `ls cv/` (the `cv/*.md` markdown resumes must remain untouched)
- [ ] 3.2 Delete `cover_letters/cover.cls` and `cover_letters/OpenFonts/`, then remove the `cover_letters/` directory if empty; verify via `ls cover_letters/ 2>&1` reporting "No such file or directory" (or the directory being absent from `git status`/`ls .`)
- [ ] 3.3 Remove the LaTeX-specific sections from `.claude/skills/job-application-assistant/05-cv-templates.md` (moderncv/banking template structure, `\cventry`/`\needspace`/`\enlargethispage` guidance) and verify only markdown-relevant guidance remains
- [ ] 3.4 Remove the LaTeX-specific sections from `.claude/skills/job-application-assistant/06-cover-letter-templates.md` (`cover.cls`, `fontspec`, Raleway/Lato font wrapping) and verify only markdown-relevant guidance remains

## 4. Rewrite `/apply` and the Skill for Markdown Output

- [ ] 4.1 Rewrite `.claude/commands/apply.md` Step 2 to draft `applications/YYYY-MM_<Company>/cv.md` and `applications/YYYY-MM_<Company>/cover_letter.md` instead of `.tex` files, and remove the "restore" language pointing at old `cv/main_*.tex`/`cover_letters/cover_*.tex` reference files
- [ ] 4.2 Rewrite `.claude/commands/apply.md` Step 3 (reviewer dispatch) to reference the new markdown file paths in the `<CV_DRAFT file=...>`/`<COVER_LETTER_DRAFT file=...>` prompt template
- [ ] 4.3 Rewrite `.claude/commands/apply.md` Step 5 to replace the mandatory LaTeX compile-and-inspect step with a markdown-appropriate quality pass (re-read both files, check length/structure is reasonable for a CV and cover letter, no leftover placeholder text) — remove all `lualatex`/`xelatex` invocation and PDF-inspection instructions
- [ ] 4.4 Rewrite `.claude/commands/apply.md` Step 6 "Files Created" list to show the new `applications/YYYY-MM_<Company>/` markdown paths; remove the SCRUM-17 LaTeX-contradiction note at the top of the file now that it's resolved
- [ ] 4.5 Rewrite `.claude/skills/job-application-assistant/SKILL.md` Steps 2-3 to reference markdown CV/cover-letter creation in `applications/YYYY-MM_<Company>/` instead of `cv/main_<company>.tex` / `cover_letters/cover_<company>_<role>.tex`
- [ ] 4.6 Verify by reading through the revised `apply.md` end-to-end that every step is internally consistent (no leftover `.tex` filename in a later step referencing an earlier step's now-markdown output)

## 5. Finish README.md and Rewrite SETUP.md

- [ ] 5.1 Update the "Customization" section's LaTeX templates subsection (currently references moderncv/`cover.cls`) to either remove it or replace it with markdown-equivalent customization guidance
- [ ] 5.2 Verify README renders correctly in markdown preview and contains no remaining references to `lualatex`, `xelatex`, `moderncv`, `cover.cls`, or `MadsLorentzen/ai-job-search` (outside Acknowledgements)
- [ ] 5.3 Remove the LaTeX installation section (MiKTeX/MacTeX/texlive) from `SETUP.md` entirely
- [ ] 5.4 Remove the LaTeX compile steps from `SETUP.md`'s "Test the workflow" / "Compile your documents" sections; replace with confirming the markdown files exist under `applications/YYYY-MM_Company/`
- [ ] 5.5 Remove the LaTeX-only troubleshooting entries from `SETUP.md` (compilation errors, missing fonts, `moderncv` package)
- [ ] 5.6 Verify `SETUP.md` contains no remaining references to `lualatex`, `xelatex`, `moderncv`, `cover.cls`, MiKTeX, MacTeX, or texlive
- [ ] 5.7 **New (2026-09-22, user-requested)**: Replace `SETUP.md`'s thin "Gmail Account with Job Alerts" subsection with two real subsections:
  - **"Create a dedicated Gmail account for job search"**: instruct the user to create a new, separate Gmail address used only for job-search alerts (not their personal/primary Gmail) — reasons to state explicitly: isolates the OAuth grant scope (`gmail.readonly`) to job-alert mail only, keeps the OAuth consent screen's test-user list and any future scope audit scoped to one purpose, lets the user revoke API access later without touching their personal account, **and avoids hardcoding a personal address anywhere** (see 5.8). Then have them subscribe that new address to LinkedIn and Indeed job alerts (the existing instruction to set up alerts still applies, just on the new address).
  - **"Configure Gmail API access"**: step-by-step, verified against `tools/fetch_inbox.py`'s actual implementation (`SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']`, `InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)`, token cached to `data/token.json`):
    1. In [Google Cloud Console](https://console.cloud.google.com/), create a new project (e.g. "ai-job-search")
    2. Enable the **Gmail API** for that project (APIs & Services -> Library)
    3. Configure the **OAuth consent screen** (External, Testing mode is sufficient for personal use) and add the dedicated job-search Gmail address as a test user
    4. Create an **OAuth 2.0 Client ID** (Application type: Desktop app)
    5. Download the credential JSON and save it as `credentials.json` in the repo root (already gitignored — never commit it)
    6. Required scope: `https://www.googleapis.com/auth/gmail.readonly` (read-only; the tooling never sends or modifies mail)
    7. Copy `config.local.example.json` to `config.local.json` (gitignored) and set `job_search_email` to the dedicated address — this is what `tools/fetch_inbox.py`'s query filter reads (see 2.8); never hardcode it into a `.py` file
    8. Run `/fetch-inbox` (or `python tools/fetch_inbox.py`) once — this opens a browser window for the OAuth consent flow; sign in with the **dedicated job-search account**, not the personal one. On success, `data/token.json` is created (gitignored) and reused on subsequent runs without re-prompting.
  - Cross-reference: this resolves the "duplicate `credentials.json`" audit item from Section 2.4 — `tools/fetch_inbox.py` reads `credentials.json` from the repo root by relative path, so root is the live copy; `private/credentials.json` is the redundant one.
- [ ] 5.8 **New (2026-09-22, user-requested — open-source safety)**: Add an "If you plan to publish or open-source your fork" callout to `README.md` (near Prerequisites or as its own short section) listing every file that carries real personal data and must be scrubbed, gitignored, or excluded before making the repo public: `CLAUDE.md`, `data/profile.md`, `.claude/skills/job-application-assistant/01-candidate-profile.md`, `cv/*.md` (per-application resumes), `applications/`, `job_search_tracker.csv`, `documents/`, and `config.local.json`/`credentials.json`/`data/token.json` (already gitignored, but call them out too so the reason is clear in one place). State plainly that this repo as committed is the maintainer's own working profile, not a scrubbed template — publishing it as-is publishes that data.

## 6. Add the `job-application` Spec

- [ ] 6.1 Copy `specs/job-application/spec.md` from this change into `openspec/specs/job-application/spec.md` as the new main spec (following the same establishment pattern used for `inbox-ingestion` and `job-evaluation`)
- [ ] 6.2 Cross-check each requirement/scenario in the new main spec against the rewritten `apply.md` from Section 4 and verify they match (fit gate, markdown output, `applications/YYYY-MM_Company/` location, reviewer loop, no-fabrication rule)

## 7. Verify No Stray References

- [ ] 7.1 Run `grep -rIl "lualatex\|xelatex\|moderncv\|cover\.cls" . --exclude-dir=.git --exclude-dir=openspec/changes/archive` and verify the only remaining hits are inside this change's own `openspec/changes/cleanup-legacy-docs-and-apply-pipeline/` planning artifacts (historical record) and `openspec/changes/archive/` (untouched history), not in live docs or code
- [ ] 7.2 Run `grep -rIl "MadsLorentzen/ai-job-search\b" . --exclude-dir=.git --exclude-dir=openspec/changes/archive` and verify no remaining hits outside the Acknowledgements section of README.md and this change's own planning artifacts
- [ ] 7.3 Run `grep -rl "cv/main_example\.tex\|cover_letters/cover_" . --exclude-dir=.git --exclude-dir=openspec/changes/archive` and verify no remaining hits outside archived history
- [ ] 7.4 Run `grep -rIl "jobindex\|jobbank" . --exclude-dir=.git --exclude-dir=openspec/changes/archive` and verify no remaining hits outside archived history (catches the `job-scraper/search-queries.md` Danish-era sentence and anything similar)
- [ ] 7.5 Re-run the Section 1 audit greps against everything deleted in Section 2 and verify each deleted path/filename has zero remaining references outside `.git/` and `openspec/changes/archive/`
- [ ] 7.6 Run `grep -n "iouri.chadour@gmail.com" tools/fetch_inbox.py` and verify zero hits (confirms 2.8's de-hardcoding — `tools/build_job_scout.py` is expected to still contain it, deferred to `centralize-config-and-private-store`); confirm `config.local.json` is untracked via `git status` (must not appear) and `config.local.example.json` is tracked

## 8. Commit and Close

- [ ] 8.1 Stage all changes (deletions, rewrites, new spec file) via targeted `git add` (not `git add -A`) and review `git status` before committing
- [ ] 8.2 Create a single commit with message `chore(SCRUM-17-followup): repo-wide dead-artifact cleanup, delete LaTeX pipeline, align apply.md/docs with markdown workflow, add job-application spec` and verify the commit appears in `git log`
- [ ] 8.3 Run `git status` and verify working tree is clean
