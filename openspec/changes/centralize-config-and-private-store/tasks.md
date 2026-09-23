## 1. Prerequisite Check

- [ ] 1.1 Verify `cleanup-legacy-docs-and-apply-pipeline` is fully implemented and committed: confirm via `git log` and `ls tools/` that the 5 dead scripts are gone and `config.local.json`/`config.local.example.json` from that change's task 2.8 exist. `tools/build_job_scout.py` is expected to be untouched by that change (still present, still hardcoding the email) — that's correct, not a gap. **Do not proceed past this task if the dead-script deletions or `config.local.json` are missing.**

## 2. Decide `tools/build_job_scout.py`'s Fate (owned by this change)

- [ ] 2.1 Confirm the script's actual role: a one-time repo-scaffold/bootstrap generator (embeds the entire original `CLAUDE.md` content and other file templates as strings, writes them to disk) rather than a recurring operational tool — re-verify this against the current file content, since it may have been edited since the 2026-09-22 audit
- [ ] 2.2 Present the finding to the user and get an explicit keep/delete decision (mirroring the sibling change's own checkpoint pattern) — do not assume either outcome
- [ ] 2.3 Record the decision here before proceeding: **[PENDING — fill in when decided]**. If deleted: remove `tools/build_job_scout.py`, verify via `grep -rl "build_job_scout" .claude .gemini .agents --include=*.md --include=*.json` that no references remain (expect only its own bash-permission entry in `.claude/settings.local.json`, which should also be removed), skip every `build_job_scout.py`-specific sub-task below (they're marked accordingly). If kept: proceed to wire it into `tools/config.py` alongside the other surviving scripts.

## 3. Create the Config Module

- [ ] 3.1 Create `config.example.json` at repo root with the expected shape (at minimum `job_search_email`; fold in whatever `config.local.example.json` from the sibling change already defined) and verify it's tracked via `git status`
- [ ] 3.2 Create `tools/config.py`: loads `private/config.json` (raising a clear error naming the missing file/key if absent, pointing at `config.example.json`), exposes `PRIVATE_DIR` and every resolved path constant needed by kept scripts (`CREDENTIALS_PATH`, `TOKEN_PATH`, `PROFILE_PATH`, `CV_DIR`, `JOB_SEARCH_TRACKER_PATH`, `INBOX_QUEUE_PATH`, `JOB_EVALUATIONS_PATH`, `JOB_EVALUATIONS_FAILED_PATH`, `FETCH_STATE_PATH`, `EVAL_BATCHES_DIR`, `SCRATCH_GLOB`, `APPLICATIONS_DIR`, `DOCUMENTS_DIR` equivalents under `private/documents/`, `SALARY_DATA_PATH`, and `MASTER_RESUME_PATH` only if task 2.3 decided to keep `build_job_scout.py`) and verify `python -c "import tools.config"` runs without error against a manually-created test `private/config.json`
- [ ] 3.3 Delete `config.local.json`/`config.local.example.json` from the sibling change now that `private/config.json`/`config.example.json` supersede them, and verify via grep that nothing still references the old filenames

## 4. Move OAuth Files

- [ ] 4.1 Move `credentials.json` -> `private/credentials.json` (the sibling change already deleted the stale duplicate that was there — verify no collision via `ls private/` before moving)
- [ ] 4.2 Move `data/token.json` -> `private/token.json`
- [ ] 4.3 Update `tools/fetch_inbox.py` to import `CREDENTIALS_PATH`/`TOKEN_PATH` from `tools/config.py` instead of hardcoded literals. **If `build_job_scout.py` was kept (task 2.3)**: same update there, plus replace its hardcoded `iouri.chadour@gmail.com` literal (line ~153) with `config.job_search_email` — this is the fix deferred from the sibling change's task 2.8.
- [ ] 4.4 Verify `python tools/fetch_inbox.py` authenticates successfully against the new paths

## 5. Move Candidate Data

- [ ] 5.1 Move `data/profile.md` -> `private/profile.md`
- [ ] 5.2 Move `cv/*.md` (the real tailored resumes, not any file already deleted by the sibling change's LaTeX cleanup) -> `private/cv/*.md`
- [ ] 5.3 **Only if `build_job_scout.py` was kept (task 2.3)**: move `data/master_resume.md` -> `private/master_resume.md`. If deleted, this file was already removed with the script — skip.
- [ ] 5.4 Update `tools/evaluate_jobs_gemini.py` (and `tools/build_job_scout.py` if kept) to import `PROFILE_PATH`/`CV_DIR` from `tools/config.py`
- [ ] 5.5 Update `.claude/skills/job-application-assistant/*.md`, `.gemini/` and `.agents/` mirrors, and `.claude/commands/apply.md` prose references from `data/profile.md`/`cv/` to `private/profile.md`/`private/cv/`
- [ ] 5.6 Verify via `grep -rn "data/profile\.md\|^cv/" .claude .gemini .agents --include=*.md` that no stale references remain outside archived OpenSpec history

## 6. Move Evaluation Data and Tracker

- [ ] 6.1 Move `data/inbox_queue.json`, `data/job_evaluations.json`, `data/job_evaluations.failed.json`, `data/fetch_state.json` -> `private/`
- [ ] 6.2 Move `data/eval_batches/` and any `data/scratch_*.json` -> `private/eval_batches/`, `private/scratch_*.json`
- [ ] 6.3 Move `job_search_tracker.csv` -> `private/job_search_tracker.csv`
- [ ] 6.4 Update `tools/fetch_inbox.py`, `tools/evaluate_jobs_gemini.py`, `tools/generate_mockup.py` to import these paths from `tools/config.py`
- [ ] 6.5 Update `.claude/commands/fetch-inbox.md`, skill mirrors, and any OpenSpec spec prose (`openspec/specs/inbox-ingestion/spec.md`, `openspec/specs/job-evaluation/spec.md`) that names these paths. **Note (2026-09-22)**: `.claude/commands/scan-inbox.md` no longer exists — `cleanup-legacy-docs-and-apply-pipeline` deleted `/scan-inbox` entirely (consolidated to a single Gmail entry point via `/fetch-inbox`); nothing to update there.
- [ ] 6.6 Run `python tools/fetch_inbox.py` and `python tools/generate_mockup.py` end to end and verify both complete without error against the new paths

## 7. Move `documents/` Personal Content

- [ ] 7.1 Move `documents/cv/`, `documents/linkedin/`, `documents/diplomas/`, `documents/references/`, `documents/applications/` (contents, preserving `.gitkeep` placeholders) -> `private/documents/{cv,linkedin,diplomas,references,applications}/`
- [ ] 7.2 Leave `documents/README.md` and the top-level `documents/` directory in place (tracked) — update its content to describe the new `private/documents/...` layout it instructs users to populate
- [ ] 7.3 Update `.claude/commands/setup.md`, `.claude/commands/expand.md`, and skill mirrors that reference `documents/cv`, `documents/linkedin`, etc., to the new `private/documents/...` paths
- [ ] 7.4 Verify via `grep -rn "documents/cv\|documents/linkedin\|documents/diplomas\|documents/references\|documents/applications" .claude .gemini .agents --include=*.md` that remaining hits are only in `documents/README.md` describing the new layout, not stale old-path instructions

## 8. Redirect Future `/apply` Output

- [ ] 8.1 If `cleanup-legacy-docs-and-apply-pipeline` has not yet been archived into `openspec/specs/job-application/spec.md`: edit that change's still-open `specs/job-application/spec.md` delta, changing `applications/YYYY-MM_Company/` to `private/applications/YYYY-MM_Company/` in both the requirement text and its scenario. If it has already been archived: edit `openspec/specs/job-application/spec.md` directly instead.
- [ ] 8.2 Update `.claude/commands/apply.md` (and mirrors) to write final output to `private/applications/YYYY-MM_Company/` instead of `applications/YYYY-MM_Company/`
- [ ] 8.3 Update `README.md`'s workflow diagram/File Structure and `CLAUDE.md`'s directive to reference `private/applications/YYYY-MM_Company/`

## 9. Simplify `.gitignore`

- [ ] 9.1 Remove now-redundant individual rules whose target has fully moved under `private/`: `data/token.json`, `data/inbox_queue.json`, `data/scratch_*.json`, `data/.tmp*`, `data/fetch_state.json`, `data/eval_batches/`, `salary_data.json`, `job_search_tracker.csv`, `cv/main_*.tex`/`!cv/main_example.tex` (already gone per sibling change), `documents/cv/**` through `documents/applications/**` and their `.gitkeep` negation
- [ ] 9.2 Keep the single `private/` rule and every non-personal-data rule (`.vscode/`, `*.pyc`, `skills-lock.json`, `.claude/settings.local.json`, `*.local.json`, etc.) untouched
- [ ] 9.3 Verify `git status` shows nothing unexpected newly untracked or newly tracked after the `.gitignore` simplification (a moved-but-still-matched file should just disappear from `git status` cleanly, not show as a new untracked file)

## 10. Update README/SETUP Open-Source Callout

- [ ] 10.1 Update the sibling change's planned README "if you plan to publish/open-source your fork" section (or `README.md` directly if that change already landed) to say the rule is now simply "never commit `private/`" instead of listing individual files

## 11. Full Verification

- [ ] 11.1 Fresh-clone smoke test: in a scratch clone (or by temporarily moving `private/` aside), copy `config.example.json` -> `private/config.json`, fill in a test value, re-run the OAuth flow, and verify `python tools/fetch_inbox.py`, `python tools/evaluate_jobs_gemini.py --prepare-batches` (or equivalent), and `python tools/generate_mockup.py` all run using only files created via this setup flow — no source edits required
- [ ] 11.2 Run `grep -rln "data/profile\.md\|data/inbox_queue\.json\|data/job_evaluations\|data/master_resume\|data/token\.json\|data/fetch_state\.json\|^job_search_tracker\.csv" --include=*.py .` and verify zero hits outside `tools/config.py` itself
- [ ] 11.3 Run the same grep against `.claude/`, `.gemini/`, `.agents/` markdown and `openspec/specs/` (excluding `openspec/changes/archive/`) and verify zero stale-path hits
- [ ] 11.4 Run `grep -n "iouri.chadour@gmail.com" tools/*.py` and verify zero hits (confirms `build_job_scout.py`'s deferred fix from task 4.3 landed, if the script was kept; expect the file itself to be absent if it was deleted in task 2.3)
- [ ] 11.5 Confirm `data/` directory is empty or removed entirely (nothing sharable was left behind); if empty, delete it

## 12. Commit and Close

- [ ] 12.1 Stage all changes (moves via `git mv` where possible to preserve history, code edits, `.gitignore` simplification) and review `git status` before committing
- [ ] 12.2 Create a single commit with message `refactor(SCRUM-17-followup): centralize private data under private/ and introduce tools/config.py` and verify the commit appears in `git log`
- [ ] 12.3 Run `git status` and verify working tree is clean
