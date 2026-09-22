---
description: Fetch unread job alert emails from Gmail and evaluate fit against profile
---

# /scan-inbox

Execute the deterministic inbox scanning and job evaluation pipeline:

1. **Poll Gmail and scrape job postings**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate job fit via interactive agent**:
   1. Prepare batches of unevaluated jobs without calling any external API:
      *(If skipping the fetch step, do not restrict evaluation to today; evaluate all pending jobs in `data/inbox_queue.json` across all dates or the desired window.)*
      ```bash
      python tools/evaluate_jobs_gemini.py --prepare-batches
      ```
   2. Score the exported jobs against `data/profile.md` using the fixed 5-dimension rubric:
      - **In Antigravity (`agy`)**: Delegate scoring to the `job-evaluator` subagent via `invoke_subagent` pinned to `Model: "pro"`. Tag records `"model": "antigravity-agent-session"`. The subagent writes directly to `data/eval_batches/batch_XX.evaluated.json`.
      - **In Standalone Gemini CLI**: Score jobs inline against `data/profile.md` using the configured model from `.gemini/settings.json` (`gemini-2.5-pro`). Tag records `"model": "gemini-agent-session"`. Write directly to `data/eval_batches/batch_XX.evaluated.json`.
   3. Merge back all evaluated batches:
      ```bash
      python tools/evaluate_jobs_gemini.py --save-evaluations "data/eval_batches/*.evaluated.json"
      ```

3. **Present evaluations**:
   Read `data/job_evaluations.json` and present a structured summary table sorted by fit percentage.
