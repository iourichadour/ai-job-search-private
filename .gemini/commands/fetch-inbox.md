---
description: Fetch unread job alert emails from Gmail and evaluate fit against profile
---

# /fetch-inbox

Execute the deterministic inbox scanning and job evaluation pipeline:

1. **Poll Gmail and scrape job postings**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate job fit via interactive agent**:
   1. Export unevaluated jobs without calling any external API:
      ```bash
      python tools/evaluate_jobs_gemini.py --days 14 --filter-only
      ```
   2. Score the exported jobs against `private/profile.md` using the fixed 5-dimension rubric:
      - **In Antigravity (`agy`)**: Delegate scoring to the `job-evaluator` subagent via `invoke_subagent` pinned to `Model: "pro"`. Tag records `"model": "antigravity-agent-session"`.
      - **In Standalone Gemini CLI**: Score jobs inline against `private/profile.md` using the configured model from `.gemini/settings.json` (`gemini-2.5-pro`). Tag records `"model": "gemini-agent-session"`.
   3. Write evaluation records as a JSON array to scratch file `private/.tmp_agent_evals.json`, then merge back:
      ```bash
      python tools/evaluate_jobs_gemini.py --save-evaluations private/.tmp_agent_evals.json
      ```

3. **Present evaluations**:
   Read `private/job_evaluations.json` and present a structured summary table sorted by fit percentage.
