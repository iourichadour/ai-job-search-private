# Plan: Power BI Report for Job Evaluations

> **First implementation action: copy this plan to `documents/plans/Power BI Report for Job Evaluations.plan.md`.**

## Context
`data/job_evaluations.json` contains 13 evaluated job postings with numeric scores (0–100), a fit category, and text arrays (strengths, gaps, red flags). The goal is a self-contained PBIP report that gives a visual decision dashboard — surfacing top-ranked roles, comparing scores across all jobs, and drilling into per-job narrative detail.

No Power BI project files exist in the repo; everything is created from scratch.

---

## Step 0 — Fix Root Cause: Sanitize Scraped Text in Python Scripts

**Root cause:** Scraped job descriptions contain `[`, `]`, `{`, `}` characters. When Claude reads these to generate `job_evaluations.json`, those characters confuse the LLM into emitting structurally broken JSON (stray `]` instead of `}` to close objects in 3 entries).

### Changes to both `tools/fetch_inbox.py` and `tools/refetch_jobs_browser.py`

Add a shared `sanitize_text()` helper and apply it to `title`, `company`, and `description` before writing to the queue JSON:

```python
def sanitize_text(text: str) -> str:
    """Strip characters that confuse LLM JSON generation."""
    if not text:
        return text
    # Replace JSON structural chars with neutral equivalents
    text = text.replace('[', '(').replace(']', ')')
    text = text.replace('{', '(').replace('}', ')')
    # Strip control characters (keep newline/tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Collapse excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
```

Apply in `fetch_inbox.py` at the `entry` dict construction (~line 354):
```python
entry = {
    'title': sanitize_text(result['title']) if result else 'N/A',
    'company': sanitize_text(result.get('company', 'N/A')) if result else 'N/A',
    'description': sanitize_text(result['description']) if result else 'Could not extract',
    ...
}
```

Apply identically in `refetch_jobs_browser.py` at the `original_job.update(...)` call (~line 300).

### Also patch `data/job_evaluations.json` directly (one-time fix)
Remove the 3 orphan `]` lines (Clearwater Analytics ~line 96, S&P Global ~line 144, Snowflake ~line 241) so the file is valid JSON immediately — future evaluations won't have this problem once the scripts are patched.

---

## Step 1 — Create PBIP Project Scaffold

Create a new PBIP project at:
```
reports/job-evaluations/
  job-evaluations.pbip
  job-evaluations.SemanticModel/
    definition/
      model.tmdl
      tables/
        Jobs.tmdl
        JobStrengths.tmdl
        JobGaps.tmdl
        JobRedFlags.tmdl
        DateDim.tmdl          ← optional, skip if no date field needed
  job-evaluations.Report/
    definition.pbir
    pages/
      ExecutiveSummary/
      ScoringComparison/
      DecisionMatrix/
      JobDetail/
```

Use `reports/job-evaluations/` as the output folder.

---

## Step 2 — Data Model (Power Query / TMDL)

### Source
Load `data/job_evaluations.json` via a relative file path using Power Query's `Json.Document(File.Contents(...))`.

### Tables

**`Jobs`** — one row per job (13 rows)
| Column | Type |
|---|---|
| JobID | Int (index, 1–13) |
| Title | Text |
| Company | Text |
| SkillMatch | Decimal |
| ExperienceLevelMatch | Decimal |
| CompanyFit | Decimal |
| GrowthPotential | Decimal |
| RedFlags | Decimal |
| OverallFit | Decimal |
| FitCategory | Text |
| Recommendation | Text |
| ReasonSummary | Text |

**`JobStrengths`** — expand `key_strengths` array
| Column | Type |
|---|---|
| JobID | Int (FK → Jobs) |
| Strength | Text |

**`JobGaps`** — expand `skill_gaps` array
| Column | Type |
|---|---|
| JobID | Int (FK → Jobs) |
| Gap | Text |

**`JobRedFlagsDetail`** — expand `red_flags_list` array
| Column | Type |
|---|---|
| JobID | Int (FK → Jobs) |
| RedFlag | Text |

