# Project Memory

Durable facts and conventions about this repo. Read by any agent working here (Claude Code, Gemini CLI, or the `.agents/` runtime) — not session-specific, update when a fact below goes stale.

## What this repo actually is now

Originally forked from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (MIT-licensed, Danish-job-market-scraping workflow). The active process has diverged significantly:

- **Sourcing**: Gmail-curated LinkedIn/Indeed alerts (`tools/fetch_inbox.py`), not portal scraping.
- **Source of truth for candidate background**: `private/profile.md` — not `CLAUDE.md` and not `.claude/skills/job-application-assistant/01-candidate-profile.md` (those belong to the original fork's onboarding flow). **Reaffirmed 2026-09-21**: this is a one-way relationship going forward. Every file under `private/cv/` and `private/documents/cv/current_cv.md` is a tailored *output* — a version matched to a specific job — not an independent input. Never pull a fact, tool, or bullet from a CV variant back into `profile.md` as if the CV were a source; if a CV claims something `profile.md` doesn't, treat that as CV drift to fix in the CV (or flag to the user), not as new information to trust. The 2026-09-21 session found real drift in both directions (CV had richer Bayview detail profile.md lacked; profile.md's new AI-workflow content hadn't propagated to any CV) — the richer Bayview detail was pulled into `profile.md` as a one-time reconciliation before this policy was made explicit; that pattern should not repeat going forward.
- **Evaluation data**: `private/inbox_queue.json` (pending/evaluated jobs) + `private/job_evaluations.json` (flat evaluation list) + `private/job_search_tracker.csv` (submissions). Always write through `tools/evaluate_jobs_gemini.py`'s `--save-evaluations` merge (`save_evaluations_to_files()`) — never hand-edit these JSON files directly; it upserts by `url` (fallback `title`+`company`).

## Evaluation rubric (fixed, don't reinvent per-file)

Five dimensions, each 0-100: `skill_match`, `experience_level_match`, `company_fit`, `growth_potential`, `red_flags`.
`overall_fit` = weighted composite: skills 30%, experience 25%, company 20%, growth 15%, red_flags −10%.
`fit_category` from `overall_fit`: `high` (80+), `medium` (60-79), `low` (40-59), `skip` (<40).
Downstream consumers depend on this exact shape: `private/job_search_tracker.csv`'s `fit_rating` column and the `upskill` skill's gap-weighting math both read `overall_fit` as a 0-100 int.

## URL canonicalization for LinkedIn and Indeed

**Design decision** (2026-09-18, `eval-dashboard` planning): all job URLs are normalized at ingestion time so downstream consumers (dashboard, matching logic) see clean URLs without tracking parameters.

- **LinkedIn**: `normalize_linkedin_url(url)` extracts job ID via `/jobs/view/(\d+)` regex and returns `https://www.linkedin.com/comm/jobs/view/{id}/` (implemented in `tools/fetch_inbox.py` since original fork, also used by `fetch_linkedin_with_browser()`).
- **Indeed**: `normalize_indeed_url(url)` extracts job ID via `jk=([0-9a-f]+)` regex and returns `https://www.indeed.com/viewjob?jk={id}` (added 2026-09-18; applied at ingestion time in `tools/fetch_inbox.py`).
- **Composite-key matching** (for `eval-dashboard`): applied-job-to-evaluation matching uses a vendor-prefixed canonical ID (`LKD` for LinkedIn, `IND` for Indeed) derived from the extracted job ID, not raw-URL string matching. This survives tracking-parameter drift between the alert email that produced an evaluation and the URL later entered in the tracker.

Two historical records in `private/job_evaluations.json` (Celonis 4413352108, FTI Consulting 4421660792) initially had full tracking URLs instead of canonicalized form; both were normalized to short form as of 2026-09-18. All future ingested URLs will be canonical at source.

## Evaluation persistence & partial-save validation

**Data files** (always write through `tools/evaluate_jobs_gemini.py`'s merge logic):
- `private/inbox_queue.json` — pending/evaluated jobs (status: "pending" or "evaluated")
- `private/job_evaluations.json` — all evaluations (flat list, upserted by url or title+company)
- `private/job_evaluations.failed.json` — invalid/malformed evaluations (appended, persistent across sessions, with error details and timestamp)

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
- In September 2026, all 487 pending jobs in the 30-day window were evaluated and marked `status: "evaluated"`. A small residual of legacy records from months prior (e.g., 6 items from June 2026) remains in `private/inbox_queue.json` in `pending_evaluation` status unless `--all-dates` is explicitly passed.

## Custom Claude Code subagents require a session restart

Adding or editing a file under `.claude/agents/*.md` does not make it invocable via the `Agent` tool in the *current* Claude Code session — the agent roster is loaded once at session start. Calling it mid-session fails with `Agent type '<name>' not found`, even though the file is valid and present on disk. A session restart (or starting a fresh session) is required before a newly created subagent (e.g. `job-evaluator`) can actually be invoked. Keep this in mind for any future work that adds new `.claude/agents/` files — plan for a restart before relying on the new agent in the same sitting.

## Two parallel agent ecosystems (Gemini CLI dropped 2026-09-22)

**Gemini CLI is deprecated and no longer available** (confirmed by the user 2026-09-22, during `headhunter-agent` implementation). This repo now mirrors its commands/skills for two interactive agents, not three:
- `.claude/` — Claude Code. Evaluations tagged `model: "claude-agent-session"`.
- `.agents/` — Antigravity (matches the historical `"model": "Antigravity-Agent-Session"` tag seen in `private/job_evaluations.json`). Supports subagent invocation via `invoke_subagent`, structurally equivalent to Claude Code's `Agent` tool — confirmed capable of the same structurally-independent multi-subagent patterns (see "Evidence-verification gate" below). Evaluations tagged `model: "antigravity-agent-session"`.

`.gemini/` files (`.gemini/commands/`, `.gemini/skills/`, `.gemini/GEMINI.md`, `.gemini/settings.json`) still exist in the repo as of 2026-09-22 but are now dead — not cleaned up as part of `headhunter-agent` (out of scope for that change; a future cleanup change should remove them). Do not add new `.gemini/` mirrors going forward. `private/job_evaluations.json` records already tagged `model: "gemini-agent-session"` remain valid historical records — don't touch them retroactively.

Keep changes to `fetch-inbox` behavior mirrored across `.claude/` and `.agents/` unless a change is deliberately scoped to just one. `/scan-inbox` (a near-duplicate `fetch-inbox` fork) was deleted 2026-09-22 as part of consolidating to a single Gmail entry point — see `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/design.md` Decision 6. When adding new evaluator provenance tags (e.g., for a new agent runtime), add them to the schema validation function's enum check.

## Gmail query is timestamp-based, not `is:unread`-based

`tools/fetch_inbox.py` used to query `is:unread from:(...)`. Since the OAuth scope is `gmail.readonly` (no `gmail.modify`), the script can never mark alert emails as read, so `is:unread` matched every alert email ever received, forever — every run re-fetched and re-parsed the full message list even though URL-level dedup against `private/inbox_queue.json` discarded the reprocessed ones. This is what made "already scanned" emails balloon each run.

**Fix (2026-09-18)**: query is now `from:(...) after:{epoch}`, where `{epoch}` comes from `private/fetch_state.json` (`last_fetch_at`, a Unix timestamp). First-ever run (no state file) defaults to a 30-day lookback. After each run, state is saved as `run_start_epoch - 86400` (1-day overlap buffer) — safe because URL dedup already handles any re-seen messages in the overlap window. `private/fetch_state.json` is gitignored (local/session state, same category as `token.json`).

**Not yet live-verified**: Gmail's `after:` operator accepting a raw Unix epoch integer (vs. `YYYY/MM/DD`) is assumed based on known Gmail search behavior, not confirmed against a real API call in this repo. Confirm on the next real `python tools/fetch_inbox.py` run — if `after:{epoch}` doesn't filter as expected, fall back to formatting `after:` as `YYYY/MM/DD` (loses same-day precision, dedup still protects against reprocessing).

## User context

- On a Claude Pro plan — no marginal cost for evaluating jobs live in a Claude Code session.
- Had reliability problems running Gemini 2.5 (API mode) — this is a real motivation for preferring interactive-agent evaluation, not just cost.
- Low job volume (not processing thousands of applications) — no need for batch/unattended evaluation infrastructure.
- Uses OpenSpec (`openspec/`, `/opsx:*` commands) for planning nontrivial changes — proposal.md / specs delta / design.md / tasks.md workflow. **Always include Mermaid diagrams in `design.md`** (e.g. system architecture flowcharts and sequence/state diagrams to clearly illustrate workflows and component interactions).

## Profile-caching token math: batch-invocation vs per-job re-embedding

**Decision (2026-09-22)**: `profile-caching-optimization` (fully planned in `openspec/changes/profile-caching-optimization/`) is **deferred**, not abandoned. Reason: its token-savings case is much weaker on the user's actual primary path than the proposal initially assumed.

- **Interactive-agent evaluation** (the user's primary path, per "User context" above): each subagent invocation reads `private/profile.md` **once per batch**, not once per job — e.g. SCRUM-12's 423-job run only cost 22 full-profile reads (one per parallel batch), not 423. Caching the profile here saves tokens per *batch invocation*, a comparatively small number.
- **Gemini API fallback**: `evaluate_job_api()` re-embeds the full profile into **every per-job prompt**, inside the per-job loop — so a 423-job run costs 423 full-profile embeddings. This is where caching actually pays off.

Since the user evaluates via the interactive-agent path, not the API fallback, the realistic savings right now are much smaller than "full profile size × job count" suggests. Revisit only if Gemini-API-fallback usage increases, or interactive-agent batch counts grow enough for the smaller per-batch saving to matter. Don't re-propose this from scratch — the planning artifacts already exist and validate cleanly; just resume `tasks.md` if/when the calculus changes.

## PII / personal-data hygiene — never hardcode into source

The maintainer's real email address (`iouri.chadour@gmail.com`) was found hardcoded directly into the Gmail query string in `tools/fetch_inbox.py` and `tools/build_job_scout.py` (2026-09-22 audit) — not just in expected places like resume/profile files (`private/profile.md`, `cv/*.md` legitimately need contact info), but baked into actual query logic in tracked `.py` source. This is wrong independent of whether the repo is ever made public: config values don't belong in source, and it breaks portability for anyone else forking the repo.

**Convention as of 2026-09-23** (superseding the `*.local.json` pattern below): any personal setting a script needs at runtime (email address, account name, API key) goes in `private/config.json` (gitignored — the whole `private/` folder is), read via the shared `tools/config.py` module, which also exposes every resolved path constant (`PROFILE_PATH`, `INBOX_QUEUE_PATH`, etc.) so no script hardcodes a path literal either. A tracked `config.example.json` at repo root is the template. Every kept `tools/*.py` script plus `salary_lookup.py` (repo root) imports `config` and uses its constants — never a literal string path or personal identifier in a `.py`, tracked `.json`, or committed `.md` file.

**Superseded history**: `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/` first fixed this narrowly — `tools/fetch_inbox.py` loaded `job_search_email` from a gitignored `config.local.json` (`config.local.example.json` template), deliberately leaving `tools/build_job_scout.py`'s identical bug unfixed. `centralize-config-and-private-store` (2026-09-23) generalized this into `tools/config.py`/`private/config.json` and deleted `config.local.json`/`config.local.example.json` entirely — see the new section below.

## Resolved repo debt (was tracked here, cleaned up 2026-09-22)

Fixed via `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/` — kept here as historical closure, not as open items:

- `/apply` no longer implements the fork's LaTeX drafter-reviewer pipeline. It now drafts markdown CV + cover letter directly to `private/applications/YYYY-MM_Company/` (path updated 2026-09-23 by `centralize-config-and-private-store`; was `applications/YYYY-MM_Company/` at the time this cleanup landed), matching `CLAUDE.md`'s directive. See `openspec/specs/job-application/spec.md` for the formal spec.
- Danish job-portal scraper skills that once lived under `.agents/skills/{jobbank,jobdanmark,jobindex,jobnet}-search/` are gone (confirmed absent as of 2026-09-22) — sourcing is Gmail-alert-based only.
- `.claude/skills/job-scraper/` (once adapted to read from `private/inbox_queue.json` instead of scraping portals) was deleted as part of consolidating to a single Gmail entry point (`/fetch-inbox` only) — its own fetch+quick-assess pass duplicated `/fetch-inbox` + `job-evaluator`'s work with a weaker heuristic. See the archived change's `design.md` Decision 6.

## Positioning rubric and evidence-verification gate (`headhunter-agent`, 2026-09-22)

Three new subagents, mirrored under both `.claude/agents/` and `.agents/agents/` (Gemini CLI dropped — see above): `career-advisor`, `deal-architect`, `evidence-verifier`. All read-only against `private/profile.md`/`private/job_evaluations.json`/`private/job_search_tracker.csv` — none of the three writes to any file; every output is a headless report presented directly in-response for human review.

- **Second, separate rubric**: `data/positioning_rubric.md` scores HIGH_FIT/FIT jobs on a *different* question than the existing fit-evaluation rubric — "how do I position/negotiate this" vs. "should I apply." Five dimensions (title level 20%, dual-threat 25%, domain 20%, comp signal 15%, technology 20%), independent `positioning_score`, never overwrites the job's original `overall_fit`/`fit_category`.
- **Evidence-verification is a structurally independent third subagent, not a self-check.** `career-advisor` and `deal-architect` both invoke `evidence-verifier` (fresh context, no visibility into the drafting conversation) on every draft before presenting it; a BLOCKED verdict withholds presentation until revised and re-verified. This is deliberate — an inline self-review was rejected as the same self-grading failure mode that makes a model's own re-drafts look better without actually improving (see `openspec/changes/archive/.../headhunter-agent/design.md` "Three subagents, not two" once archived). Re-asserting a blocked claim as true, without adding supporting text to `private/profile.md` itself, does not clear the block — confirmed live.
- **Negotiation prep (`deal-architect`) is double-gated**: only runs when `private/job_search_tracker.csv` status is `OFFER`/`FINAL_ROUND` **and** `private/profile.md` has a `Target Compensation Band` set (currently `$200K-$300K`, under "Target Roles & Industries"). Either condition failing alone blocks negotiation output — confirmed live against a scratch profile copy with the band stripped.
- Model tiers follow the existing cost-consciousness precedent: `career-advisor` haiku/flash (high-volume, lower-stakes), `deal-architect` and `evidence-verifier` sonnet/pro (higher-stakes, a false PASS has real consequences).

## Private data consolidation (`centralize-config-and-private-store`, 2026-09-23)

Every artifact carrying real personal or job-search data now lives under the gitignored `private/` folder — `private/profile.md`, `private/cv/`, `private/job_search_tracker.csv`, `private/job_evaluations*.json`, `private/inbox_queue.json`, `private/fetch_state.json`, `private/eval_batches/`, `private/documents/{cv,linkedin,diplomas,references,applications}/`, `private/credentials.json`, `private/token.json`, `private/config.json`, `private/salary_data.json`, `private/applications/`. `data/` as a directory is now retired except for `data/positioning_rubric.md` (tracked, non-personal — the `headhunter-agent` rubric; deliberately left in place rather than relocated). `documents/` keeps only `README.md` and empty `.gitkeep`-placeholder subfolders — real content goes in the matching `private/documents/<subfolder>/` path instead.

**Gotcha worth remembering**: `job_search_tracker.csv` and (surprisingly) `data/job_evaluations.json` were already *tracked* in git before this change — never gitignored, unlike the rest of `data/`. Plain `git mv` on an already-tracked file keeps it tracked at the new path even if the destination matches a `.gitignore` rule, since `.gitignore` only blocks adding *new* untracked files. Moving a tracked file into `private/` requires a follow-up `git rm --cached` (keeping the file on disk) to actually stop tracking it going forward. Apply this same two-step (`git mv` or `mv`, then `git rm --cached` if the source was tracked) for any future move of a tracked file into `private/`.

**Also found and fixed during this change** (both audits — this one and the sibling `cleanup-legacy-docs-and-apply-pipeline` — missed these originally):
- `tools/build_job_scout.py` was a stale, disconnected bootstrap script (would have overwritten current `CLAUDE.md`/`fetch_inbox.py` with an outdated snapshot if ever run) — deleted, along with its only consumer `data/master_resume.md` and the orphaned `tools/readme_build_job_scout_tool.md`.
- `documents/plans/` held 5 tracked markdown files with real candidate-identifying content, never audited by any prior change. The one genuinely undocumented shipped feature they described (the two-phase fetch pipeline) was formalized as a proper spec requirement (`document-two-phase-fetch-pipeline`, archived) with all personal details scrubbed; the originals were then deleted and untracked.
- `salary_lookup.py`/`tools/convert_salary_excel.py` were listed in the proposal as in-scope but never actually assigned a task — closed the gap, both now use `config.SALARY_DATA_PATH`.

**New known gap surfaced, not fixed here**: `.claude/skills/job-application-assistant/01-candidate-profile.md` and `02-behavioral-profile.md` are tracked files that `/setup` populates in place with the candidate's real name, phone number, email, and work history — outside the `private/` convention entirely. User's explicit call (2026-09-23): defer to a future change rather than expand this one further. Whoever picks this up needs to touch every command that reads/writes these paths (`/setup`, `/expand`, `/apply`, `/reset`).

## Known repo debt (still open)

- License is MIT, copyright Mads Lorentzen (original fork author) — any cleanup must preserve the copyright/permission notice per `LICENSE`.
- `apply.md` Step 6 references "the verification checklist from `CLAUDE.md`", but `CLAUDE.md` has no such checklist and never did — pre-existing, unresolved.
- `.gemini/` (`.gemini/commands/`, `.gemini/skills/`, `.gemini/GEMINI.md`, `.gemini/settings.json`) is dead weight since Gemini CLI was confirmed deprecated 2026-09-22 (see "Two parallel agent ecosystems" above) — not cleaned up as part of `headhunter-agent`, out of scope for that change. A future cleanup change should remove it.
- `.claude/skills/job-application-assistant/01-candidate-profile.md` and `02-behavioral-profile.md` carry real PII in tracked files, outside the `private/` convention — see "Private data consolidation" above for full detail. Not yet scoped as a change.
