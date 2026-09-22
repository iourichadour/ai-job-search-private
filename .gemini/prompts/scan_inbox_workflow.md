# 📩 Gemini Job Inbox Scan & Evaluation Prompt

Execute the deterministic Job Scout workflow to process Gmail job alerts and evaluate candidate-job fit:

1. **Scan & Scrape**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate Fit via Interactive Agent Session (Primary — No API Key Required)**:
   *If skipping or bypassing the fetch step, do not restrict evaluation to today; inspect `data/inbox_queue.json` and evaluate all pending jobs (`status: 'pending_evaluation'`) across all dates or the desired window.*
   
   Prepare batches:
   ```bash
   python tools/evaluate_jobs_gemini.py --prepare-batches
   ```
   - In **Antigravity (`agy`)**: delegate scoring to the dedicated `job-evaluator` subagent via `invoke_subagent` (pinned `Model: "pro"`). Tag records `"model": "antigravity-agent-session"`. The subagent writes directly to `data/eval_batches/batch_XX.evaluated.json`.
   - In **Standalone Gemini CLI**: score jobs inline against `data/profile.md` using the fixed 5-dimension rubric. Tag records `"model": "gemini-agent-session"`. Write directly to `data/eval_batches/batch_XX.evaluated.json`.
   - Merge back all evaluated batches:
   ```bash
   python tools/evaluate_jobs_gemini.py --save-evaluations "data/eval_batches/*.evaluated.json"
   ```
   *(Note: Calling `python tools/evaluate_jobs_gemini.py` with external Gemini API is strictly a headless fallback for unattended pipelines, not for interactive agent sessions.)*

3. **Present Summary Table**:
   Read `data/job_evaluations.json` and output a markdown table sorted by fit score descending. Highlight top matches (80%+ fit).
