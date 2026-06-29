# evaluate_jobs_gemini.py

Evaluates job postings from `data/inbox_queue.json` against your candidate profile using **Google Gemini AI**. Scores each role across five dimensions and saves structured results with fit categories and recommendations.

---

## Prerequisites

- Python 3.8+
- A Google Gemini API key → [Get one free at Google AI Studio](https://aistudio.google.com/apikey)

---

## Installation

```bash
pip install google-genai
```

---

## Configuration

### 1. Set your API key (required)

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Mac / Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

> **Tip:** Add the export line to your `.bashrc` / `.zshrc` / PowerShell profile so you don't have to set it every session.

---

### 2. Choose a model (optional)

The default model is `gemini-2.5-flash` — fast and cost-effective for bulk evaluation. Override it via the `GEMINI_MODEL` environment variable:

| Model | When to use |
|---|---|
| `gemini-2.5-flash` *(default)* | Fast, cheap — good for batches of 20+ jobs |
| `gemini-2.5-pro` | Slower, deeper reasoning — use for borderline roles |

**Windows (Command Prompt):**
```cmd
set GEMINI_MODEL=gemini-2.5-pro
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_MODEL = "gemini-2.5-pro"
```

**Mac / Linux:**
```bash
export GEMINI_MODEL=gemini-2.5-pro
```

---

## Required Files

The script expects these files relative to where you run it (project root):

| File | Description |
|---|---|
| `data/profile.md` | Your candidate profile (skills, experience, preferences) |
| `data/inbox_queue.json` | List of job postings to evaluate (from `fetch_inbox.py`) |

---

## Usage

Run from the **project root** directory:

```bash
python tools/evaluate_jobs_gemini.py
```

The script will:
1. Load your profile from `data/profile.md`
2. Find all jobs in `data/inbox_queue.json` that haven't been evaluated yet
3. Evaluate each one with Gemini and print a live progress summary
4. Save results back into both data files

---

## Output

### Console output (live)
```
[+] Using model: gemini-2.5-flash
[+] Loading candidate profile...
[+] Loading job queue...
[+] Found 12 jobs to evaluate

[1/12] Acme Corp - VP of Data Engineering
    [→] Evaluating with Gemini (gemini-2.5-flash)...
    [✓] Fit: 87% (high)
    📋 Strong match - modern cloud stack with Fabric/Snowflake. Strongly consider.
...

[📊] Summary:
  High Fit (80+):     4 jobs
  Medium Fit (60-79): 5 jobs
  Low Fit (40-59):    2 jobs
  Skip (<40):         1 jobs

[🎯] Top Recommendations:
  87% - Acme Corp - VP of Data Engineering
  84% - FinTech Inc - Principal Data Architect
```

### Saved files

| File | Contents |
|---|---|
| `data/inbox_queue.json` | Original jobs + `evaluation` field added to each |
| `data/job_evaluations.json` | Flat list of all evaluations for quick review |

Each evaluation record includes:

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

## Re-evaluating Jobs

The script only evaluates jobs that **don't already have** an `evaluation` field. To re-evaluate a job, remove its `evaluation` key from `data/inbox_queue.json` and re-run the script.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `google-genai SDK not installed` | Run `pip install google-genai` |
| `GEMINI_API_KEY not set` | Set the env variable (see [Configuration](#configuration)) |
| `data/profile.md not found` | Run from the project root, not from `tools/` |
| `data/inbox_queue.json not found` | Run `fetch_inbox.py` first to populate the queue |
| API quota / rate limit errors | Add a short `time.sleep(2)` between jobs, or switch to `gemini-2.5-pro` with higher quota |

---

## Related Tools

| Script | Purpose |
|---|---|
| `tools/fetch_inbox.py` | Fetches job postings into `inbox_queue.json` |
| `tools/evaluate_jobs.py` | Same evaluation using Claude (Anthropic) |
| `tools/build_job_scout.py` | Broader job discovery pipeline |
