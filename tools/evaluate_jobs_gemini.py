#!/usr/bin/env python3
"""
Job Evaluation using Gemini AI.
Evaluates each job posting against the candidate profile.

Setup:
  1. pip install google-genai
  2. Set environment variable: export GEMINI_API_KEY="your-key-here"
     (On Windows: set GEMINI_API_KEY=your-key-here)
  3. Run: python tools/evaluate_jobs_gemini.py

Notes:
  - Uses gemini-2.5-flash by default (fast + cost-effective)
  - Override model via: set GEMINI_MODEL=gemini-2.5-pro
"""

import os
import json
import sys
from datetime import datetime

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[!] google-genai SDK not installed. Run:")
    print("    pip install google-genai")
    sys.exit(1)

# Initialize Gemini client
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("[!] GEMINI_API_KEY environment variable not set")
    print("\nSet it with:")
    print("  Windows: set GEMINI_API_KEY=your-api-key")
    print("  Mac/Linux: export GEMINI_API_KEY=your-api-key")
    print("\nGet your key at: https://aistudio.google.com/apikey")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Model selection — override via GEMINI_MODEL env var
MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')


def load_profile():
    """Load candidate profile from data/profile.md"""
    profile_path = 'data/profile.md'
    if not os.path.exists(profile_path):
        print(f"[!] {profile_path} not found")
        sys.exit(1)

    with open(profile_path, 'r', encoding='utf-8') as f:
        return f.read()


def evaluate_job(job_data, profile):
    """
    Evaluate a job posting using Gemini.
    Returns structured evaluation with fit score and analysis.
    """
    job_title = job_data.get('title', 'N/A')
    company = job_data.get('company', 'N/A')
    description = job_data.get('description', 'N/A')[:3000]  # Limit to 3000 chars

    # Create evaluation prompt
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

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,           # Low temperature for consistent structured output
                max_output_tokens=1200,
                response_mime_type="application/json",  # Gemini native JSON mode
            ),
        )

        response_text = response.text.strip()

        # Parse JSON response
        try:
            evaluation = json.loads(response_text)
            evaluation['evaluated_at'] = datetime.now().isoformat()
            evaluation['model'] = MODEL
            return evaluation
        except json.JSONDecodeError:
            print(f"    [!] Failed to parse response as JSON")
            print(f"    Response: {response_text[:200]}")
            return None

    except Exception as e:
        print(f"    [ERROR] API call failed: {e}")
        return None


def main():
    inbox_file = 'data/inbox_queue.json'
    evaluations_file = 'data/job_evaluations.json'

    print(f"[+] Using model: {MODEL}")

    # Load profile
    print("[+] Loading candidate profile...")
    profile = load_profile()

    # Load inbox queue
    print("[+] Loading job queue...")
    if not os.path.exists(inbox_file):
        print(f"[!] {inbox_file} not found")
        sys.exit(1)

    with open(inbox_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    # Filter jobs that need evaluation (no evaluation yet)
    jobs_to_evaluate = [
        job for job in queue
        if not job.get('evaluation')
    ]

    if not jobs_to_evaluate:
        print("[✓] All jobs already evaluated")
        return

    print(f"\n[+] Found {len(jobs_to_evaluate)} jobs to evaluate\n")

    # Load existing evaluations if they exist
    evaluations = []
    if os.path.exists(evaluations_file):
        try:
            with open(evaluations_file, 'r', encoding='utf-8') as f:
                evaluations = json.load(f)
        except Exception:
            evaluations = []

    # Evaluate each job
    evaluated = 0
    for i, job in enumerate(jobs_to_evaluate, 1):
        job_title = job.get('title', 'Unknown')[:50]
        company = job.get('company', 'Unknown')[:30]
        print(f"[{i}/{len(jobs_to_evaluate)}] {company} - {job_title}")

        # Skip if description is missing
        if job.get('description') == 'N/A' or not job.get('description'):
            print(f"    [⊘] Skipping (no description)")
            continue

        # Evaluate with Gemini
        print(f"    [→] Evaluating with Gemini ({MODEL})...")
        evaluation = evaluate_job(job, profile)

        if evaluation:
            # Add URL reference to evaluation
            evaluation['url'] = job.get('url')

            # Add to job record
            job['evaluation'] = evaluation

            # Store in evaluations list
            evaluations.append(evaluation)
            evaluated += 1

            fit = evaluation.get('overall_fit', 0)
            category = evaluation.get('fit_category', 'unknown')
            print(f"    [✓] Fit: {fit}% ({category})")

            # Show recommendation
            rec = evaluation.get('recommendation', '')
            if rec:
                print(f"    📋 {rec[:80]}")

    # Save updated queue with evaluations
    print(f"\n[+] Saving results...")
    with open(inbox_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    # Save evaluation summary
    with open(evaluations_file, 'w', encoding='utf-8') as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)

    print(f"[✓] Evaluation complete!")
    print(f"[+] Evaluated: {evaluated} jobs")
    print(f"[+] Results saved to:")
    print(f"    - {inbox_file}")
    print(f"    - {evaluations_file}")

    # Summary statistics
    if evaluations:
        high_fit   = [e for e in evaluations if e.get('fit_category') == 'high']
        medium_fit = [e for e in evaluations if e.get('fit_category') == 'medium']
        low_fit    = [e for e in evaluations if e.get('fit_category') == 'low']
        skip       = [e for e in evaluations if e.get('fit_category') == 'skip']

        print(f"\n[📊] Summary:")
        print(f"  High Fit (80+):     {len(high_fit)} jobs")
        print(f"  Medium Fit (60-79): {len(medium_fit)} jobs")
        print(f"  Low Fit (40-59):    {len(low_fit)} jobs")
        print(f"  Skip (<40):         {len(skip)} jobs")

        if high_fit:
            print(f"\n[🎯] Top Recommendations:")
            for eval in sorted(high_fit, key=lambda x: x.get('overall_fit', 0), reverse=True)[:5]:
                print(f"  {eval['overall_fit']}% - {eval['company']} - {eval['title'][:40]}")


if __name__ == "__main__":
    main()
