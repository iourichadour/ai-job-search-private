# Resume

Snapshot of in-progress work, for picking this back up in a new session (any agent). See `MEMORY.md` for durable project facts/conventions this doesn't repeat.

**Last updated**: 2026-09-22 (README checkpoint ready for user review)

## Planned, awaiting user checkpoint: `cleanup-legacy-docs-and-apply-pipeline` OpenSpec change (2026-09-22)

Location: `openspec/changes/cleanup-legacy-docs-and-apply-pipeline/` (branch: `feature/SCRUM-17-cleanup-stale-artifacts`, reused/fast-forwarded from dev — see JIRA/branch notes below)
Status: **planning complete + Task 1.1/1.2 done, waiting on Task 1.3 checkpoint (user review)**. Proposal, design, `job-application` delta spec, and tasks.md pass `openspec validate --changes cleanup-legacy-docs-and-apply-pipeline --strict`. `README.md` has already been rewritten in place (uncommitted) with the real workflow + a Mermaid diagram, per user request, as the review artifact.

**Why this exists**: the archived `2026-09-22-cleanup-stale-fork-artifacts` (SCRUM-17) change checked off "rewrite README.md"/"update SETUP.md" as done, but they still documented the original Danish-fork LaTeX CV/cover-letter workflow. `.claude/commands/apply.md` and the `job-application-assistant` skill still implement that LaTeX pipeline end to end, contradicting `CLAUDE.md`'s "tailored markdown resume" directive. User confirmed this is actively confusing the pending `headhunter-agent` change (SCRUM-16).

