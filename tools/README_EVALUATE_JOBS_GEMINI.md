# evaluate_jobs_gemini.py

Evaluates and filters job postings from `data/inbox_queue.json` against your candidate profile using **Google Gemini AI** or **Agent Session Mode**. Scores each role across five dimensions and saves structured results with fit categories and recommendations.

---

## Modes of Operation

### 1. Agent Evaluation Mode (Recommended — No API Key Required)
Filter inbound job postings by date range and let the session AI agent evaluate them directly:

```bash
# Filter jobs for the past 2 weeks (14 days)
python tools/evaluate_jobs_gemini.py --days 14 --filter-only

# Filter jobs for a specific date range
python tools/evaluate_jobs_gemini.py --start-date 2026-06-01 --end-date 2026-06-30 --filter-only
```

Once evaluated by the Agent, save the evaluations back into `data/inbox_queue.json` and `data/job_evaluations.json`:

```bash
python tools/evaluate_jobs_gemini.py --save-evaluations path/to/evaluations.json
```

---

### 2. External Gemini API Mode (Requires API Key)
Evaluates pending jobs in bulk via Google Gemini API:

```bash
# Evaluate past 14 days of jobs using Gemini API
python tools/evaluate_jobs_gemini.py --days 14

# Evaluate all pending jobs regardless of date
python tools/evaluate_jobs_gemini.py --all-dates
```

---

### 3. Submission & Application Tracking
Log job applications and mark items in the queue as `applied`:

```bash
python tools/evaluate_jobs_gemini.py --track-applied "https://www.linkedin.com/jobs/view/123456" --company "Acme Corp" --role "Director of Data"
```

This will:
1. Update `"status": "applied"` in `data/inbox_queue.json`.
2. Append a row to `job_search_tracker.csv`.

---

## Command Line Arguments

| Flag | Description | Example |
|---|---|---|
| `--days N`, `-d N` | Filter jobs fetched in the past N days | `--days 14` |
| `--start-date YYYY-MM-DD` | Filter jobs on or after start date | `--start-date 2026-06-01` |
| `--end-date YYYY-MM-DD` | Filter jobs on or before end date | `--end-date 2026-06-30` |
| `--all-dates` | Disable date filtering (process all pending jobs) | `--all-dates` |
| `--filter-only` | Output filtered JSON for Agent evaluation without calling API | `--filter-only` |
| `--save-evaluations PATH` | Ingest JSON file containing evaluation results | `--save-evaluations evals.json` |
| `--track-applied URL` | Mark job as applied and record row in `job_search_tracker.csv` | `--track-applied "https://..."` |
| `--all-jobs` | Include already-evaluated jobs in filtering output | `--all-jobs` |

---

## Required Files

| File | Description |
|---|---|
| `data/profile.md` | Your candidate profile (skills, experience, preferences) |
| `data/inbox_queue.json` | List of job postings to evaluate (from `fetch_inbox.py`) |
| `data/job_evaluations.json` | Flat list of all evaluations for quick review |
| `job_search_tracker.csv` | Master application spreadsheet |

---

## Evaluation Output Schema

Each evaluation record stored in `data/inbox_queue.json` and `data/job_evaluations.json` includes:

```json
{
  "title": "VP of Data Engineering",
  "company": "Acme Corp",
  "skill_match": 90,
  "experience_level_match": 85,
  "company_fit": 80,
  "growth_potential": 88,
  "red_flags": 5,
  "overall_fit": 87,
  "fit_category": "high",
  "key_strengths": ["Fabric expertise", "Cloud-native stack", "Leadership scope"],
  "skill_gaps": ["Kafka experience preferred"],
  "red_flags_list": [],
  "recommendation": "Strong match - VP+ title in modern data stack. Consider applying.",
  "reason_summary": "...",
  "url": "https://...",
  "evaluated_at": "2026-06-29T01:30:00",
  "model": "gemini-2.5-flash"
}
```

---

## Fit Categories

| Category | Score | Meaning |
|---|---|---|
| **high** | 80–100 | Strong match — prioritize applying |
| **medium** | 60–79 | Decent fit — worth considering |
| **low** | 40–59 | Weak match — only if pipeline is thin |
| **skip** | < 40 | Deal-breakers present — skip |

---

## Related Tools

| Script | Purpose |
|---|---|
| `tools/fetch_inbox.py` | Fetches job postings into `inbox_queue.json` |
| `tools/evaluate_jobs.py` | Evaluation using Claude API |
| `job_search_tracker.csv` | Master job submission tracking spreadsheet |
