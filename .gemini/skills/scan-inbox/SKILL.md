---
name: scan-inbox
description: Polls Gmail for unread LinkedIn/Indeed job alerts, extracts posting details, and evaluates job fit against candidate profile via an interactive agent or Gemini CLI session.
user-invocable: true
disable-model-invocation: false
---

# Scan Inbox & Evaluate Jobs Skill (Gemini / Antigravity)

## Execution Steps

1. Run `python tools/fetch_inbox.py`
2. Export unevaluated jobs without calling any external API:
   ```bash
   python tools/evaluate_jobs_gemini.py --days 14 --filter-only
   ```
3. Score each job against `data/profile.md` using the fixed 5-dimension rubric:
   - **In Antigravity (`agy`)**: Delegate scoring to the `job-evaluator` subagent via `invoke_subagent` (Model: `pro`). Tag records `"model": "antigravity-agent-session"`.
   - **In Standalone Gemini CLI**: Score jobs inline against `data/profile.md` using the configured model from `.gemini/settings.json` (`gemini-2.5-pro`). Tag records `"model": "gemini-agent-session"`.
4. Write the evaluations as a JSON array to a scratch file (e.g. `data/.tmp_agent_evals.json`), then merge it back:
   ```bash
   python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json
   ```
5. Present markdown summary table from `data/job_evaluations.json`
