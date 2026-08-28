---
description: Fetch unread job alert emails from Gmail and evaluate fit against profile
---

# /fetch-inbox

Execute the deterministic inbox scanning and job evaluation pipeline:

1. **Poll Gmail and scrape job postings**:
   ```bash
   python tools/fetch_inbox.py
   ```

2. **Evaluate job fit with Gemini AI**:
   ```bash
   python tools/evaluate_jobs_gemini.py
   ```

3. **Present evaluations**:
   Read `data/job_evaluations.json` and present a structured summary table sorted by fit percentage.
