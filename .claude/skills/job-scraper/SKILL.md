---
name: job-scraper
description: >
  Processes job URLs from inbox_queue.json (populated by /fetch-inbox from Gmail alerts), fetches full descriptions, and presents with quick fit assessment.
  Triggers on: job scrape, find jobs, check inbox jobs, evaluate inbox, /scrape
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Agent, AskUserQuestion
---

# Job Scraper (Inbox Queue Processor)

---

## How It Works

This skill reads job postings from `data/inbox_queue.json` (URLs fetched from LinkedIn/Indeed alerts via `/fetch-inbox`), retrieves full job descriptions, performs a quick fit assessment against your profile, deduplicates against previously seen jobs and the application tracker, and presents matches for evaluation or skipping.

**Key difference from original:** Instead of scraping job boards, this skill leverages Gmail's curated alerts, which are already filtered by LinkedIn/Indeed for relevance to your profile.

## Invocation

The user triggers this skill by saying things like:
- "Evaluate inbox jobs"
- "Check new jobs from inbox"
- "Process inbox queue"
- "/scrape" (when inbox_queue.json has jobs)

---

## Execution Steps

### Step 0: Load State

1. Read `data/inbox_queue.json` to get URLs and job metadata from `/fetch-inbox`
2. Read `job_scraper/seen_jobs.json` (create if missing - start with `{"seen": {}}`) for deduplication
3. Read `job_search_tracker.csv` to extract already-applied companies+roles
4. Read `data/profile.md` for fit assessment reference

### Step 1: Identify Pending Jobs

Filter jobs from `inbox_queue.json` with `status: "pending_evaluation"`:
- Skip any jobs already in `seen_jobs.json` (check by URL)
- Skip any company+role combos in `job_search_tracker.csv`
- Queue the rest for full description fetch

### Step 2: Fetch & Parse Job Descriptions

For each pending job:
- Use `WebFetch` to retrieve the full LinkedIn/Indeed job posting page
- Extract: **job title**, **company**, **location**, **posting date** (or "recent"), **key requirements**, **application deadline** (if listed), **full URL**
- Store raw description for later evaluation

If WebFetch fails (page moved, closed, etc.):
- Mark as `status: "fetch_failed"` in local processing
- Skip presenting but log it

### Step 3: Quick Fit Assessment

For each successfully fetched job, do a rapid fit check against the profile (NOT the full evaluation from `04-job-evaluation.md` - just a quick signal):

**Scoring logic:**
- **High match**: Role title is VP/SVP/Head/Principal + requirements heavily overlap with core technical competencies (Fabric, Snowflake, Power BI, data architecture, team leadership)
- **Medium match**: Role is adjacent (e.g., analytics engineering, data governance, modern BI) + some skill gaps that are learnable
- **Low match**: Role requires significant domain shifts (legacy-only stacks, unrelated functions like "network engineer")

### Step 4: Deduplicate & Store

1. Update `seen_jobs.json` with all processed jobs:
```json
{
  "seen": {
    "<url_hash_or_id>": {
      "title": "...",
      "company": "...",
      "url": "...",
      "first_seen": "YYYY-MM-DD",
      "source": "linkedin/indeed",
      "fit": "high/medium/low",
      "status": "new/skipped/evaluated/fetch_failed"
    }
  }
}
```
2. Only present jobs with `status: "new"` (not yet seen or evaluated)

### Step 5: Present Results

Present new jobs in a table sorted by fit (high first):

```
## Inbox Job Queue - YYYY-MM-DD

Processing jobs from data/inbox_queue.json.
Found X new positions (Y high, Z medium, W low match).

| # | Fit | Title | Company | Location | URL |
|---|-----|-------|---------|----------|-----|
| 1 | High | ... | ... | ... | [Link](...) |

### High-Match Highlights
For each high-match job, add 2-3 bullet points:
- Why it matches your profile
- Key requirements to verify
- Any red flags (e.g., legacy stack, relocation required)

### Medium-Match Summary
- List titles and quick rationale
```

After presenting, ask:
> "Want me to run a detailed evaluation for any of these? Just give me the number(s) (or press Enter to skip)."

If the user picks numbers, invoke the **job-application-assistant** skill workflow (fit evaluation first, then CV + cover letter if approved).

If user says "skip all", mark all as `status: "skipped"` in `seen_jobs.json`.

### Step 6: Update Inbox Queue

Mark evaluated jobs in `data/inbox_queue.json` with status updates:
- `"status": "evaluated"` - if user chose to evaluate
- `"status": "skipped"` - if user chose to skip

---

## Important Rules

1. **Source of truth is inbox_queue.json.** All jobs come from Gmail alerts already filtered by LinkedIn/Indeed.
2. **Respect deduplication.** Always check `seen_jobs.json` AND `job_search_tracker.csv` before presenting.
3. **Quick fit only.** Step 3 is a 20-second scan against profile, NOT the full 5-dimension evaluation from `04-job-evaluation.md`.
4. **Handle fetch failures gracefully.** If a URL is dead/moved/closed, mark it and skip (don't error out).
5. **Preserve job data.** Store the fetched description in seen_jobs.json for reference during full evaluation later.
6. **No Web Search.** Unlike the original scraper, this doesn't search job boards — it processes URLs already in the queue.
