# Project Memory

Durable facts and conventions about this repo. Read by any agent working here (Claude Code, Gemini CLI, or the `.agents/` runtime) — not session-specific, update when a fact below goes stale.

## What this repo actually is now

Originally forked from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (MIT-licensed, Danish-job-market-scraping workflow). The active process has diverged significantly:

- **Sourcing**: Gmail-curated LinkedIn/Indeed alerts (`tools/fetch_inbox.py`), not portal scraping.
- **Source of truth for candidate background**: `data/profile.md` — not `CLAUDE.md` and not `.claude/skills/job-application-assistant/01-candidate-profile.md` (those belong to the original fork's onboarding flow). **Reaffirmed 2026-09-21**: this is a one-way relationship going forward. Every file under `cv/` and `documents/cv/current_cv.md` is a tailored *output* — a version matched to a specific job — not an independent input. Never pull a fact, tool, or bullet from a CV variant back into `profile.md` as if the CV were a source; if a CV claims something `profile.md` doesn't, treat that as CV drift to fix in the CV (or flag to the user), not as new information to trust. The 2026-09-21 session found real drift in both directions (CV had richer Bayview detail profile.md lacked; profile.md's new AI-workflow content hadn't propagated to any CV) — the richer Bayview detail was pulled into `profile.md` as a one-time reconciliation before this policy was made explicit; that pattern should not repeat going forward.
- **Evaluation data**: `data/inbox_queue.json` (pending/evaluated jobs) + `data/job_evaluations.json` (flat evaluation list) + `job_search_tracker.csv` (submissions). Always write through `tools/evaluate_jobs_gemini.py`'s `--save-evaluations` merge (`save_evaluations_to_files()`) — never hand-edit these JSON files directly; it upserts by `url` (fallback `title`+`company`).

## Evaluation rubric (fixed, don't reinvent per-file)

Five dimensions, each 0-100: `skill_match`, `experience_level_match`, `company_fit`, `growth_potential`, `red_flags`.
`overall_fit` = weighted composite: skills 30%, experience 25%, company 20%, growth 15%, red_flags −10%.
`fit_category` from `overall_fit`: `high` (80+), `medium` (60-79), `low` (40-59), `skip` (<40).
Downstream consumers depend on this exact shape: `job_search_tracker.csv`'s `fit_rating` column and the `upskill` skill's gap-weighting math both read `overall_fit` as a 0-100 int.

## URL canonicalization for LinkedIn and Indeed

**Design decision** (2026-09-18, `eval-dashboard` planning): all job URLs are normalized at ingestion time so downstream consumers (dashboard, matching logic) see clean URLs without tracking parameters.

- **LinkedIn**: `normalize_linkedin_url(url)` extracts job ID via `/jobs/view/(\d+)` regex and returns `https://www.linkedin.com/comm/jobs/view/{id}/` (implemented in `tools/fetch_inbox.py` since original fork, also used by `fetch_linkedin_with_browser()`).
- **Indeed**: `normalize_indeed_url(url)` extracts job ID via `jk=([0-9a-f]+)` regex and returns `https://www.indeed.com/viewjob?jk={id}` (added 2026-09-18; applied at ingestion time in `tools/fetch_inbox.py`).
- **Composite-key matching** (for `eval-dashboard`): applied-job-to-evaluation matching uses a vendor-prefixed canonical ID (`LKD` for LinkedIn, `IND` for Indeed) derived from the extracted job ID, not raw-URL string matching. This survives tracking-parameter drift between the alert email that produced an evaluation and the URL later entered in the tracker.

Two historical records in `data/job_evaluations.json` (Celonis 4413352108, FTI Consulting 4421660792) initially had full tracking URLs instead of canonicalized form; both were normalized to short form as of 2026-09-18. All future ingested URLs will be canonical at source.

## Evaluation persistence & partial-save validation

**Data files** (always write through `tools/evaluate_jobs_gemini.py`'s merge logic):
- `data/inbox_queue.json` — pending/evaluated jobs (status: "pending" or "evaluated")
- `data/job_evaluations.json` — all evaluations (flat list, upserted by url or title+company)
- `data/job_evaluations.failed.json` — invalid/malformed evaluations (appended, persistent across sessions, with error details and timestamp)

**Validation approach** (when saving evaluations):
- Each record validated against JSON schema (required fields, types, ranges, enum values)
- **Score clamping (0-100)**: when `red_flags` penalty (-10%) exceeds positive match dimensions (common on completely irrelevant or junk postings), raw arithmetic can yield negative scores (e.g. -10). The schema strictly requires `overall_fit` to be an integer between 0 and 100 (`fit_category: 'skip'`). Evaluators and save scripts must clamp `overall_fit` to `[0, 100]` before validation.
- **Valid records**: persisted immediately to inbox_queue and job_evaluations
- **Invalid records**: appended to job_evaluations.failed.json with error details (not lost, not corrupting main files)
- **Consistency checks** (non-blocking): warnings to stderr if overall_fit doesn't match weighted dimensions, fit_category doesn't match thresholds, or arrays are empty — records still persist
- End-of-session summary printed to stderr: "✓ Persisted N | ✗ Failed M"
- This partial-save design prevents agent hallucinations from breaking a batch (97 good jobs still persist even if 3 are malformed)

**Date filtering & queue scope**:
- Sourcing tools default to or accept `--days N` (e.g. `--days 30` filters the queue to the past month).
- In September 2026, all 487 pending jobs in the 30-day window were evaluated and marked `status: "evaluated"`. A small residual of legacy records from months prior (e.g., 6 items from June 2026) remains in `data/inbox_queue.json` in `pending_evaluation` status unless `--all-dates` is explicitly passed.

## Custom Claude Code subagents require a session restart

Adding or editing a file under `.claude/agents/*.md` does not make it invocable via the `Agent` tool in the *current* Claude Code session — the agent roster is loaded once at session start. Calling it mid-session fails with `Agent type '<name>' not found`, even though the file is valid and present on disk. A session restart (or starting a fresh session) is required before a newly created subagent (e.g. `job-evaluator`) can actually be invoked. Keep this in mind for any future work that adds new `.claude/agents/` files — plan for a restart before relying on the new agent in the same sitting.

## Three parallel agent ecosystems

This repo mirrors its commands/skills for three interactive agents:
- `.claude/` — Claude Code. Evaluations tagged `model: "claude-agent-session"`.
- `.gemini/` — Google's Gemini CLI (global model set once in `.gemini/settings.json`, currently `gemini-2.5-flash`; no per-task model override mechanism exists here). Evaluations tagged `model: "gemini-agent-session"`.
- `.agents/` — a third agent runtime (likely "Antigravity" — matches the historical `"model": "Antigravity-Agent-Session"` tag seen in `data/job_evaluations.json`). Its `fetch-inbox` skill already documented Agent Mode as the recommended default ahead of the other two. Evaluations tagged `model: "antigravity-agent-session"`.

Keep changes to `fetch-inbox` behavior mirrored across all three unless a change is deliberately scoped to just one. `/scan-inbox` (a near-duplicate `fetch-inbox` fork) was deleted 2026-09-22 as part of consolidating to a single Gmail entry point — see `openspec/changes/cleanup-legacy-docs-and-apply-pipeline/design.md` Decision 6. When adding new evaluator provenance tags (e.g., for a new agent runtime), add them to the schema validation function's enum check.

## Gmail query is timestamp-based, not `is:unread`-based

`tools/fetch_inbox.py` used to query `is:unread from:(...)`. Since the OAuth scope is `gmail.readonly` (no `gmail.modify`), the script can never mark alert emails as read, so `is:unread` matched every alert email ever received, forever — every run re-fetched and re-parsed the full message list even though URL-level dedup against `data/inbox_queue.json` discarded the reprocessed ones. This is what made "already scanned" emails balloon each run.

**Fix (2026-09-18)**: query is now `from:(...) after:{epoch}`, where `{epoch}` comes from `data/fetch_state.json` (`last_fetch_at`, a Unix timestamp). First-ever run (no state file) defaults to a 30-day lookback. After each run, state is saved as `run_start_epoch - 86400` (1-day overlap buffer) — safe because URL dedup already handles any re-seen messages in the overlap window. `data/fetch_state.json` is gitignored (local/session state, same category as `token.json`).

**Not yet live-verified**: Gmail's `after:` operator accepting a raw Unix epoch integer (vs. `YYYY/MM/DD`) is assumed based on known Gmail search behavior, not confirmed against a real API call in this repo. Confirm on the next real `python tools/fetch_inbox.py` run — if `after:{epoch}` doesn't filter as expected, fall back to formatting `after:` as `YYYY/MM/DD` (loses same-day precision, dedup still protects against reprocessing).

## User context

- On a Claude Pro plan — no marginal cost for evaluating jobs live in a Claude Code session.
- Had reliability problems running Gemini 2.5 (API mode) — this is a real motivation for preferring interactive-agent evaluation, not just cost.
- Low job volume (not processing thousands of applications) — no need for batch/unattended evaluation infrastructure.
- Uses OpenSpec (`openspec/`, `/opsx:*` commands) for planning nontrivial changes — proposal.md / specs delta / design.md / tasks.md workflow. **Always include Mermaid diagrams in `design.md`** (e.g. system architecture flowcharts and sequence/state diagrams to clearly illustrate workflows and component interactions).

## PII / personal-data hygiene — never hardcode into source

The maintainer's real email address (`iouri.chadour@gmail.com`) was found hardcoded directly into the Gmail query string in `tools/fetch_inbox.py` and `tools/build_job_scout.py` (2026-09-22 audit) — not just in expected places like resume/profile files (`data/profile.md`, `cv/*.md` legitimately need contact info), but baked into actual query logic in tracked `.py` source. This is wrong independent of whether the repo is ever made public: config values don't belong in source, and it breaks portability for anyone else forking the repo.

**Convention going forward**: any personal identifier a script needs at runtime (email address, account name, API key, phone number) goes in a gitignored local config file — this repo's existing pattern is `*.local.json` (already in `.gitignore`; see `credentials.json`, `data/token.json`, `.claude/settings.local.json` for the established local-file convention). Ship a tracked `*.example.json` template alongside it. Never a literal string in a `.py`, tracked `.json`, or committed `.md` file (outside the profile/resume files whose whole job is to carry that data).

**Implemented 2026-09-22** via `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/`: `tools/fetch_inbox.py` now loads `job_search_email` from `config.local.json` (gitignored) via a small helper that raises a clear error if the file/key is missing; `config.local.example.json` is the tracked template. `README.md` has an "if you plan to publish/open-source your fork" callout listing every tracked file that carries real personal data (`CLAUDE.md`, `data/profile.md`, `01-candidate-profile.md`, `cv/*.md`, `applications/`, `job_search_tracker.csv`, `documents/`, plus the already-gitignored `config.local.json`/`credentials.json`/`data/token.json`). **`tools/build_job_scout.py`'s identical hardcoded-email bug was deliberately left unfixed** — deferred to the still-open `centralize-config-and-private-store` change.

## Resolved repo debt (was tracked here, cleaned up 2026-09-22)

Fixed via `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/` — kept here as historical closure, not as open items:

- `/apply` no longer implements the fork's LaTeX drafter-reviewer pipeline. It now drafts markdown CV + cover letter directly to `applications/YYYY-MM_Company/`, matching `CLAUDE.md`'s directive. See `openspec/specs/job-application/spec.md` for the formal spec.
- Danish job-portal scraper skills that once lived under `.agents/skills/{jobbank,jobdanmark,jobindex,jobnet}-search/` are gone (confirmed absent as of 2026-09-22) — sourcing is Gmail-alert-based only.
- `.claude/skills/job-scraper/` (once adapted to read from `data/inbox_queue.json` instead of scraping portals) was deleted as part of consolidating to a single Gmail entry point (`/fetch-inbox` only) — its own fetch+quick-assess pass duplicated `/fetch-inbox` + `job-evaluator`'s work with a weaker heuristic. See the archived change's `design.md` Decision 6.

## Known repo debt (still open)

- `documents/` still has the original fork's onboarding layout (`cv/`, `diplomas/`, `linkedin/`, `references/`, `applications/`) alongside the user's own `documents/plans/` notes folder.
- License is MIT, copyright Mads Lorentzen (original fork author) — any cleanup must preserve the copyright/permission notice per `LICENSE`.
- `tools/build_job_scout.py` still has the same hardcoded-email bug `fetch_inbox.py` had — deliberately deferred to the still-open `centralize-config-and-private-store` change, not a miss.
- `apply.md` Step 6 references "the verification checklist from `CLAUDE.md`", but `CLAUDE.md` has no such checklist and never did — pre-existing, unresolved.
