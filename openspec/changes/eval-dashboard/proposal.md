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

## Capabilities

### New Capabilities
- `job-evaluation-dashboard`: Frontend dashboard that ingests job evaluation JSON data and provides interactive visualization with filtering, sorting, and detail views. Supports dynamic data loading and real-time updates when underlying JSON changes.
- `applied-jobs-tracker`: Application tracking view that loads submitted jobs from CSV, matches them to evaluations by URL, and displays a timeline with filterable applied jobs. Detail popups show full evaluation data (fit scores, strengths, gaps, recommendations). Supports filtering by fit level, application date range, and status.

### Modified Capabilities
<!-- No existing capabilities are being modified in this change. -->

## Impact

- **Affected Code**: Creates new `dashboard.html` file (standalone, no backend required)
- **Data**: Reads from `data/job_evaluations.json` (existing file, no changes)
- **UI/UX**: New user-facing interface for job exploration
- **Dependencies**: Vanilla JavaScript + lightweight CSS (no external frameworks required for MVP)
- **Scope**: Frontend only—does not modify job evaluation logic or data generation
