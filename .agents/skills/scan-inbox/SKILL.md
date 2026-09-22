---
name: scan-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, extracts posting details, filters by date range, and evaluates job fit against candidate profile interactively in-session using the job-evaluator subagent.
user-invocable: true
disable-model-invocation: false
---

# Scan Inbox & Evaluate Jobs Workflow

Use this skill when asked to check inbox for new jobs, scan job alerts, filter job postings for the past 2 weeks (or specified date range), or evaluate job opportunities from Gmail.

## Procedure

1. **Fetch Inbox Alerts**:
   Run `python tools/fetch_inbox.py` to poll Gmail and scrape posting text into `data/inbox_queue.json`.

2. **Filter & Evaluate Jobs (Interactive Agent Session — Primary)**:
   Always evaluate jobs interactively in-session using the dedicated subagent without external API calls:

   1. Prepare batches of unevaluated jobs without calling external API:
      *(If skipping the fetch step, do not restrict evaluation to today; evaluate all pending jobs in `data/inbox_queue.json` across all dates or the desired window.)*
      ```bash
      python tools/evaluate_jobs_gemini.py --prepare-batches
      ```
   2. Delegate evaluation to the dedicated `job-evaluator` subagent via `invoke_subagent`:
      - `TypeName: "job-evaluator"`
      - `Model: "pro"` (pinned to Gemini 2.5 Pro for deep executive discernment; `flash` can be used for bulk sweeps)
      - Pass the batch files and `data/profile.md`
      - The subagent writes structured evaluation records tagged `"model": "antigravity-agent-session"` directly to `data/eval_batches/batch_XX.evaluated.json`.
   3. Merge evaluated batches into queue:
      ```bash
      python tools/evaluate_jobs_gemini.py --save-evaluations "data/eval_batches/*.evaluated.json"
      ```

   > [!NOTE]
   > **Headless Fallback Only**: `python tools/evaluate_jobs_gemini.py --days 14` (requires `GEMINI_API_KEY`) is reserved strictly as a secondary fallback for non-interactive/headless automated pipelines, not for agent sessions.

3. **Present Summary & Submission Tracking**:
   - Read `data/job_evaluations.json` and present a structured markdown table of evaluated opportunities sorted by fit percentage.
   - When user applies to a job, log the submission by running:
     ```bash
     python tools/evaluate_jobs_gemini.py --track-applied "JOB_URL_OR_TITLE" --company "COMPANY" --role "ROLE"
     ```
