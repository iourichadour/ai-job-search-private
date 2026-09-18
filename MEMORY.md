# Project Memory

Durable facts and conventions about this repo. Read by any agent working here (Claude Code, Gemini CLI, or the `.agents/` runtime) — not session-specific, update when a fact below goes stale.

## What this repo actually is now

Originally forked from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (MIT-licensed, Danish-job-market-scraping workflow). The active process has diverged significantly:

- **Sourcing**: Gmail-curated LinkedIn/Indeed alerts (`tools/fetch_inbox.py`), not portal scraping.
- **Source of truth for candidate background**: `data/profile.md` — not `CLAUDE.md` and not `.claude/skills/job-application-assistant/01-candidate-profile.md` (those belong to the original fork's onboarding flow).
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
- **Valid records**: persisted immediately to inbox_queue and job_evaluations
- **Invalid records**: appended to job_evaluations.failed.json with error details (not lost, not corrupting main files)
- **Consistency checks** (non-blocking): warnings to stderr if overall_fit doesn't match weighted dimensions, fit_category doesn't match thresholds, or arrays are empty — records still persist
- End-of-session summary printed to stderr: "✓ Persisted N | ✗ Failed M"
- This partial-save design prevents agent hallucinations from breaking a batch (97 good jobs still persist even if 3 are malformed)

## Custom Claude Code subagents require a session restart

Adding or editing a file under `.claude/agents/*.md` does not make it invocable via the `Agent` tool in the *current* Claude Code session — the agent roster is loaded once at session start. Calling it mid-session fails with `Agent type '<name>' not found`, even though the file is valid and present on disk. A session restart (or starting a fresh session) is required before a newly created subagent (e.g. `job-evaluator`) can actually be invoked. Keep this in mind for any future work that adds new `.claude/agents/` files — plan for a restart before relying on the new agent in the same sitting.

## Three parallel agent ecosystems

This repo mirrors its commands/skills for three interactive agents:
- `.claude/` — Claude Code. Evaluations tagged `model: "claude-agent-session"`.
- `.gemini/` — Google's Gemini CLI (global model set once in `.gemini/settings.json`, currently `gemini-2.5-flash`; no per-task model override mechanism exists here). Evaluations tagged `model: "gemini-agent-session"`.
- `.agents/` — a third agent runtime (likely "Antigravity" — matches the historical `"model": "Antigravity-Agent-Session"` tag seen in `data/job_evaluations.json`). Its `fetch-inbox`/`scan-inbox` skills already documented Agent Mode as the recommended default ahead of the other two. Evaluations tagged `model: "antigravity-agent-session"`.

Keep changes to fetch-inbox/scan-inbox behavior mirrored across all three unless a change is deliberately scoped to just one. When adding new evaluator provenance tags (e.g., for a new agent runtime), add them to the schema validation function's enum check.

## User context

- On a Claude Pro plan — no marginal cost for evaluating jobs live in a Claude Code session.
- Had reliability problems running Gemini 2.5 (API mode) — this is a real motivation for preferring interactive-agent evaluation, not just cost.
- Low job volume (not processing thousands of applications) — no need for batch/unattended evaluation infrastructure.
- Uses OpenSpec (`openspec/`, `/opsx:*` commands) for planning nontrivial changes — proposal.md / specs delta / design.md / tasks.md workflow.

## Known repo debt (fork remnants, not yet cleaned up)

Tracked for a **separate, not-yet-created** OpenSpec change — see RESUME.md for current status. Do not fold cleanup work into unrelated changes.

- `/apply` (`.claude/commands/apply.md`) still implements the original fork's full drafter-reviewer LaTeX pipeline (CV + cover letter, PDF compile-and-inspect, `salary_lookup.py`, `.claude/skills/job-application-assistant/01-07`) — this **contradicts** `CLAUDE.md`'s current one-line description of `/apply` producing "a tailored markdown resume" in `applications/YYYY-MM_Company/` (a directory that doesn't exist). Nobody has reconciled these since `CLAUDE.md` was rewritten for the Gmail-alert workflow.
- Danish job-portal scraper skills under `.agents/skills/{jobbank,jobdanmark,jobindex,jobnet}-search/` appear fully dead now that sourcing is Gmail-alert-based.
- `.claude/skills/job-scraper/SKILL.md` was already adapted (not dead) — it explicitly documents reading from `data/inbox_queue.json` instead of scraping portals.
- `documents/` still has the original fork's onboarding layout (`cv/`, `diplomas/`, `linkedin/`, `references/`, `applications/`) alongside the user's own `documents/plans/` notes folder.
- License is MIT, copyright Mads Lorentzen (original fork author) — any cleanup must preserve the copyright/permission notice per `LICENSE`.
