# Resume

Snapshot of in-progress work, for picking this back up in a new session (any agent). See `MEMORY.md` for durable project facts/conventions this doesn't repeat.

**Last updated**: 2026-09-22 (`cleanup-legacy-docs-and-apply-pipeline` shipped, verified, and archived)

## Completed & Archived: `cleanup-legacy-docs-and-apply-pipeline` OpenSpec change (2026-09-22)

Archived as: `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/`
Main specs updated: `openspec/specs/job-application/spec.md` (new capability), `openspec/specs/job-evaluation/spec.md` (modified: dropped the scan-inbox mention)
Branch: `feature/SCRUM-17-cleanup-stale-artifacts` — 3 commits (`bda145c` cleanup, `3f0aa66` task bookkeeping, `ae39305` archive move), pushed to origin. **Not yet merged to `dev`** — open a PR when ready.
Status: **all 42 tasks complete, archived**.

**What shipped**:
- Repo-wide audit (Section 1) surfaced everything below; checkpoint review with the user resolved every open decision (consolidate to one Gmail entry point, delete `job-scraper` skill entirely, LaTeX confirmed for deletion).
- **Deleted**: `job_scraper/`, 5 dead `tools/*.py` scripts (one — `evaluate_jobs.py` etc — had been falsely marked done in an earlier session without actually being deleted; caught and fixed during this session via re-verification), duplicate `credentials.json`, stale `data/` scratch/backup files, top-level `prompts/scan_inbox_workflow.md`.
- **Consolidated to a single Gmail entry point**: deleted `/scan-inbox` (all 4 locations: `.claude/`, `.gemini/` command+skill, `.agents/` skill) and the `job-scraper` skill entirely (its `search-queries.md` was a whole obsolete manual-search-query doc, not just the flagged Danish-CLI sentence). Fixed `.claude/commands/setup.md` onboarding, which actively wired up both (a `job-scraper` Step 8, a `/scrape` "try it out" callout, plus its own separate `cv/main_example.tex` references) — this was larger than the original task text anticipated but was mechanical execution of the same confirmed decision.
- **Deleted the LaTeX CV/cover-letter pipeline** (`cv/main_example.tex`, `cover_letters/cover.cls` + `OpenFonts/`) and rewrote `/apply`, `job-application-assistant/SKILL.md`, `05-cv-templates.md`, `06-cover-letter-templates.md` for markdown output to `applications/YYYY-MM_Company/cv.md`/`cover_letter.md` — kept and adapted all the non-LaTeX content (profile statement templates, relevance-weighted cutting logic, section ordering).
- **De-hardcoded the maintainer's email** out of `tools/fetch_inbox.py` into a gitignored `config.local.json` (tracked `config.local.example.json` template) — verified end-to-end against live Gmail auth. `tools/build_job_scout.py`'s same bug is deferred to `centralize-config-and-private-store` (below), not fixed here.
- **Rewrote `SETUP.md`**: dropped all LaTeX install/compile/troubleshooting content, added real "create a dedicated Gmail account" + "configure Gmail API access" (8-step, `config.local.json`-aware) subsections.
- **Rewrote `README.md`**: real Mermaid workflow diagram, correct fork/clone origin, corrected file structure, an "if you plan to publish/open-source your fork" PII callout.
- **New `openspec/specs/job-application/spec.md`** — first formal spec for `/apply`'s behavior (fit gate, markdown output, `applications/YYYY-MM_Company/` location, reviewer loop, no-fabrication rule), cross-checked against the rewritten `apply.md`.
- **Fixed several stale references discovered along the way** (not in the original task list, but direct consequences of the confirmed decisions): the live `job-evaluation` spec's "fetch-inbox or scan-inbox" scenario (formally declared as a Modified Capability delta, not silently patched), dead `.gitignore` rules for deleted LaTeX/job_scraper paths, a dead `settings.local.json` permission entry, `MEMORY.md`'s stale Danish-scraper note.

