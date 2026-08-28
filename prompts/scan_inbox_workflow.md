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
Execute the Gemini evaluation script:
```bash
python tools/evaluate_jobs_gemini.py
```
- Reads candidate profile from `data/profile.md`.
- Evaluates pending jobs across 5 criteria:
  1. Technical Skill Match (Microsoft Fabric, Snowflake, Power BI, Python, SQL)
  2. Experience Level Match (Director/VP/Principal alignment, team leadership)
  3. Company & Industry Fit (Financial Services, Tech, Consulting, SaaS)
  4. Growth Potential (Leadership, strategic impact, innovation)
  5. Red Flags (Legacy stack, siloed IT, pure operational maintenance)
- Saves evaluations with fit scores, strengths, gaps, and recommendations to `data/job_evaluations.json`.

### 3. Present Results Table
Read `data/job_evaluations.json` and render a formatted summary table sorted by `overall_fit` descending. Detail top matches (80%+ fit) with key strengths, gaps, and recommended actions.
