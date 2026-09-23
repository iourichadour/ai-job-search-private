# Resume

Snapshot of in-progress work, for picking this back up in a new session (any agent). See `MEMORY.md` for durable project facts/conventions this doesn't repeat.

**Last updated**: 2026-09-23 (`centralize-config-and-private-store` implemented, live-verified, archived, committed on `feature/SCRUM-18-centralize-config-and-private-store` — **not yet pushed or PR'd**, `SCRUM-18` at In Review)

## Next up: push `feature/SCRUM-18-centralize-config-and-private-store` and open a PR

All work is committed locally (3 commits: `981af0b` implementation, `cd00fed` tasks.md completion, `ceb5bce` archive move) but was never pushed — this session's git safety policy is to never push without explicit user request, and none came before the session ended. **Next action**: `git push -u origin feature/SCRUM-18-centralize-config-and-private-store`, open a PR into `dev`, merge, then transition Jira `SCRUM-18` (currently "In Review") to Done with a note that it merged. See the "Completed" section below for full detail on what shipped and two things deliberately left open.

## Deferred: PII in tracked job-application-assistant skill files (surfaced 2026-09-23, not scoped as a change yet)

`.claude/skills/job-application-assistant/01-candidate-profile.md` and `02-behavioral-profile.md` are tracked in git and `/setup` populates them in place with the candidate's real name, phone number, email, and work history — discovered during `centralize-config-and-private-store`'s `documents/` audit, outside that change's (and the sibling cleanup change's) scope. **User's explicit call**: flag as a future follow-up change rather than fix now (this change was already large). Not yet turned into an OpenSpec proposal or a Jira ticket — whoever picks this up needs to touch every command that reads/writes these paths (`/setup`, `/expand`, `/apply`, `/reset`), likely moving their real content to something like `private/candidate-profile.md`/`private/behavioral-profile.md` and leaving a blank template tracked at the current path. Full detail in `MEMORY.md`'s "Private data consolidation" section and `README.md`'s "if you plan to publish your fork" callout.

## Completed (locally, not yet pushed): `centralize-config-and-private-store` OpenSpec change (2026-09-23)

Archived as: `openspec/changes/archive/2026-09-23-centralize-config-and-private-store/`. Branch `feature/SCRUM-18-centralize-config-and-private-store`, cut from `dev`. Jira `SCRUM-18` created under epic `SCRUM-10`, commented with full summary, transitioned To Do → In Review (not Done — not merged yet). All 42 original tasks plus several tasks added mid-session for scope gaps found during implementation — see the archived `tasks.md` for full detail on every task and how it was verified.

