#!/usr/bin/env python3
"""
Job Evaluation & Filtering Tool.
Evaluates job postings against candidate profile using Gemini AI API or Agent-driven mode.

Usage:
  1. API Evaluation Mode (requires GEMINI_API_KEY):
     python tools/evaluate_jobs_gemini.py --days 14

  2. Agent Filtering / Export Mode (no API key required):
     python tools/evaluate_jobs_gemini.py --days 14 --filter-only

  3. Save Agent Evaluations back to Queue:
     python tools/evaluate_jobs_gemini.py --save-evaluations data/agent_evals.json

  4. Track Application Submission:
     python tools/evaluate_jobs_gemini.py --track-applied "https://job-url..." --company "Acme" --role "Director"
"""

import os
import json
import sys
import time
import re
import csv
import argparse
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Globals for lazy SDK loading
genai_client = None
genai_types = None
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')


def get_gemini_client():
    """Lazy initializer for Gemini API client."""
    global genai_client, genai_types
    if genai_client is not None:
        return genai_client, genai_types

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[!] google-genai SDK not installed. Run:")
        print("    pip install google-genai")
        sys.exit(1)

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("[!] GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  Windows: set GEMINI_API_KEY=your-api-key")
        print("  Mac/Linux: export GEMINI_API_KEY=your-api-key")
        print("\nGet your key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    genai_client = genai.Client(api_key=api_key)
    genai_types = types
    return genai_client, genai_types


def load_profile():
    """Load candidate profile from data/profile.md"""
    profile_path = 'data/profile.md'
    if not os.path.exists(profile_path):
        print(f"[!] {profile_path} not found")
        sys.exit(1)

    with open(profile_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_job_date(job):
    """
    Extract datetime object from job record fields (fetched_at, refetched_at, created_at)
    or parse relative date strings from job description text (e.g. '2 weeks ago', '3 days ago').
    """
    for date_key in ('fetched_at', 'refetched_at', 'created_at'):
        ts_str = job.get(date_key)
        if ts_str:
            try:
                # Clean ISO format if needed
                ts_str_clean = ts_str.replace('Z', '+00:00')
                return datetime.fromisoformat(ts_str_clean)
            except (ValueError, AttributeError):
                pass

    # Fallback: check job description for relative date strings
    desc = job.get('description', '')
    if desc:
        match = re.search(r'(\d+)\s+(hour|day|week|month)s?\s+ago', desc, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            unit = match.group(2).lower()
            now = datetime.now()
            if 'hour' in unit:
                return now - timedelta(hours=num)
            elif 'day' in unit:
                return now - timedelta(days=num)
            elif 'week' in unit:
                return now - timedelta(weeks=num)
            elif 'month' in unit:
                return now - timedelta(days=num * 30)

    return None


def filter_jobs_by_date(queue, days=None, start_date=None, end_date=None, unevaluated_only=True):
    """
    Filter jobs in queue based on date range and evaluation status.
    """
    start_dt = None
    end_dt = None

    if days is not None:
        start_dt = datetime.now() - timedelta(days=days)
        end_dt = datetime.now()
    else:
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print(f"[!] Invalid start-date format: {start_date}. Use YYYY-MM-DD.")
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            except ValueError:
                print(f"[!] Invalid end-date format: {end_date}. Use YYYY-MM-DD.")

    filtered = []
    for job in queue:
        # Check evaluation status
        if unevaluated_only and (job.get('evaluation') or job.get('status') == 'evaluated'):
            continue

        # Check date range
        if start_dt or end_dt:
            job_dt = parse_job_date(job)
            if job_dt:
                if job_dt.tzinfo is not None:
                    job_dt = job_dt.replace(tzinfo=None)

                if start_dt and job_dt < start_dt:
                    continue
                if end_dt and job_dt > end_dt:
                    continue

        filtered.append(job)

    return filtered


def evaluate_job_api(job_data, profile):
    """
    Evaluate a job posting using Gemini API.
    Returns structured evaluation with fit score and analysis.
    """
    client, types = get_gemini_client()

    job_title = job_data.get('title', 'N/A')
    company = job_data.get('company', 'N/A')
    description = job_data.get('description', 'N/A')[:3000]

    prompt = f"""You are an expert career advisor evaluating job opportunities for a senior data & analytics professional.

CANDIDATE PROFILE:
{profile}

---

JOB TO EVALUATE:
Title: {job_title}
Company: {company}

Description:
{description}

---

Evaluate this job posting based on these criteria:
1. **Technical Skill Match** (0-100%): How well do the required skills align with the candidate's expertise in Fabric, Snowflake, Power BI, data architecture?
2. **Experience Level Match** (0-100%): Does the seniority level match (VP/SVP/Principal/C-suite)?
3. **Company/Industry Fit** (0-100%): Is this in a target industry? (Finance, Tech, Consulting, SaaS)
4. **Growth Potential** (0-100%): Does this role offer opportunities for leadership, innovation, or strategic impact?
5. **Red Flags** (0-100%, lower is better): Any deal-breakers (legacy stack, siloed IT, no modernization path)?

Provide response in this exact JSON format (no markdown, just raw JSON):
{{
  "title": "{job_title}",
  "company": "{company}",
  "skill_match": 85,
  "experience_level_match": 90,
  "company_fit": 75,
  "growth_potential": 80,
  "red_flags": 10,
  "overall_fit": 82,
  "fit_category": "high",
  "key_strengths": ["strength1", "strength2", "strength3"],
  "skill_gaps": ["gap1", "gap2"],
  "red_flags_list": ["flag1"],
  "recommendation": "Strong match - VP+ title in modern data stack. Consider applying.",
  "reason_summary": "Company is in target fintech sector with modern cloud infrastructure. Role aligns with leadership experience and Fabric/Snowflake expertise."
}}

Notes:
- overall_fit should be average of the 5 dimensions (weighted: skills 30%, experience 25%, company 20%, growth 15%, red_flags -10%)
- fit_category: "high" (80+), "medium" (60-79), "low" (40-59), "skip" (<40)
- Be thorough but concise in reasoning
- Flag any deal-breaker concerns clearly"""

    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2500,
                    response_mime_type="application/json",
                ),
            )

            response_text = response.text.strip()
            response_text = re.sub(r'^```(?:json)?\s*', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'\s*```$', '', response_text, flags=re.MULTILINE).strip()

            try:
                evaluation = json.loads(response_text)
                evaluation['evaluated_at'] = datetime.now().isoformat()
                evaluation['model'] = GEMINI_MODEL
                return evaluation
            except json.JSONDecodeError:
                if attempt < 3:
                    time.sleep(2)
                    continue
                print(f"    [!] Failed to parse response as JSON")
                print(f"    Response: {response_text[:200]}")
                return None

        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                match = re.search(r'retry in ([\d\.]+)s', err_msg, re.IGNORECASE)
                wait_sec = float(match.group(1)) + 2.0 if match else 60.0
                if attempt < 4:
                    print(f"    [!] Rate limit reached, pausing {wait_sec:.1f}s before retry (attempt {attempt}/4)...")
                    time.sleep(wait_sec)
                    continue
            if attempt < 3:
                time.sleep(2 * attempt)
                continue
            print(f"    [ERROR] API call failed: {e}")
            return None


def save_evaluations_to_files(evaluations_list, inbox_file='data/inbox_queue.json', evaluations_file='data/job_evaluations.json'):
    """
    Merge evaluation results into data/inbox_queue.json and data/job_evaluations.json.
    Updates job status to 'evaluated' and attaches the evaluation dict to each job item.
    """
    if not os.path.exists(inbox_file):
        print(f"[!] {inbox_file} not found")
        return False

    with open(inbox_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    # Load existing evaluations
    existing_evals = []
    if os.path.exists(evaluations_file):
        try:
            with open(evaluations_file, 'r', encoding='utf-8') as f:
                existing_evals = json.load(f)
        except Exception:
            existing_evals = []

    eval_by_url = {e['url']: e for e in evaluations_list if e.get('url')}
    eval_by_title_comp = {f"{e.get('title')}__{e.get('company')}": e for e in evaluations_list}

    updated_count = 0
    for job in queue:
        url = job.get('url')
        key = f"{job.get('title')}__{job.get('company')}"
        matched_eval = eval_by_url.get(url) or eval_by_title_comp.get(key)

        if matched_eval:
            matched_eval['url'] = url
            job['evaluation'] = matched_eval
            job['status'] = 'evaluated'
            updated_count += 1

            # Update or append in existing_evals list
            idx = next((i for i, item in enumerate(existing_evals) if item.get('url') == url or (item.get('title') == matched_eval.get('title') and item.get('company') == matched_eval.get('company'))), None)
            if idx is not None:
                existing_evals[idx] = matched_eval
            else:
                existing_evals.append(matched_eval)

    # Save queue
    with open(inbox_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    # Save evaluation summary
    with open(evaluations_file, 'w', encoding='utf-8') as f:
        json.dump(existing_evals, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved {updated_count} evaluations to {inbox_file} & {evaluations_file}")
    return True


def track_submission(url_or_title, company=None, role=None, status='applied', notes='', tracker_csv='job_search_tracker.csv', inbox_file='data/inbox_queue.json'):
    """
    Mark job as applied/submitted in data/inbox_queue.json and log row to job_search_tracker.csv.
    """
    # 1. Update queue file
    updated = False
    target_job = None
    if os.path.exists(inbox_file):
        with open(inbox_file, 'r', encoding='utf-8') as f:
            queue = json.load(f)

        for job in queue:
            if (url_or_title and (job.get('url') == url_or_title or url_or_title in job.get('title', ''))) or \
               (company and role and company.lower() in job.get('company', '').lower() and role.lower() in job.get('title', '').lower()):
                job['status'] = status
                job['applied_at'] = datetime.now().isoformat()
                target_job = job
                updated = True
                break

        if updated:
            with open(inbox_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            print(f"[✓] Updated status to '{status}' in {inbox_file}")

    # 2. Append to job_search_tracker.csv
    file_exists = os.path.exists(tracker_csv)
    fieldnames = ['date', 'company', 'sector', 'role', 'role_type', 'channel', 'status', 'contact_person', 'fit_rating', 'notes', 'cv_file', 'cover_letter_file', 'source']

    comp = company or (target_job.get('company') if target_job else 'Unknown')
    r_title = role or (target_job.get('title') if target_job else 'Unknown')
    fit_rating = ''
    source_channel = target_job.get('source', 'linkedin') if target_job else 'direct'
    if target_job and target_job.get('evaluation'):
        fit_rating = f"{target_job['evaluation'].get('overall_fit', '')}%"

    row = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'company': comp,
        'sector': 'Tech / Analytics',
        'role': r_title,
        'role_type': 'Full-time',
        'channel': source_channel,
        'status': status,
        'contact_person': '',
        'fit_rating': fit_rating,
        'notes': notes,
        'cv_file': '',
        'cover_letter_file': '',
        'source': source_channel
    }

    with open(tracker_csv, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists or os.path.getsize(tracker_csv) == 0:
            writer.writeheader()
        writer.writerow(row)

    print(f"[✓] Logged submission to {tracker_csv}: {comp} - {r_title} ({status})")


def main():
    parser = argparse.ArgumentParser(description="Job Evaluation & Filtering Tool (Gemini / Agent Mode)")
    parser.add_argument('--days', '-d', type=int, default=None, help="Filter jobs fetched in past N days (e.g. 14 for past 2 weeks)")
    parser.add_argument('--start-date', type=str, default=None, help="Start date filter (YYYY-MM-DD)")
    parser.add_argument('--end-date', type=str, default=None, help="End date filter (YYYY-MM-DD)")
    parser.add_argument('--all-dates', action='store_true', help="Include all jobs regardless of date")
    parser.add_argument('--filter-only', action='store_true', help="Output filtered jobs for Agent review without using API key")
    parser.add_argument('--save-evaluations', type=str, default=None, help="Path to JSON file containing evaluation objects to save/merge")
    parser.add_argument('--track-applied', type=str, default=None, help="Job URL or Title keyword to mark as applied in tracker")
    parser.add_argument('--company', type=str, default=None, help="Company name for submission tracking")
    parser.add_argument('--role', type=str, default=None, help="Role title for submission tracking")
    parser.add_argument('--status', type=str, default='applied', help="Status for tracking (default: applied)")
    parser.add_argument('--all-jobs', action='store_true', help="Include already-evaluated jobs in filtering")
    args = parser.parse_args()

    # Handle submission tracking mode
    if args.track_applied or (args.company and args.role):
        track_submission(
            url_or_title=args.track_applied,
            company=args.company,
            role=args.role,
            status=args.status
        )
        return

    # Handle save evaluations mode
    if args.save_evaluations:
        if os.path.exists(args.save_evaluations):
            with open(args.save_evaluations, 'r', encoding='utf-8') as f:
                evals = json.load(f)
            save_evaluations_to_files(evals)
        else:
            try:
                evals = json.loads(args.save_evaluations)
                save_evaluations_to_files(evals)
            except Exception as e:
                print(f"[!] Failed to parse evaluations input: {e}")
        return

    inbox_file = 'data/inbox_queue.json'
    evaluations_file = 'data/job_evaluations.json'

    if not os.path.exists(inbox_file):
        print(f"[!] {inbox_file} not found")
        sys.exit(1)

    with open(inbox_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    # Determine default date filter: if no date specified and --all-dates not passed, default --days 14 when --filter-only used
    days_val = args.days
    if not args.all_dates and days_val is None and not args.start_date and not args.end_date and args.filter_only:
        days_val = 14  # Default past 2 weeks

    unevaluated_only = not args.all_jobs
    candidate_jobs = filter_jobs_by_date(
        queue,
        days=days_val,
        start_date=args.start_date,
        end_date=args.end_date,
        unevaluated_only=unevaluated_only
    )

    date_desc = f"past {days_val} days" if days_val else (f"{args.start_date} to {args.end_date}" if args.start_date else "all dates")

    # Handle --filter-only mode for Agent session evaluation
    if args.filter_only:
        print(f"[+] Exporting jobs for Agent Evaluation ({date_desc}, unevaluated_only={unevaluated_only}):")
        print(f"[+] Found {len(candidate_jobs)} jobs\n")
        export_payload = []
        for j in candidate_jobs:
            export_payload.append({
                "url": j.get('url'),
                "title": j.get('title'),
                "company": j.get('company'),
                "description": j.get('description', '')[:2500],
                "fetched_at": j.get('fetched_at') or j.get('refetched_at')
            })
        print(json.dumps(export_payload, indent=2, ensure_ascii=False))
        return

    # Standard API Evaluation Mode
    print(f"[+] Using model: {GEMINI_MODEL}")
    print("[+] Loading candidate profile...")
    profile = load_profile()

    print(f"[+] Found {len(candidate_jobs)} jobs to evaluate ({date_desc})\n")
    if not candidate_jobs:
        print("[✓] No pending jobs to evaluate in specified date range.")
        return

    evaluations = []
    evaluated_count = 0

    for i, job in enumerate(candidate_jobs, 1):
        job_title = job.get('title', 'Unknown')[:50]
        company = job.get('company', 'Unknown')[:30]
        print(f"[{i}/{len(candidate_jobs)}] {company} - {job_title}")

        if job.get('description') == 'N/A' or not job.get('description'):
            print(f"    [⊘] Skipping (no description)")
            continue

        print(f"    [→] Evaluating with Gemini ({GEMINI_MODEL})...")
        evaluation = evaluate_job_api(job, profile)

        if evaluation:
            evaluation['url'] = job.get('url')
            job['evaluation'] = evaluation
            job['status'] = 'evaluated'
            evaluations.append(evaluation)
            evaluated_count += 1

            fit = evaluation.get('overall_fit', 0)
            category = evaluation.get('fit_category', 'unknown')
            print(f"    [✓] Fit: {fit}% ({category})")
            rec = evaluation.get('recommendation', '')
            if rec:
                print(f"    📋 {rec[:80]}")

        time.sleep(1.0)

    # Save results
    save_evaluations_to_files(evaluations, inbox_file=inbox_file, evaluations_file=evaluations_file)


if __name__ == "__main__":
    main()
