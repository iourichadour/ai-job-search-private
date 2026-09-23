---
name: fetch-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, fetches job posting content from URLs, and evaluates fit against candidate profile.
user-invocable: true
disable-model-invocation: true
---
## What This Skill Does
1. Authenticates with Gmail API and polls for unread emails from LinkedIn and Indeed
2. Extracts job posting URLs from email alerts
3. Fetches the actual job description from LinkedIn and Indeed job pages
4. Stores extracted jobs with title, description, and source in `private/inbox_queue.json`
5. Evaluates each pending job's fit against the candidate profile via an interactive-agent round trip and persists the structured evaluations

## How to Use
1. Execute the python script located at `tools/fetch_inbox.py`:
   ```bash
   python tools/fetch_inbox.py
   ```

2. Export unevaluated jobs without calling any external API:
   ```bash
   python tools/evaluate_jobs_gemini.py --days 14 --filter-only
   ```

3. Invoke the `job-evaluator` subagent (pinned `model: haiku`) in a single batched call, passing it the exported jobs and `private/profile.md`. It scores each job against the fixed 5-dimension rubric (skill_match, experience_level_match, company_fit, growth_potential, red_flags) and returns a JSON array of evaluation records tagged `"model": "claude-agent-session"`.

4. Write the subagent's JSON array output to a scratch file (e.g. `private/.tmp_agent_evals.json`), then merge it back into `private/inbox_queue.json` and `private/job_evaluations.json`:
   ```bash
   python tools/evaluate_jobs_gemini.py --save-evaluations private/.tmp_agent_evals.json
   ```

5. Summarize the persisted evaluations in chat with: skills fit %, experience match, fit category, and recommendation (strong/moderate/pass) — read from `private/job_evaluations.json`, sorted by fit percentage.
