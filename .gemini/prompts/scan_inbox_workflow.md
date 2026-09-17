# 📩 Gemini Job Inbox Scan & Evaluation Prompt

Execute the deterministic Job Scout workflow to process Gmail job alerts and evaluate candidate-job fit:

1. **Scan & Scrape**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate Fit via Interactive Agent Session** (default, no API key required):
   ```bash
   python tools/evaluate_jobs_gemini.py --days 14 --filter-only
   ```
   Score every exported job yourself, in this session, against `data/profile.md` using the fixed 5-dimension rubric (skill_match, experience_level_match, company_fit, growth_potential, red_flags → weighted `overall_fit` → thresholded `fit_category`). Tag every record `"model": "gemini-agent-session"`. Write the evaluations as a JSON array to a scratch file, then merge them back:
   ```bash
   python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json
   ```
   **Fallback** (requires `GEMINI_API_KEY`): run `python tools/evaluate_jobs_gemini.py` with no flags to evaluate via the Gemini API directly.

3. **Present Summary Table**:
   Read `data/job_evaluations.json` and output a markdown table sorted by fit score descending. Highlight top matches (80%+ fit).