**Known gap, not fixed (pre-existing, out of scope)**: `apply.md` Step 6 says "run the verification checklist from `CLAUDE.md`" but `CLAUDE.md` has no such checklist and never did. Worth a follow-up if you want that step to actually do something.

**Next step**: open a PR from `feature/SCRUM-17-cleanup-stale-artifacts` into `dev` when ready, or continue directly with `centralize-config-and-private-store` (now unblocked, see below).

## Ready to implement (unblocked): `centralize-config-and-private-store` OpenSpec change (2026-09-22)

Location: `openspec/changes/centralize-config-and-private-store/`
Status: **planning complete, ready to implement now** (0/42 tasks; `skip_specs: true` — pure infra/organization change, no capability behavior delta of its own). Passes `openspec validate --changes centralize-config-and-private-store --strict`. **Previously blocked on `cleanup-legacy-docs-and-apply-pipeline` — that dependency is now resolved** (cleanup shipped and archived 2026-09-22). One small stale reference already fixed during cleanup: `tasks.md` 6.5's "if kept per sibling change's decision" conditional on `/scan-inbox` was resolved (deleted, not kept) and the task text updated accordingly — worth a quick read of that task before implementing 6.x.

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

## Ready to implement (unblocked): `headhunter-agent` OpenSpec change (2026-09-21)

Location: `openspec/changes/headhunter-agent/`
Status: **planning complete, ready to implement now** (0/22 tasks). Proposal, design, 3 specs, and task list are done and validated. **Previously blocked on `cleanup-legacy-docs-and-apply-pipeline` — now unblocked**: `openspec/specs/job-application/spec.md` exists (fit gate, markdown output, `applications/YYYY-MM_Company/` location, reviewer loop, no-fabrication rule) for resume-bullet-diff requests to target.

**Scope**: Three new capabilities for HIGH_FIT/FIT roles and OFFER/FINAL_ROUND opportunities:
- `opportunity-positioning`: Score against positioning-specific rubric (title/level fit, dual-threat, domain, comp signal, tech stack), draft positioning rationale + resume bullet diffs
- `interview-negotiation-prep`: Three-lens adversarial interview simulation (hiring manager / peer / bar raiser) + negotiation talking points
- `evidence-verification`: Block any drafted claim not traced to `data/profile.md`

**Resolved (2026-09-22)**: target compensation band is defined in `data/profile.md` ("Target Roles & Industries" section: `$200K-$300K` total comp), confirmed current by the user — no longer an open input. `proposal.md`, `tasks.md` (1.1, 3.5), and `design.md` (Non-Goals, Risks, Open Questions) updated to reflect this via `/opsx:update`.

**Possible overlap to check before implementing**: `data/positioning_rubric.md` (see "Untracked" section below) may be intended as this change's positioning-scoring rubric — resolve that scope question first.

**Next step**: Implement this change per its tasks.md.

---

## Independent: `eval-dashboard` OpenSpec change (planning phase, 2026-09-18)

Location: `openspec/changes/eval-dashboard/`
Status: **planning complete, 0/68 tasks implemented** (2026-09-18). Proposal, design, both specs, and task list are done and validated. **Independent** — does not block or depend on other changes; deferred pending application decisions.

**Scope**: Multi-page HTML dashboard (evaluations browser + applied-jobs tracker) reading from `data/job_evaluations.json` and `job_search_tracker.csv`. Single-file vanilla JS/CSS, no backend, works offline in a browser.

**Key design decision**: Applied-jobs matching uses a vendor-aware composite key (vendor prefix `LKD`/`IND` + canonical job ID extracted from URL) instead of raw-URL string matching, because tracking parameters in LinkedIn/Indeed alert URLs can differ from what's later pasted in the tracker, even for the same job.

**Completed pre-work (loose ends fixed, 2026-09-18)**:
- `job_search_tracker.csv`: added required `url` column header and populated the Trace3 row with its LinkedIn URL
- `data/job_evaluations.json`: normalized Celonis (4413352108) and FTI Consulting (4421660792) URLs from full tracking-param form to canonical short form
- `tools/fetch_inbox.py`: added `extract_indeed_job_id()` and `normalize_indeed_url()` functions; applied them at Indeed URL ingestion time (same pattern as LinkedIn)

