---
name: scan-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, extracts posting details, filters by date range, and evaluates job fit against candidate profile using Agent-in-Session or Gemini API.
user-invocable: true
disable-model-invocation: false
---

# Scan Inbox & Evaluate Jobs Workflow

Use this skill when asked to check inbox for new jobs, scan job alerts, filter job postings for the past 2 weeks (or specified date range), or evaluate job opportunities from Gmail.

## Procedure

1. **Fetch Inbox Alerts**:
   Run `python tools/fetch_inbox.py` to poll Gmail and scrape posting text into `data/inbox_queue.json`.

2. **Filter & Evaluate Jobs**:
   You can evaluate jobs using **Agent Session Mode** (default / no API key required) or **API Mode** (bulk API calls):

   - **Option A: Agent Evaluation Mode (Recommended / No API Key Required)**:
     1. Export unevaluated jobs without calling external API:
        ```bash
        python tools/evaluate_jobs_gemini.py --days 14 --filter-only
        ```
     2. Delegate evaluation to the dedicated `job-evaluator` subagent via `invoke_subagent`:
        - `TypeName: "job-evaluator"`
        - `Model: "pro"` (pinned to Gemini 2.5 Pro for deep executive discernment; `flash` can be used for bulk sweeps)
        - Pass the exported jobs and `data/profile.md`
        - The subagent returns structured evaluation records tagged `"model": "antigravity-agent-session"`.
     3. Write the evaluation records JSON array to scratch file `data/.tmp_agent_evals.json`, then merge into queue:
        ```bash
        python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json
        ```

   - **Option B: External Gemini API Mode**:
     If `GEMINI_API_KEY` is set, run:
     ```bash
     python tools/evaluate_jobs_gemini.py --days 14
     ```

3. **Present Summary & Submission Tracking**:
   - Read `data/job_evaluations.json` and present a structured markdown table of evaluated opportunities sorted by fit percentage.
   - When user applies to a job, log the submission by running:
     ```bash
     python tools/evaluate_jobs_gemini.py --track-applied "JOB_URL_OR_TITLE" --company "COMPANY" --role "ROLE"
     ```
