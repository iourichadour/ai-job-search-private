# Resume

Snapshot of in-progress work, for picking this back up in a new session (any agent). See `MEMORY.md` for durable project facts/conventions this doesn't repeat.

**Last updated**: 2026-09-20 12:41:41 UTC (session complete)

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

## In-Progress: SCRUM-12 — Re-evaluate pending jobs & select high-fit roles for application (2026-09-21)

**Work branch**: `feature/SCRUM-12-re-evaluate-pending-jobs`

**Current progress**:
1. ✅ Pruned feature/SCRUM-11 branch from dev (3 commits behind, safely deleted)
2. ✅ Ran `/fetch-inbox` — fetched 24 jobs from Gmail alerts (1004 → 1019 total queue)
3. ✅ Ran `/scan-inbox` evaluation pass via `job-evaluator` subagent (Gemini 2.5 Pro) on 22 fresh postings:
   - 21 unique evaluations passed schema validation and merged into `data/job_evaluations.json` (423 → 444 total)
   - 4 new high-fit roles (80%+ fit) identified: Huron (84%), Citi (83%), Visa (80%), Baringa (80%)
   - 6 new medium-fit roles (60-79% fit), including Dun & Bradstreet (79%)

**Current evaluation snapshot** (444 total evals):
- Total high-fit roles (80+): **224**
- Available to apply (not yet applied): **223**
- Already applied to: 1 (Senior Director, AI Platforms @ Trace3, 83% fit)

**Next steps**:
1. Present top fresh high-fit candidates for application decisions
2. Select target roles and prepare customized application packages (tailored CV & cover letter)

**Expected outcome**: Identify 3-5 high-fit roles to prioritize for applications, then pause dashboard work to focus on targeted applications

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