**What shipped**:
- New `tools/config.py` (tracked) + `private/config.json` (gitignored, `config.example.json` tracked template at repo root) — the single place every kept script resolves paths/settings from. No `tools/*.py` file (or `salary_lookup.py` at repo root) hardcodes a personal path or the maintainer's email anymore.
- Every personal/job-search artifact moved into `private/`: `profile.md`, `cv/*.md` (6 tailored resumes), `job_search_tracker.csv`, `inbox_queue.json`, `job_evaluations.json`, `fetch_state.json`, `eval_batches/`, `credentials.json`, `token.json`, `documents/{cv,linkedin,diplomas,references,applications}/` real content, `salary_data.json` (path only, file doesn't exist yet), future `/apply` output (`private/applications/YYYY-MM_Company/`).
- `data/` retired except `data/positioning_rubric.md` (tracked, non-personal `headhunter-agent` rubric — user explicitly chose to leave it there rather than relocate it, a design amendment mid-session).
- Deleted `tools/build_job_scout.py` (confirmed via direct question to the user: it was a stale, disconnected bootstrap script that would have overwritten current `CLAUDE.md`/`fetch_inbox.py` with an outdated snapshot if ever run — not part of the real `/setup` onboarding path), plus its only consumers `data/master_resume.md` and `tools/readme_build_job_scout_tool.md`.
- `.gitignore` simplified from ~12 individual personal-data rules down to one `private/` rule.
- `documents/` keeps only `README.md` (rewritten to describe the new layout) and empty `.gitkeep` placeholder subfolders.
- **New, separately-archived OpenSpec change `document-two-phase-fetch-pipeline`** (`openspec/changes/archive/2026-09-23-document-two-phase-fetch-pipeline/`): formalizes the already-shipped-but-unspecced two-phase (collect-then-fetch) `fetch_inbox.py` architecture as a proper `inbox-ingestion` spec requirement. This came out of reviewing and then deleting `documents/plans/` (5 tracked files with real candidate-identifying content, never audited by any prior change) — per explicit user instruction: review, formalize any genuinely-shipped-but-undocumented feature (scrubbed of PII), then delete and untrack the originals. Two of the five plan files described a Power BI Desktop (PBIP) dashboard that was never built (superseded by the HTML dashboard that shipped instead) — noted in the new change's `design.md` for historical record, no fabricated spec for it.
- README.md, SETUP.md, CLAUDE.md, and MEMORY.md all updated to the new `private/` paths (well beyond the minimum ask, since both docs had many more stale references than anticipated from sections not yet touched).
- Live end-to-end verification against real data (not synthetic): `fetch_inbox.py` (auth, dedup against the real 1080-job queue, scratch/log files), `evaluate_jobs_gemini.py --filter-only` and `--prepare-batches`, `generate_mockup.py` (875 evals, 236 high-fit, regenerated `_brief/mockup.html`), `salary_lookup.py`.

**Real mistake caught and fixed mid-session, worth remembering**: ran `fetch_inbox.py` once to test OAuth *before* moving `inbox_queue.json`/`fetch_state.json` into `private/` — the script correctly-per-its-own-logic treated the not-yet-existing `private/inbox_queue.json` as empty and started fetching all 35 scraped URLs as "new," creating a partial 4-job queue before being killed by a timeout. No real data was lost (the authoritative 1080-job `data/inbox_queue.json` was untouched; the partial file was deleted), but the lesson is recorded in `MEMORY.md`: move all related state files together before re-testing a script that reads several of them.

**Also a real, separate gotcha found and fixed**: `job_search_tracker.csv` and `data/job_evaluations.json` were unexpectedly already *tracked* in git (never gitignored) before this change. Plain `git mv` into `private/` kept them tracked at the new path (since `.gitignore` only blocks *new* untracked files) — required a follow-up `git rm --cached -r private/` to actually untrack everything. Recorded in `MEMORY.md` as a convention to apply for any future move of a tracked file into `private/`.

**Two scope gaps found in the original plan, closed with the user's sign-off** (see `tasks.md` 6.7 and 6a, and `design.md`'s amendment note): `salary_lookup.py`/`tools/convert_salary_excel.py` were named in `proposal.md` as in-scope but never actually assigned a task — closed by wiring both to `config.SALARY_DATA_PATH`. `data/positioning_rubric.md` (tracked, non-personal, added by the already-merged `headhunter-agent` change after this change's `design.md` was written) conflicted with the "retire `data/` entirely" goal — resolved by relaxing that goal to "no personal data in `data/`," per user decision.

## Completed & Merged: `headhunter-agent` OpenSpec change (2026-09-22/23)

Archived as: `openspec/changes/archive/2026-09-22-headhunter-agent/`. Branch `feature/SCRUM-16-headhunter-agent` → PR #3 → merged to `dev` 2026-09-23. Jira `SCRUM-16` commented with full summary and transitioned To Do → Done. See prior session detail below (kept for history) — nothing further to do here.

## Completed & Merged: `cleanup-legacy-docs-and-apply-pipeline` OpenSpec change (2026-09-22)

Archived as: `openspec/changes/archive/2026-09-22-cleanup-legacy-docs-and-apply-pipeline/`
Main specs updated: `openspec/specs/job-application/spec.md` (new capability), `openspec/specs/job-evaluation/spec.md` (modified: dropped the scan-inbox mention)
Branch: `feature/SCRUM-17-cleanup-stale-artifacts` — merged to `dev` via PR #2. Jira `SCRUM-17` is Done.
Status: **all 42 tasks complete, archived, merged**.

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

## `centralize-config-and-private-store` OpenSpec change — full scope (planned 2026-09-22, not yet started)

Location: `openspec/changes/centralize-config-and-private-store/`
Status: **planning complete, ready to implement now** (0/42 tasks; `skip_specs: true` — pure infra/organization change, no capability behavior delta of its own). Passes `openspec validate --changes centralize-config-and-private-store --strict`. No longer blocked on anything — both `cleanup-legacy-docs-and-apply-pipeline` and `headhunter-agent` have shipped and merged. One small stale reference already fixed during cleanup: `tasks.md` 6.5's "if kept per sibling change's decision" conditional on `/scan-inbox` was resolved (deleted, not kept) and the task text updated accordingly — worth a quick read of that task before implementing 6.x.

**Why this exists**: follow-up to a "should we adopt a `private/` folder for all private artifacts?" exploratory question — user confirmed yes, and asked to make it larger: every kept Python tool should read paths/settings from one central config instead of hardcoding relative-string literals per script (11 files inventoried in `design.md` - Context).

**Scope, confirmed via direct questions to the user (2026-09-22)**:
- `tools/config.py` (tracked code) + `private/config.json` (gitignored data, `config.example.json` tracked template at repo root) becomes the single source every kept script reads paths/settings from.
- Full `private/` consolidation, not partial: `data/profile.md`, `cv/*.md`, `job_search_tracker.csv`, `credentials.json`, `data/token.json` move in (as previously discussed) — **plus**, per explicit user confirmation, `data/job_evaluations.json`/`.failed.json` (not classic PII, but sensitive-by-association — user chose to move it) and `documents/`'s personal subfolders (`cv/`, `linkedin/`, `diplomas/`, `references/`, `applications/` — currently protected by granular `.gitignore` rules instead of the single-folder pattern; user chose to move these too for consistency). Already-gitignored operational data (`fetch_state.json`, `scratch_*.json`, `eval_batches/`) moves too, for location consistency (not a new privacy decision, since already excluded from git).
- `documents/README.md` and the top-level `documents/` structure stay tracked in place (public setup instructions) — only the personal *content* underneath moves.
- Future `/apply` output redirects from `applications/YYYY-MM_Company/` to `private/applications/YYYY-MM_Company/` — requires editing the sibling change's still-open `job-application` delta spec (or `openspec/specs/job-application/spec.md` directly if that change archives first).
- **`tools/build_job_scout.py` fully owned by this change** (2026-09-22 scoping clarification, mid-session correction from an earlier draft that had it split across both changes): its keep/delete decision, its hardcoded-email fix, and its config/path wiring all happen here, not in `cleanup-legacy-docs-and-apply-pipeline`. That sibling change makes zero edits to it.

**Next step**: see "Next up" at the top of this file — create the Jira ticket, cut the branch, then implement per `tasks.md` (11 sections: prerequisite check, config module, then move-and-rewire in groups — OAuth, candidate data, evaluation data/tracker, `documents/`, future `/apply` output — then `.gitignore` simplification, full verification, single commit).

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

## Completed & Archived: `headhunter-agent` OpenSpec change (2026-09-22)

Archived as: `openspec/changes/archive/2026-09-22-headhunter-agent/`
Main specs added: `openspec/specs/opportunity-positioning/spec.md`, `openspec/specs/interview-negotiation-prep/spec.md`, `openspec/specs/evidence-verification/spec.md` (all new capabilities, 13 requirements total). `openspec validate --all --strict` passes clean (9/9).
Branch: `feature/SCRUM-16-headhunter-agent`, cut from `dev` after `feature/SCRUM-17-cleanup-stale-artifacts` (PR #2) merged. **Still not committed** — all work below (including the archive move itself) is uncommitted in the working tree; commit and open a PR when ready.
Status: **21/22 tasks complete** (task 6.2, the archive command itself, is self-referential and archives at 21/22 by design — this is expected, not a gap).

**Shipped**: 6 new subagent files, all live-verified against real repo data this session (not synthetic test fixtures):
- `.claude/agents/career-advisor.md` (`model: haiku`), `.claude/agents/deal-architect.md` (`model: sonnet`), `.claude/agents/evidence-verifier.md` (`model: sonnet`)
- `.agents/agents/career-advisor.agent.md` (`model: flash`), `.agents/agents/deal-architect.agent.md` (`model: pro`), `.agents/agents/evidence-verifier.agent.md` (`model: pro`) — Antigravity mirrors, confirmed byte-identical to their `.claude/` counterparts apart from the intended `invoke_subagent`/model-tier substitutions.

**Both prior-session blockers resolved**:
1. **Session-restart requirement**: resolved automatically — this session started fresh (via `/clear`), and the agent roster already listed all three new subagents as available. No restart needed once a genuinely new session starts.
2. **Gemini CLI mirroring question**: resolved by direct user decision (2026-09-22) — **Gemini CLI is deprecated and no longer available**, full stop, not just unable to replicate the structurally-independent evidence-verifier pattern. `tasks.md` 2.4/3.7/4.3 and `design.md` updated to drop Gemini mirroring entirely; `MEMORY.md`'s "Three parallel agent ecosystems" section rewritten to "Two parallel agent ecosystems" accordingly. **`.gemini/` files still exist in the repo but are now dead** — flagged as known debt in `MEMORY.md`, not cleaned up here (out of scope for this change).

**Live verification highlights** (all via real Agent-tool subagent invocations, not mocked):
- `career-advisor` scored 3 real HIGH_FIT jobs (Clearwater Analytics, Apollo Global Management, Snowflake) from `data/job_evaluations.json` — all passed evidence verification, verdicts added genuine judgment beyond the score/rationale.
- `deal-architect` ran a full three-lens interview simulation against the real tracked Trace3 opportunity (`job_search_tracker.csv`, status `applied`) — evidence-verifier caught and forced a revision of one real unmapped claim mid-run before presenting; negotiation-prep gate correctly returned `gated_not_ready` (status isn't OFFER/FINAL_ROUND).
- Negative-case test: with status simulated as OFFER but a scratch `profile.md` copy with the compensation band stripped, `deal-architect` correctly returned `blocked_no_comp_band` and fabricated no numbers.
- `evidence-verifier` tested directly: PASS on a profile-grounded draft, BLOCKED on the same draft plus a fabricated "50 engineers across three continents" claim, and confirmed the block survives an explicit re-assertion instruction (per spec's anti-argue-your-way-out requirement).

**Next step**: commit this branch's work (6 new agent files + archived OpenSpec change + `MEMORY.md`/`RESUME.md` updates) and open a PR from `feature/SCRUM-16-headhunter-agent` into `dev` when ready.

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

## Archived: `agy-job-evaluator-subagent` OpenSpec change

Archived as: `openspec/changes/archive/2026-09-22-agy-job-evaluator-subagent/`
Status: **applied, 8/8 tasks complete** (2026-09-17), **archived 2026-09-22**. All tasks across sections 1-4 were done and verified live back in September; archiving was blocked until 2026-09-22 by a stale delta spec (its "Evaluations are tagged by evaluator provenance" MODIFIED block used an older scenario name/wording than the live main spec, which `openspec archive` refuses to silently drop). Fixed by reconciling the delta's two MODIFIED requirements to match the live main spec exactly (a no-op for those two, since the later `interactive-agent-job-evaluation` and `cleanup-legacy-docs-and-apply-pipeline` changes had already superseded that wording) — its one genuinely new `ADDED` requirement ("Dedicated evaluator subagents pinned to specialized models") archived cleanly into `openspec/specs/job-evaluation/spec.md`.

**Side note surfaced while fixing this, not acted on**: the live `job-evaluation` spec's "Interactive-agent evaluation is the primary path" requirement still only mentions Claude Code/Gemini CLI, not `.agents/`/Antigravity — even though Antigravity evaluation is live and working (`antigravity-agent-session` tag, `MEMORY.md`'s "Three parallel agent ecosystems"). Possible spec-completeness gap, not a behavior bug; leave for a future change if it matters.

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

## Deferred: `profile-caching-optimization` OpenSpec change (planned 2026-09-22, deferred 2026-09-22)

Location: `openspec/changes/profile-caching-optimization/`
Status: **planning complete (0/16 tasks across 6 sections), implementation deliberately deferred.** Proposal, one modified + one new requirement in a `job-evaluation` delta spec, design, and tasks are all done and pass `openspec validate --changes profile-caching-optimization --strict`. Standalone/independent — no dependency on `centralize-config-and-private-store`, `headhunter-agent`, or `eval-dashboard` — so it can be picked up any time without re-sequencing other work.

**Why deferred**: the token-savings case is much stronger for the Gemini API fallback path (full profile re-embedded per job, ~423x multiplier in a large run) than for the interactive-agent path (profile read once per batch invocation, not per job — e.g. only 22 reads across SCRUM-12's 423-job/22-batch run). The user's primary evaluation path is the interactive agent, not the API fallback, so the realistic payoff right now is smaller than the proposal originally framed it. Revisit if Gemini-API-fallback usage picks up, or if interactive-agent batch counts grow enough to make the smaller per-batch saving worthwhile.

**Why this exists** (original motivation, still accurate for the API path): `data/profile.md` (139 lines, ~10KB, ~2,000-2,500 tokens) is read in full by 4 separate evaluator entry points, most wastefully by the Gemini API fallback which embeds it in *every per-job* prompt (not once per batch).

**Scope**:
- New `tools/extract_profile.py` — rule-based (non-LLM) extractor generating `data/profile.cache.json` (checked into git).
- Freshness guarantee via a SHA-256 content hash stored in the cache's `_meta` (not mtime — git doesn't preserve mtimes across clones), checked via `extract_profile.py --check`.
- Auto-regeneration on staleness for the Gemini API path (it's code, so it self-heals); interactive-agent paths (`.claude/agents/job-evaluator.md`, `.agents/agents/job-evaluator.agent.md`, `.gemini/GEMINI.md`) are instructed to run the check-then-regenerate themselves via their shell tool.
- **Key design constraint**: the cache is NOT a fully re-structured metadata blob — `company_fit`/`growth_potential` score against `profile.md`'s narrative sections (Behavioral Profile, Key AI-Driven Projects, etc.), so those stay near-verbatim in the cache. Only the multi-decade job-history section gets meaningfully condensed (current role kept in full, pre-2020 roles collapsed to one line each).
- Extractor fails loudly (non-zero exit) on unrecognized `profile.md` section structure, so future profile.md restructuring can't silently degrade the cache.

**Side finding surfaced while researching this change**: `data/profile.md` already has a `Target Compensation Band: $200K-$300K (total comp)` line (under "Target Roles & Industries") — this may resolve the `headhunter-agent` change's noted blocker ("target compensation band not yet defined — negotiation prep cannot be considered usable"). Worth checking whether that's actually current/accurate before treating it as resolved.

**Next step**: none for now — deferred. If picked back up, implement per `tasks.md` (extractor → generate+commit initial cache → wire Gemini API fallback → wire 3 interactive-agent instruction files → grep cross-check for stragglers → live verification batches on both paths).

## Resolved: `data/positioning_rubric.md` scope (was "Untracked", resolved 2026-09-22)

Confirmed as `headhunter-agent`'s `opportunity-positioning` rubric and tracked in git — see that change's section above for details. No longer an open question.

---

## Dropped this session

- `/statusline` setup — no PS1 config found on this Windows machine at Unix-style paths; user chose to drop it rather than provide an alternate path or describe the desired status line content. Not pursued further; revisit only if asked again.
