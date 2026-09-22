# 📩 Job Inbox Scan & Evaluation Deterministic Workflow Prompt

You are tasked with executing the deterministic Job Scout workflow to process Gmail job alerts and evaluate candidate-job fit. Follow these steps strictly in order:

## Workflow Execution Steps

### 1. Fetch Inbox Alerts & Scrape Posting Details
Execute the inbox fetcher script:
```bash
python tools/fetch_inbox.py
```
- Authenticates with Gmail API using `credentials.json` / `data/token.json`.
- Polls for unread emails from LinkedIn (`jobalerts-noreply@linkedin.com`) and Indeed (`alert@indeed.com`).
- Extracts posting URLs, deduplicates them, and fetches full job descriptions using Playwright headless browser.
- Saves pending jobs to `data/inbox_queue.json`.

### 2. Evaluate Pending Jobs against Profile
**Primary: Interactive-Agent Evaluation (Standard — no external API calls).**

*If skipping or bypassing the fetch step, do not restrict evaluation to today; inspect `data/inbox_queue.json` and evaluate all pending jobs (`status: 'pending_evaluation'`) across all dates or the desired window.*

Prepare batches:
```bash
python tools/evaluate_jobs_gemini.py --prepare-batches
```
- Reads candidate profile from `data/profile.md`.
- The interactive agent scores each pending job across 5 criteria:
  1. Technical Skill Match (Microsoft Fabric, Snowflake, Power BI, Python, SQL)
  2. Experience Level Match (Director/VP/Principal alignment, team leadership)
  3. Company & Industry Fit (Financial Services, Tech, Consulting, SaaS)
  4. Growth Potential (Leadership, strategic impact, innovation)
  5. Red Flags (Legacy stack, siloed IT, pure operational maintenance)
- **Subagent delegation**:
  - In **Antigravity (`agy`)**: delegate scoring to the dedicated `job-evaluator` subagent via `invoke_subagent` (pinned `Model: "pro"`). Tag records `"model": "antigravity-agent-session"`. The subagent writes directly to `data/eval_batches/batch_XX.evaluated.json`.
  - In **Claude Code**: delegate scoring to the `job-evaluator` subagent (pinned `model: haiku`). Tag records `"model": "claude-agent-session"`. The subagent writes directly to `data/eval_batches/batch_XX.evaluated.json`.
  - In **Standalone Gemini CLI**: score jobs inline against `data/profile.md` using the configured model. Tag records `"model": "gemini-agent-session"`. Write directly to `data/eval_batches/batch_XX.evaluated.json`.
- Merge back all evaluated batches:
```bash
python tools/evaluate_jobs_gemini.py --save-evaluations "data/eval_batches/*.evaluated.json"
```
- Validates and saves evaluations with fit scores, strengths, gaps, and recommendations to `data/job_evaluations.json`.

> [!NOTE]
> **Headless Fallback Only**: `python tools/evaluate_jobs_gemini.py` with no flags requires `GEMINI_API_KEY` and is reserved strictly as a secondary fallback for unattended/headless cron jobs, never as the default in agent sessions.

### 3. Present Results Table
Read `data/job_evaluations.json` and render a formatted summary table sorted by `overall_fit` descending. Detail top matches (80%+ fit) with key strengths, gaps, and recommended actions.