### Measures (DAX)
```dax
Avg Overall Fit = AVERAGE(Jobs[OverallFit])
Top Company = CALCULATE(SELECTEDVALUE(Jobs[Company]), TOPN(1, Jobs, Jobs[OverallFit]))
High Fit Count = COUNTROWS(FILTER(Jobs, Jobs[FitCategory] = "high"))
Adj Fit Score = Jobs[OverallFit] * (1 - Jobs[RedFlags]/200)   -- penalizes red-flag risk
```

---

## Step 3 — Report Pages

### Page 1: Executive Summary
- **KPI cards**: High Fit Count, Avg Overall Fit, count of "Skip" recommendations
- **Donut chart**: FitCategory distribution (high / medium / low)
- **Ranked table**: All 13 jobs sorted by OverallFit — columns: Company, Title, FitCategory, OverallFit, SkillMatch
- **Slicer**: FitCategory filter

### Page 2: Scoring Comparison
- **Clustered bar chart**: Jobs on Y-axis, five score metrics (SkillMatch, ExperienceLevelMatch, CompanyFit, GrowthPotential, OverallFit) as series — sorted by OverallFit descending
- **100% stacked bar**: RedFlags as a risk overlay (color: red)
- Conditional formatting on bars: green ≥ 80, yellow 60–79, red < 60

### Page 3: Decision Matrix (Scatter)
- **Scatter chart**: X = SkillMatch, Y = OverallFit, bubble size = GrowthPotential, color = FitCategory
- Labels: Company name on each bubble
- Reference lines: X=75, Y=75 to create quadrant view
- Tooltip: Title, Recommendation

### Page 4: Job Detail (drill-through)
- Set up as a **drill-through page** from any job row
- **Text cards**: Title, Company, FitCategory, Recommendation, ReasonSummary
- **Gauge**: OverallFit (0–100)
- **Bullet list visual (or table)**: JobStrengths, JobGaps, JobRedFlagsDetail filtered to selected JobID
- Score breakdown bar for the 5 numeric metrics

---

## Step 4 — Styling
- Theme: dark background (`#1E2A3A`) with accent `#00B4D8` (teal) — consistent with a modern executive dashboard
- Use conditional formatting on FitCategory: high = green, medium = amber, low = red
- Font: Segoe UI, 12pt body, 18pt headers

---

## Files to Create/Modify

| File | Action |
|---|---|
| `tools/fetch_inbox.py` | Add `sanitize_text()` + apply to entry fields |
| `tools/refetch_jobs_browser.py` | Add `sanitize_text()` + apply to update fields |
| `data/job_evaluations.json` | One-time fix: remove 3 orphan `]` lines |
| `reports/job-evaluations/job-evaluations.pbip` | Create new |
| `reports/job-evaluations/job-evaluations.SemanticModel/definition/model.tmdl` | Create |
| `reports/job-evaluations/job-evaluations.SemanticModel/definition/tables/Jobs.tmdl` | Create |
| `reports/job-evaluations/job-evaluations.SemanticModel/definition/tables/JobStrengths.tmdl` | Create |
| `reports/job-evaluations/job-evaluations.SemanticModel/definition/tables/JobGaps.tmdl` | Create |
| `reports/job-evaluations/job-evaluations.SemanticModel/definition/tables/JobRedFlagsDetail.tmdl` | Create |
| `reports/job-evaluations/job-evaluations.Report/definition.pbir` | Create |
| `reports/job-evaluations/job-evaluations.Report/pages/` (4 pages) | Create |

---

## Verification
1. Run `python -c "import json; json.load(open('data/job_evaluations.json'))"` — should parse without error after the one-time fix
2. Run `tools/fetch_inbox.py` on a fresh email batch and confirm `inbox_queue.json` descriptions contain `(` `)` instead of `[` `]`
3. Open the `.pbip` file in Power BI Desktop — confirm it loads without errors
4. Check the Jobs table has 13 rows and the three expanded tables join correctly
5. Navigate all 4 report pages and verify visuals render
6. Drill-through from Page 1 table row to Page 4 Job Detail
7. Apply the FitCategory slicer on Page 1 and confirm cross-filtering propagates
