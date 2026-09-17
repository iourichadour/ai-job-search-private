---
description: Scan Gmail inbox for job alerts, fetch job postings, and evaluate fit against profile
---

# /scan-inbox

Execute the deterministic inbox scanning and job evaluation pipeline:

1. **Poll Gmail and scrape job postings**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate job fit via interactive agent session**:
   1. Export unevaluated jobs without calling any external API:
      ```bash
      python tools/evaluate_jobs_gemini.py --days 14 --filter-only
      ```
   2. Invoke the `job-evaluator` subagent (pinned `model: haiku`) in a single batched call, passing it the exported jobs and `data/profile.md`. It scores every job against the fixed 5-dimension rubric and returns a JSON array of evaluation records tagged `"model": "claude-agent-session"`.
   3. Write the subagent's JSON array output to a scratch file (e.g. `data/.tmp_agent_evals.json`), then merge it back into `data/inbox_queue.json` and `data/job_evaluations.json`:
      ```bash
      python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json
      ```

3. **Present evaluations**:
   Read `data/job_evaluations.json` and present a structured summary table sorted by fit percentage.
