## Why

The job evaluation system generates detailed JSON data on candidate-job fit across multiple dimensions, but users lack visibility into both evaluated opportunities and application decisions. Currently, evaluations are stored in raw JSON and applications are tracked manually in a CSV—requiring manual cross-reference. An integrated dashboard provides immediate visibility into fit scores, allows browsing and filtering evaluated jobs, and connects submitted applications back to their evaluation data for post-application analysis and tracking.

**Note (2026-09-22):** `tools/generate_mockup.py` already exists and produces a working interim dashboard (`_brief/mockup.html`) — a Python-generated single-file HTML with real KPIs, a fit-category donut, a computed tech-stack chart, and an application-tracker table, all computed from `data/job_evaluations.json` and `job_search_tracker.csv` (no hardcoded/placeholder values as of this note — see its git history for the pre-2026-09-22 version, which had several). It satisfies the immediate need to review tracking today. It is a simpler architecture than this proposal's MVP (regenerate-by-rerunning-the-script vs. this design's dynamic `fetch()`-based live reload, single evaluations-only view vs. this design's two-page evaluations+applied-jobs-with-URL-matching), not a replacement for it. Treat it as the interim/v0 tool while this change's fuller design remains the target for the two-page, live-reloading, exportable version. See `design.md` - Interim Artifact for how they relate.

## What Changes

- **New**: Multi-page HTML dashboard application with evaluation browser and application tracker
- **Page 1 - Evaluations**: Dynamically loads and displays all evaluated jobs with interactive filtering, sorting, and detail views
- **Page 2 - Applied Jobs**: Timeline view of submitted applications with evaluation data overlaid (fit scores, strengths, gaps) via click/hover popups
- **New**: Summary metrics panel (high/medium/low counts, top skill gap patterns)
- **New**: CSV data integration to match applied jobs to their evaluations via a vendor-aware job key extracted from URL (LinkedIn, Indeed)
- **New**: Multi-filter interface supporting fit level, date range, and application status
- Jobs are displayed with color-coded fit indicators and real-time search/filter updates
- **New**: `private/job_evaluations.json` becomes the linking hub for a job's entire lineage, not just its fit score. Its record schema gains optional fields — `application_status`, `application_folder`, `strategy_path`, `positioning_score`, `interview_prep_last_run_at` — populated as a job progresses through later pipeline stages, so the dashboard can trace a job's full history (fetched → evaluated → positioned → applied → interviewed → outcome) from one file instead of joining across `inbox_queue.json`, the tracker CSV, and the applications folder every time.
- **New**: Every stage that already has a fixed orchestrating skill/command (`/fetch-inbox` for evaluation, `/apply` and `generate-application-strategy` for positioning/application) upserts its fields into the matching `job_evaluations.json` record via a shared merge mechanism, keyed by the same vendor+canonical-id composite key `applied-jobs-tracker` already uses for URL matching (not raw URL string, which drifts between capture points — see design.md Decision 8's precedent).
- **New**: The Applied Jobs page shows each job's current lineage stage and, when `application_folder` is present, a clickable link that opens `private/applications/YYYY-MM_Company/` directly (a `file://` or relative link, consistent with the dashboard's no-backend design).

## Capabilities

### New Capabilities
- `job-evaluation-dashboard`: Frontend dashboard that ingests job evaluation JSON data and provides interactive visualization with filtering, sorting, and detail views. Supports dynamic data loading and real-time updates when underlying JSON changes.
- `applied-jobs-tracker`: Application tracking view that loads submitted jobs from CSV, matches them to evaluations by URL, and displays a timeline with filterable applied jobs. Detail popups show full evaluation data (fit scores, strengths, gaps, recommendations). Supports filtering by fit level, application date range, and status.

### Modified Capabilities
- `job-evaluation`: Adds optional lineage fields to the persisted evaluation record schema and a requirement that they are upserted only via the existing merge mechanism (extended to key on the vendor+canonical-id composite key for cross-artifact joins), never by overwriting fields another stage owns.
- `job-application`: Adds a requirement that `/apply` upserts `application_status`, `application_folder`, and (once generated) `strategy_path` into the matching `job_evaluations.json` record after writing application files.
- `opportunity-positioning`: Adds a requirement that whichever orchestrator invokes `career-advisor` (`/apply`, `generate-application-strategy`) upserts `positioning_score` and `strategy_path` into the matching record.
- `interview-negotiation-prep`: Adds a requirement that `deal-architect`'s output names the ledger update (`interview_prep_last_run_at`) for the invoking session to record — no dedicated command wraps this capability today, so the write stays outside the agent itself, consistent with its existing "does not modify any file" behavior.

## Impact

- **Affected Code**: Creates new `dashboard.html` file (standalone, no backend required). Adds a shared upsert mechanism (extending `tools/evaluate_jobs_gemini.py`'s existing merge logic, or a small new shared module) usable by `/apply`, `generate-application-strategy`, and future callers. Updates `.claude/commands/apply.md`, `.agents/skills/generate-application-strategy/SKILL.md`, `.claude/skills/generate-application-strategy.md`, and `.claude/agents/deal-architect.md` (+ Antigravity equivalents) to call it or reference it.
- **Data**: Reads from `private/job_evaluations.json` and `private/job_search_tracker.csv` (existing files; schema gains optional fields, no breaking changes to required fields).
- **UI/UX**: New user-facing interface for job exploration and lineage tracing.
- **Dependencies**: Vanilla JavaScript + lightweight CSS (no external frameworks required for MVP).
- **Scope**: Frontend dashboard plus the minimal write-back plumbing needed to populate the ledger fields it displays — does not change the fit-evaluation rubric, the positioning rubric, or the interview-simulation logic themselves.
