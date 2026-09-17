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
**Default: interactive-agent evaluation (no external API key required).**

Export unevaluated jobs first:
```bash
python tools/evaluate_jobs_gemini.py --days 14 --filter-only
```
- Reads candidate profile from `data/profile.md`.
- The interactive agent scores each pending job across 5 criteria:
  1. Technical Skill Match (Microsoft Fabric, Snowflake, Power BI, Python, SQL)
  2. Experience Level Match (Director/VP/Principal alignment, team leadership)
  3. Company & Industry Fit (Financial Services, Tech, Consulting, SaaS)
  4. Growth Potential (Leadership, strategic impact, innovation)
  5. Red Flags (Legacy stack, siloed IT, pure operational maintenance)
- On the Claude Code side, scoring is delegated to the `job-evaluator` subagent (pinned `model: haiku`), invoked once with the full batch of exported jobs. On the Gemini CLI side, scoring happens inline in the session.
- Write the resulting evaluations as a JSON array to a scratch file (e.g. `data/.tmp_agent_evals.json`), then merge them back:
```bash
python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json
```
- Saves evaluations with fit scores, strengths, gaps, and recommendations to `data/job_evaluations.json`, tagged `"model": "claude-agent-session"` or `"model": "gemini-agent-session"` depending on which agent produced them.

**Fallback: external Gemini API (requires `GEMINI_API_KEY`).** Run `python tools/evaluate_jobs_gemini.py` with no flags to evaluate pending jobs via the Gemini API directly.

### 3. Present Results Table
Read `data/job_evaluations.json` and render a formatted summary table sorted by `overall_fit` descending. Detail top matches (80%+ fit) with key strengths, gaps, and recommended actions.