**Next step**: User wants to apply to a few high-fit roles first so the dashboard has real application data to work with. Deferred pending cleanup landing + targeted applications from top 11 high-fit targets (SCRUM-12).

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

## Deferred: `fix-failed-evals` skill

**Status**: Deliberately deferred (2026-09-22) — `data/job_evaluations.failed.json` doesn't currently exist (no accumulated failures). User decided to wait until failures actually land there again before building the retry tool, rather than build against a guessed schema now.

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

## Ready to implement (unblocked): `profile-caching-optimization` OpenSpec change (2026-09-22)

Location: `openspec/changes/profile-caching-optimization/`
Status: **planning complete, ready to implement now** (0/16 tasks across 6 sections). Proposal, one modified + one new requirement in a `job-evaluation` delta spec, design, and tasks are all done. Passes `openspec validate --changes profile-caching-optimization --strict`. Standalone/independent — no dependency on `centralize-config-and-private-store`, `headhunter-agent`, or `eval-dashboard`.

**Why this exists**: `data/profile.md` (139 lines, ~10KB, ~2,000-2,500 tokens) is read in full by 4 separate evaluator entry points, most wastefully by the Gemini API fallback which embeds it in *every per-job* prompt (not once per batch). At current volume (850+ evaluations run) this is a real recurring cost.

**Scope**:
- New `tools/extract_profile.py` — rule-based (non-LLM) extractor generating `data/profile.cache.json` (checked into git).
- Freshness guarantee via a SHA-256 content hash stored in the cache's `_meta` (not mtime — git doesn't preserve mtimes across clones), checked via `extract_profile.py --check`.
- Auto-regeneration on staleness for the Gemini API path (it's code, so it self-heals); interactive-agent paths (`.claude/agents/job-evaluator.md`, `.agents/agents/job-evaluator.agent.md`, `.gemini/GEMINI.md`) are instructed to run the check-then-regenerate themselves via their shell tool.
- **Key design constraint**: the cache is NOT a fully re-structured metadata blob — `company_fit`/`growth_potential` score against `profile.md`'s narrative sections (Behavioral Profile, Key AI-Driven Projects, etc.), so those stay near-verbatim in the cache. Only the multi-decade job-history section gets meaningfully condensed (current role kept in full, pre-2020 roles collapsed to one line each).
- Extractor fails loudly (non-zero exit) on unrecognized `profile.md` section structure, so future profile.md restructuring can't silently degrade the cache.

**Side finding surfaced while researching this change**: `data/profile.md` already has a `Target Compensation Band: $200K-$300K (total comp)` line (under "Target Roles & Industries") — this may resolve the `headhunter-agent` change's noted blocker ("target compensation band not yet defined — negotiation prep cannot be considered usable"). Worth checking whether that's actually current/accurate before treating it as resolved.

**Next step**: implement per `tasks.md` (extractor → generate+commit initial cache → wire Gemini API fallback → wire 3 interactive-agent instruction files → grep cross-check for stragglers → live verification batches on both paths).

## Untracked: `data/positioning_rubric.md`

A new positioning-scoring rubric for HIGH_FIT/FIT roles (distinct from job-evaluation rubric) was created but is untracked. Its scope is unclear:
- Is this part of **headhunter-agent** (SCRUM-16) scope? (looks like it could be the `career-advisor` subagent's rubric)
- Or a standalone new capability?

**Decision needed**: Determine if this should be:
- Integrated into `headhunter-agent`'s design.md + specs as the positioning-scoring rubric (task 2 under `opportunity-positioning` spec)
- Scoped as a separate change
- Archived for later review

**Current**: file is in working directory but untracked; don't commit until scope is decided.

---

## Dropped this session

- `/statusline` setup — no PS1 config found on this Windows machine at Unix-style paths; user chose to drop it rather than provide an alternate path or describe the desired status line content. Not pursued further; revisit only if asked again.