**Scope confirmed with user during proposal**: delete the LaTeX pipeline outright (not archive) — `cv/main_example.tex`, `cover_letters/cover.cls`, `cover_letters/OpenFonts/`, LaTeX sections of `05-cv-templates.md`/`06-cover-letter-templates.md` — and rewrite `/apply`, the skill, README.md, and SETUP.md to be markdown-only, matching the real `cv/*.md` resumes already in use. Adds a new `job-application` OpenSpec capability (never spec'd before) so this doesn't silently drift again.

**Expanded scope, 2026-09-22 (user asked for a full repo rescan before any deletion)**: ran a repo-wide audit beyond the known LaTeX files, cross-referencing every skill/command/tool script for live usage. Findings recorded in `design.md` - Repo-Wide Audit Findings, and surfaced in `README.md`'s new "Repo cleanup: pending review" section:
- **Confirmed dead**: `job_scraper/` (empty shell), five zero-reference `tools/*.py` scripts, a duplicate `credentials.json`, accumulated `data/` scratch/backup files, top-level `prompts/scan_inbox_workflow.md`.
- **Needs a user decision**: three overlapping inbox-fetch pathways (`/fetch-inbox`, `/scan-inbox`, the `job-scraper` skill), a leftover Danish-CLI-tools sentence in `.claude/skills/job-scraper/search-queries.md`.
- **Deferred entirely to `centralize-config-and-private-store`** (2026-09-22 scoping clarification, not decided by this change even conditionally): `tools/build_job_scout.py` ("job scout setup") and `data/master_resume.md` (its only consumer) — kept intact, untouched, including their hardcoded-email instance (see Security scope addition below).
- `tasks.md` Section 1 is the checkpoint gate: nothing in Section 2+ (actual deletions) runs until the user reviews `README.md` and confirms what to drop.

**Reversal, 2026-09-22 (`_brief/`/`tools/generate_mockup.py`)**: initially flagged as dead (zero references), but user asked to keep and fix it instead — it's a real, working dashboard generator tied to the pending `eval-dashboard` change (its `_brief/report-spec.md` is a design brief for the same idea, never cross-referenced). Fixed real bugs: a broken model-name-casing filter that silently dropped most of `data/job_evaluations.json`'s 875 records, and several hardcoded placeholder KPIs (fake 68%/76%/88%/82%/85%, a fabricated tech-stack chart). Rewrote it to compute everything live; verified rendering correctly in-browser across all 3 tabs (875 evals, 236 high-fit sorted correctly, real tracker data) with 0 console errors. README.md now documents it under a new "Dashboard: review tracking" section. `eval-dashboard/proposal.md` and `design.md` updated with an "Interim Artifact" note explaining the relationship (this is a quick static-generation tool, not a replacement for `eval-dashboard`'s larger planned live-reloading two-page design). Also resolved which `credentials.json` is live: `tools/fetch_inbox.py` reads the repo-root copy by relative path, so `private/credentials.json` is the confirmed-redundant one (updates tasks.md 2.4).

**Scope addition, 2026-09-22 (user-requested)**: `tasks.md` 5.7 now specifies that the SETUP.md rewrite must replace the current thin "Gmail Account with Job Alerts" note with two real subsections — "Create a dedicated Gmail account for job search" (a separate address, not personal Gmail, to isolate the OAuth grant) and "Configure Gmail API access" (step-by-step Google Cloud Console project creation, enabling the Gmail API, OAuth consent screen + test user, creating an OAuth Client ID, downloading `credentials.json` to repo root, and the first-run browser auth flow) — verified against `tools/fetch_inbox.py`'s actual implementation (`SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']`, reads `credentials.json` from repo root, caches token to `data/token.json`). Not yet written into the real `SETUP.md` file — still pending Section 5 execution after the checkpoint.

**Security scope addition, 2026-09-22 (user-flagged, re: open-sourcing)**: found the maintainer's real email (`iouri.chadour@gmail.com`) hardcoded directly into the Gmail query string in `tools/fetch_inbox.py:344` and `tools/build_job_scout.py:153` (not just in expected places like resume/profile files — 10 tracked files total carry it, see `design.md` - Security/open-source hygiene finding). Documented as a durable convention in the repo's own `MEMORY.md` (new "PII / personal-data hygiene" section — user pointed out this belongs there, not in a private per-user memory file, since it's a project convention any agent working here should see). Scoped into this change's `tasks.md`: 2.8 (de-hardcode `tools/fetch_inbox.py` only into new gitignored `config.local.json` + tracked `config.local.example.json` template), 5.7 updated (SETUP.md's new Gmail subsection also covers creating `config.local.json`), 5.8 (new — README "if you plan to publish/open-source your fork" callout listing every file with real PII), 7.6 (verify zero hits for the literal email in `tools/fetch_inbox.py`). **`tools/build_job_scout.py`'s instance of the same bug is explicitly deferred** to `centralize-config-and-private-store` (see below) — it will still contain the hardcoded literal after this change lands; that's expected, not a miss. None of this is implemented yet — still planning-artifact-only, pending the Section 1.3 checkpoint.

## Staged, not started: `centralize-config-and-private-store` OpenSpec change (2026-09-22)

Location: `openspec/changes/centralize-config-and-private-store/`
Status: **planning complete** (`skip_specs: true` — pure infra/organization change, no capability behavior delta of its own). Passes `openspec validate --changes centralize-config-and-private-store --strict`. **Hard sequencing dependency: must be implemented after `cleanup-legacy-docs-and-apply-pipeline`** (deletes dead scripts this change would otherwise also have to touch, and this change's `tools/config.py` supersedes that change's narrower `config.local.json`).

**Why this exists**: follow-up to a "should we adopt a `private/` folder for all private artifacts?" exploratory question — user confirmed yes, and asked to make it larger: every kept Python tool should read paths/settings from one central config instead of hardcoding relative-string literals per script (11 files inventoried in `design.md` - Context).

**Scope, confirmed via direct questions to the user (2026-09-22)**:
- `tools/config.py` (tracked code) + `private/config.json` (gitignored data, `config.example.json` tracked template at repo root) becomes the single source every kept script reads paths/settings from.
- Full `private/` consolidation, not partial: `data/profile.md`, `cv/*.md`, `job_search_tracker.csv`, `credentials.json`, `data/token.json` move in (as previously discussed) — **plus**, per explicit user confirmation, `data/job_evaluations.json`/`.failed.json` (not classic PII, but sensitive-by-association — user chose to move it) and `documents/`'s personal subfolders (`cv/`, `linkedin/`, `diplomas/`, `references/`, `applications/` — currently protected by granular `.gitignore` rules instead of the single-folder pattern; user chose to move these too for consistency). Already-gitignored operational data (`fetch_state.json`, `scratch_*.json`, `eval_batches/`) moves too, for location consistency (not a new privacy decision, since already excluded from git).
- `documents/README.md` and the top-level `documents/` structure stay tracked in place (public setup instructions) — only the personal *content* underneath moves.
- Future `/apply` output redirects from `applications/YYYY-MM_Company/` to `private/applications/YYYY-MM_Company/` — requires editing the sibling change's still-open `job-application` delta spec (or `openspec/specs/job-application/spec.md` directly if that change archives first).
- **`tools/build_job_scout.py` fully owned by this change** (2026-09-22 scoping clarification, mid-session correction from an earlier draft that had it split across both changes): its keep/delete decision, its hardcoded-email fix, and its config/path wiring all happen here, not in `cleanup-legacy-docs-and-apply-pipeline`. That sibling change makes zero edits to it.

**Next step**: implement `cleanup-legacy-docs-and-apply-pipeline` first (see above — still awaiting the Section 1.3 README checkpoint). Once that's committed, implement this change per its `tasks.md` (11 sections: prerequisite check, config module, then move-and-rewire in groups — OAuth, candidate data, evaluation data/tracker, `documents/`, future `/apply` output — then `.gitignore` simplification, full verification, single commit).

**Next step (for the checkpoint-gated change above)**: user reviews the rewritten `README.md` (specifically the "Repo cleanup: pending review" section) and confirms what to delete. Once confirmed, continue that change's `tasks.md` from Section 2 onward.

## Completed: SCRUM-11 — Verify timestamp-based Gmail query fix (2026-09-20 12:41:05 UTC)

**Work branch**: `feature/SCRUM-11-verify-gmail-timestamp-fix`

**All 4 acceptance criteria verified live**:
1. ✅ **Gmail query correct format**: `Gmail query: from:(...) after:1789834837` (timestamp-based, not `is:unread`)
2. ✅ **fetch_state.json loaded and updated**: Initialized from log, updated to `last_fetch_at: 1789834837` after run
3. ✅ **First run**: Found 100 alert emails, fetched 67 new unique jobs, 419 deduplicated from queue
4. ✅ **Second run** (36 seconds later): Found 7 new emails (legitimately arrived after first run), URL deduplication prevented re-processing

**Verification results**:
- Run 1 (12:20:37): 100 emails → 67/67 new jobs fetched successfully, queue total 995
- Run 2 (12:41:41): 7 emails → 0 new jobs (all URLs already in queue), confirming deduplication working
- Overlap buffer: 1-day re-query enabled, dedup handles overlap via URL hash checking

**Merged to dev**: ✓

## Completed: SCRUM-12 — Re-evaluate pending jobs & select high-fit roles for application (2026-09-21)

**Work branch**: `feature/SCRUM-12-re-evaluate-pending-jobs`

**All acceptance criteria completed** (via Gemini session):
1. ✅ **Pruned SCRUM-11 branch** — safely deleted (3 commits behind dev).
2. ✅ **Fresh job fetch** — Ran `/fetch-inbox`, fetched 24 new jobs from Gmail alerts (1004 → 1019 total queue).
3. ✅ **Comprehensive 30-day evaluation pass**:
   - Scope: all 487 pending jobs in 30-day window (August 22 – September 21, 2026)
   - Pre-screening: 64 alert digests marked `fit_category: "skip"` (`overall_fit: 0`)
   - Main eval: 423 distinct postings evaluated in 22 parallel batches via `job-evaluator` subagents (Gemini, `model: "antigravity-agent-session"`)
   - Validation: 100% schema pass (0-100 clamped), strict canonical URL deduplication
   - Results merged into `data/job_evaluations.json` and `data/inbox_queue.json`

**Final evaluation snapshot** (849 total evals, 843 unique URLs):
- **High-fit roles (80%+)**: 235 (24 fresh targets from this run)
- **Medium-fit roles (60-79%)**: 280
- **Queue status**: 942 evaluated, 71 closed, 6 pending (legacy June 2026, outside window)

**Top 11 fresh high-fit targets identified** (ready for targeted applications):
1. **MetLife** — Principal Data & Analytics Lead (94%)
2. **Enzo Tech Group** — Head of Data Management (90%)
3. **Novartis** — Director, Analytics Engineering (89%) & Director Analytics Infrastructure (87%)
4. **HealthEdge** — Sr Director, Business Intelligence (88%)
5. **Cetera Financial Group** — Director, Data Trust (88%)
6. **Achieve Life Sciences** — Director, Data Strategy & Operations (86%)
7. **JPMorganChase** — Exec Director - Data & AI Fusion Platform (86%)
8. **Huron** — Digital Sr Director – Data & Analytics (84%)
9. **Citi** — Data Architecture Sr Grp Mgr, Director (83%)
10. **ION** — Head of Data & AI Practice, New York (82%)
11. **Apollo Global Management** — AI Solutions Director - Investment Ops (82%)

**Next steps**: Select 3–5 from top 11 for targeted applications; prepare customized application packages.

## Active: `eval-dashboard` OpenSpec change (planning phase, 2026-09-18)

Location: `openspec/changes/eval-dashboard/`
Status: **planning complete, 0/68 tasks implemented** (2026-09-18). Proposal, design, both specs, and task list are done and validated.

**Scope**: Multi-page HTML dashboard (evaluations browser + applied-jobs tracker) reading from `data/job_evaluations.json` and `job_search_tracker.csv`. Single-file vanilla JS/CSS, no backend, works offline in a browser.

**Key design decision**: Applied-jobs matching uses a vendor-aware composite key (vendor prefix `LKD`/`IND` + canonical job ID extracted from URL) instead of raw-URL string matching, because tracking parameters in LinkedIn/Indeed alert URLs can differ from what's later pasted in the tracker, even for the same job.

**Completed pre-work (loose ends fixed, 2026-09-18)**:
- `job_search_tracker.csv`: added required `url` column header and populated the Trace3 row with its LinkedIn URL
- `data/job_evaluations.json`: normalized Celonis (4413352108) and FTI Consulting (4421660792) URLs from full tracking-param form to canonical short form
- `tools/fetch_inbox.py`: added `extract_indeed_job_id()` and `normalize_indeed_url()` functions; applied them at Indeed URL ingestion time (same pattern as LinkedIn)

**Next step**: User reconsidered workflow — wants to re-fetch/re-evaluate jobs and pick a few high-fit roles to apply to *before* building the dashboard, so the dashboard has real application data to work with. Dashboard implementation (tasks 1.1+) deferred pending fresh job evaluations and application decisions.

## Recently Archived: `interactive-agent-job-evaluation` OpenSpec change

Archived as: `openspec/archive/2026-09-17-interactive-agent-job-evaluation/`
Main spec updated: `openspec/specs/job-evaluation/spec.md`
Status: **archived, 26/26 tasks complete** (2026-09-17). Verified live on both Claude Code and Gemini sides.

**Real side effect of live verification (not test data)**:
- **Claude Code batch (task 4.2)**: 6 real jobs evaluated with `model: "claude-agent-session"` (Harnham, Dayforce — 81%, NetApp, Novartis, Jobgether, Accuity).
- **Gemini batch (task 4.3)**: 5 real jobs evaluated with `model: "gemini-agent-session"` (Clearwater Analytics — 80% high fit, FTI Consulting — 79%, BlackRock — 78%, Celonis — 72%, Wellington Management — 58%).
- Total evaluations in `data/job_evaluations.json`: 423 records, 0 duplicate URLs, pre-existing historical records completely intact.

## Active: `agy-job-evaluator-subagent` OpenSpec change

Location: `openspec/changes/agy-job-evaluator-subagent/`
Status: **applied, 8/8 tasks complete** (2026-09-17). All tasks across sections 1-4 are done and verified live.

**Completed work**:
- Defined `.agents/agents/job-evaluator.agent.md` pinned to `Model: pro` (`gemini-2.5-pro`) for high-nuance executive role evaluation (~$0.20/50 jobs).
- Corrected `.gemini/settings.json` model schema to `"model": { "name": "gemini-2.5-pro" }` (verified `gemini --version` runs with zero errors).
- Updated `.agents/skills/fetch-inbox/SKILL.md`, `scan-inbox/SKILL.md`, `.gemini/commands/`, and `.gemini/skills/` to delegate evaluation to the subagent via `invoke_subagent`.
- Live verified: 2 real pending jobs (Apollo Global Management — 82% high fit, S&P Global — 79% medium fit) evaluated via subagent on `pro`, passed schema validation, and merged with `"model": "antigravity-agent-session"`. 423 total records, 0 duplicate URLs.
- Ready to archive via `/opsx:archive`.





**Bug caught and fixed during verification**: the first draft of `.claude/agents/job-evaluator.md` scored `red_flags` backwards (described it as "100 = no red flags, add it into the formula") versus the actual implemented formula in `tools/evaluate_jobs_gemini.py`'s `check_evaluation_consistency()` (which **subtracts** raw `red_flags`, i.e. `red_flags` is a risk-magnitude score where 0 = none) — confirmed by re-deriving the formula against 417 real historical evaluation records and against `MEMORY.md`'s pre-existing (correct) note "red_flags −10%". Fixed before any live evaluation ran; verified correct via a live 6-job test batch (all `overall_fit` values matched the weighted formula within rounding).

**Environment finding**: newly created `.claude/agents/*.md` files are not picked up by the Agent tool mid-session — the agent roster loads once at session start. Confirmed this by hitting `Agent type 'job-evaluator' not found` right after creating the file; a session restart picked it up. Worth remembering for any future new-subagent work in this repo.

**Real side effect of live verification (not test data)**: during task 4.2, `job-evaluator` genuinely scored 6 real pending jobs from the actual Gmail backlog (Director of Analytics/Harnham, Sr Director Enterprise Data & AI Platform/Dayforce — 81% high fit, Director Data & AI/NetApp, Dir Innovative Enterprise Data Product Lead/Novartis, Director Data Strategy & Operations/Jobgether, Director Client Analytics/Accuity) and persisted them to `data/inbox_queue.json` / `data/job_evaluations.json` with `model: "claude-agent-session"`. These are real, kept evaluations — worth a look in the next job-review pass. (A separate `--track-applied` test against the Dayforce job was run and then cleanly reverted — no false "applied" status was left.)

**Scope of the shipped change**: switched job evaluation from Gemini-API-default to interactive-agent-primary:
- Claude Code side (`.claude/commands/fetch-inbox.md`, `scan-inbox.md`, `.claude/skills/fetch-inbox/SKILL.md`) delegates scoring to `.claude/agents/job-evaluator.md`, pinned `model: haiku`.
- Gemini CLI side (`.gemini/commands/...`, `.gemini/skills/...`, `.gemini/GEMINI.md`) scores inline in-session — no per-task model-pinning exists there, so no equivalent subagent.
- Gemini API mode (`evaluate_job_api()` in `tools/evaluate_jobs_gemini.py`, `GEMINI_API_KEY`) kept **completely unchanged** as a fallback, not removed.
- Evaluations tagged by provenance: `claude-agent-session`, `gemini-agent-session`, or the Gemini model name.

**Known gap, still not resolved (unchanged from before this apply session)**: `tasks.md` doesn't cover `.agents/skills/fetch-inbox/SKILL.md` or `.agents/skills/scan-inbox/SKILL.md` (the third, "Antigravity" mirror). Those already document Agent Mode as the default, so they likely only need a provenance tag, not a rewrite — this was deliberately left out of this change's scope and never revisited. Decide via `/opsx:update` on a future change, or explicitly declare out of scope.

## Planned follow-up 1: `fix-failed-evals` skill

**Status**: Not yet scoped as OpenSpec change — durable facts captured in MEMORY.md, ready to build as a standalone skill after `interactive-agent-job-evaluation` ships.

**Purpose**: Manage accumulated failed evaluations in `data/job_evaluations.failed.json`:
- List failed jobs (by session or all accumulated)
- Re-evaluate specific job(s) or all failed jobs
- Move successfully-retried jobs to main evaluation files
- Track retry history

**Planned commands**:
- `/fix-failed-evals --list` → Show all failed evaluations with error details
- `/fix-failed-evals --all` → Re-evaluate all failed jobs (with confirmation prompt)
- `/fix-failed-evals --job "Company Inc"` → Re-evaluate a specific job by name
- Interactive mode (no flags) → Menu-driven selection

**Scope boundary**: This change handles partial save + failure tracking; the retry skill handles post-hoc recovery. Don't fold retry logic into the current change.

## Planned follow-up 2: Profile caching optimization

**Status**: Quick optimization script (not a formal OpenSpec change), to be built after `interactive-agent-job-evaluation` ships.

**Goal**: Save ~100 tokens per evaluation run by replacing full `data/profile.md` (118 lines) with a structured JSON cache.

**Approach**:
- Create `tools/extract_profile.py` — rule-based parser that reads profile.md and extracts key structured facts (skills, target companies, role level, avoid-patterns, etc.) into a 2-3 line JSON cache
- Cache stored as `data/profile.cache.json` (check into git, regenerate only when profile.md changes)
- Update agent instructions (`.claude/agents/job-evaluator.md`, Gemini CLI workflow) to reference cache instead of full profile
- Agent receives ~30 tokens instead of ~200 tokens per run
- Savings: ~170 tokens per run, zero upfront cost (parsing is rule-based, not LLM)

**Why after this change**: Profile caching is a standalone optimization that doesn't block current work and can ship independently.

## Deferred: repo cleanup / fork-provenance

Discussed via `/openspec-explore`, deliberately **not started** as a change yet — no name chosen, no artifacts created. Decision made: this is a **separate** OpenSpec change from `interactive-agent-job-evaluation` (no file overlap, different capability, different blast radius, don't block one on the other).

**Confirmed dead** (safe to remove in that future change): `.agents/skills/{jobbank,jobdanmark,jobindex,jobnet}-search/` (Danish job-portal scraper CLIs).

**Still undecided** — needs the user's call before scoping that change:
- Fate of `/apply`'s original LaTeX drafter-reviewer pipeline (`.claude/commands/apply.md`, `cv/`, `cover_letters/`, `salary_lookup.py`, `.claude/skills/job-application-assistant/01-07`) — currently contradicts `CLAUDE.md`'s simplified description of `/apply`. Is the LaTeX pipeline still wanted in any form, or fully superseded?
- Fate of `/setup`, `/expand`, `/reset` (original onboarding commands) and the `documents/` folder layout they depend on.
- README.md / SETUP.md rewrite scope, and where the MIT attribution (copyright notice to Mads Lorentzen, per `LICENSE`) should live once the README no longer describes the original fork's workflow.

## Dropped this session

- `/statusline` setup — no PS1 config found on this Windows machine at Unix-style paths; user chose to drop it rather than provide an alternate path or describe the desired status line content. Not pursued further; revisit only if asked again.
