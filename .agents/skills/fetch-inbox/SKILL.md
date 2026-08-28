---
name: fetch-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, extracts posting details, filters by date range, and evaluates job fit against candidate profile using Agent-in-Session or Gemini API.
user-invocable: true
disable-model-invocation: false
---

# Fetch Inbox & Evaluate Jobs Workflow

Use this skill when asked to check inbox for new jobs, scan job alerts, filter job postings for the past 2 weeks (or specified date range), or evaluate job opportunities from Gmail.

## Procedure

1. **Fetch Inbox Alerts**:
   Run `python tools/fetch_inbox.py` to poll Gmail and scrape posting text into `data/inbox_queue.json`.

2. **Filter & Evaluate Jobs**:
   You can evaluate jobs using **Agent Session Mode** (default / no API key required) or **API Mode** (bulk API calls):

   - **Option A: Agent Evaluation Mode (Recommended / No API Key Required)**:
     1. Run `python tools/evaluate_jobs_gemini.py --days 14 --filter-only` (or specify `--start-date YYYY-MM-DD` / `--end-date YYYY-MM-DD`).
     2. Read candidate profile `data/profile.md` and score each candidate job across the 5 evaluation dimensions:
        - **Technical Skill Match** (30%)
        - **Experience Level Match** (25%)
        - **Company/Industry Fit** (20%)
        - **Growth Potential** (15%)
        - **Red Flags** (-10%)
     3. Save evaluations back to queue by invoking:
        `python tools/evaluate_jobs_gemini.py --save-evaluations "<JSON_STRING_OR_FILE>"`
        (This updates `data/inbox_queue.json` job status to `evaluated` and appends to `data/job_evaluations.json`).

   - **Option B: External Gemini API Mode**:
     If `GEMINI_API_KEY` is set, run:
     `python tools/evaluate_jobs_gemini.py --days 14`

3. **Present Summary & Submission Tracking**:
   - Read `data/job_evaluations.json` and present a structured markdown table of evaluated opportunities sorted by fit percentage.
   - When user applies to a job, log the submission by running:
     `python tools/evaluate_jobs_gemini.py --track-applied "JOB_URL_OR_TITLE" --company "COMPANY" --role "ROLE"`
     (This updates `data/inbox_queue.json` status to `applied` and appends a row to `job_search_tracker.csv`).
