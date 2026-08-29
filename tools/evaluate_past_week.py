#!/usr/bin/env python3
"""
Evaluate past week jobs from data/inbox_queue.json against data/profile.md.
Updates data/inbox_queue.json and data/job_evaluations.json.
"""

import os
import json
import sys
import re
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_profile():
    with open('data/profile.md', 'r', encoding='utf-8') as f:
        return f.read()

def parse_job_date(job):
    for k in ('fetched_at', 'refetched_at', 'created_at'):
        ts = job.get(k)
        if ts:
            try:
                return datetime.fromisoformat(ts.replace('Z', '+00:00')).replace(tzinfo=None)
            except Exception:
                pass
    return None

def extract_company_and_location(job):
    company = job.get('company', '')
    desc = job.get('description', '')
    title = job.get('title', '')
    
    if company and company != 'N/A':
        comp = company
    else:
        comp = 'Unknown Company'
        lines = [l.strip() for l in desc.split('\n') if l.strip()]
        for idx, line in enumerate(lines[:5]):
            if line == title and idx + 1 < len(lines):
                potential_comp = lines[idx+1]
                if not potential_comp.startswith(('Apply', 'Join', 'Email', 'Password', 'http', 'Save', 'Report')):
                    comp = potential_comp
                    break
        if comp == 'Unknown Company' and len(lines) >= 2:
            if not lines[1].startswith(('Apply', 'Join', 'Email', 'Password', 'http', 'Save', 'Report')):
                comp = lines[1]
                
    return comp

def evaluate_job(job, profile_text):
    title = job.get('title', 'N/A')
    company = extract_company_and_location(job)
    desc = job.get('description', '')
    text = f"{title} {company} {desc}".lower()
    title_lower = title.lower()

    closed_keywords = [
        'no longer accepting applications',
        'this job is no longer available',
        'job posting has expired',
        'no longer active',
        'position closed'
    ]
    if any(ck in text for ck in closed_keywords):
        return {
            'title': title,
            'company': company,
            'skill_match': 0,
            'experience_level_match': 0,
            'company_fit': 0,
            'growth_potential': 0,
            'red_flags': 100,
            'overall_fit': 0,
            'fit_category': 'closed',
            'key_strengths': [],
            'skill_gaps': ['Job posting closed'],
            'red_flags_list': ['No longer accepting applications'],
            'recommendation': 'Closed - No longer accepting applications.',
            'reason_summary': f"{title} at {company}: Job posting is closed (no longer accepting applications).",
            'evaluated_at': datetime.now().isoformat(),
            'model': 'Antigravity-Agent-Session'
        }

    # 1. Technical Skill Match (30%)
    high_keywords = [
        'fabric', 'microsoft fabric', 'snowflake', 'power bi', 'powerbi', 'dax', 'tabular editor',
        'data mesh', 'onelake', 'lakehouse', 'azure data factory', 'pyspark', 'python', 'sql',
        'semantic model', 'data architecture', 'data engineering', 'analytics engineering'
    ]
    med_keywords = [
        'cloud', 'azure', 'aws', 'ai', 'artificial intelligence', 'genai', 'generative ai',
        'machine learning', 'data platform', 'business intelligence', 'bi', 'analytics', 'etl',
        'pipeline', 'data warehouse', 'databricks', 'llm', 'copilot', 'agentic'
    ]
    
    high_hits = list(set([k for k in high_keywords if k in text]))
    med_hits = list(set([k for k in med_keywords if k in text]))
    
    if len(high_hits) >= 3:
        skill_match = 95
    elif len(high_hits) >= 1:
        skill_match = 85
    elif len(med_hits) >= 4:
        skill_match = 75
    elif len(med_hits) >= 2:
        skill_match = 65
    elif len(med_hits) >= 1:
        skill_match = 50
    else:
        skill_match = 30

    # 2. Experience Level Match (25%)
    exec_titles = ['vice president', 'vp', 'svp', 'avp', 'chief', 'cdo', 'head of', 'executive director', 'senior director', 'director', 'principal', 'practice lead']
    mgr_titles = ['manager', 'lead', 'architect', 'senior manager', 'sr. manager']
    
    if any(t in title_lower for t in exec_titles):
        exp_match = 90
        if any(d in title_lower for d in ['data', 'analytics', 'ai', 'technology', 'engineering', 'platform', 'solutions', 'bi', 'business intelligence']):
            exp_match = 95
    elif any(t in title_lower for t in mgr_titles):
        exp_match = 75
    else:
        exp_match = 40

    # 3. Company / Industry Fit (20%)
    fin_services = ['finance', 'financial', 'asset management', 'investment', 'capital', 'bank', 'banking', 'wealth', 'fintech', 'insurance', 'lazard', 'bayview', 'guardian', 'axa', 'jpmorgan', 'goldman', 'blackrock', 'citigroup', 'morgan stanley']
    tech_consult = ['microsoft', 'databricks', 'snowflake', 'trace3', 'accenture', 'deloitte', 'mckinsey', 'palantir', 'salesforce', 'software', 'technology', 'saas', 'cloud', 'ai platform']
    
    if any(k in text for k in fin_services):
        company_fit = 90
    elif any(k in text for k in tech_consult):
        company_fit = 85
    elif any(k in text for k in ['healthcare', 'pharma', 'energy', 'retail', 'biotech', 'novartis', 'kraken']):
        company_fit = 70
    else:
        company_fit = 50

    # 4. Growth Potential (15%)
    growth_keywords = ['transformation', 'strategy', 'roadmap', 'modernization', 'build team', 'scale', 'lead', 'vision', 'innovate', 'innovation', 'agentic', 'copilot']
    growth_hits = list(set([k for k in growth_keywords if k in text]))
    if len(growth_hits) >= 3:
        growth_potential = 90
    elif len(growth_hits) >= 1:
        growth_potential = 75
    else:
        growth_potential = 55

    # 5. Red Flags (-10% penalty / lower is better)
    unrelated = [
        'racquet', 'parent engagement', 'logistics', 'burger king', 'salt', 'beef', 'tax director',
        'joint', 'dental', 'nursing', 'store manager', 'annual fund', 'flight', 'aviation', 'food'
    ]
    red_flags_list = []
    if any(u in title_lower for u in unrelated):
        red_flags_list.append('Unrelated field / role outside Data & AI target scope')
    if exp_match < 50:
        red_flags_list.append('Seniority level below target executive profile')

    if 'Unrelated field / role outside Data & AI target scope' in red_flags_list:
        red_flags = 85
    elif red_flags_list:
        red_flags = 45
    else:
        red_flags = 10

    # Weighted Overall Fit Score
    # Skills 30%, Experience 25%, Company 20%, Growth 15%, Red Flags -10% (i.e. +10% for (100 - red_flags))
    overall_fit = round(skill_match * 0.30 + exp_match * 0.25 + company_fit * 0.20 + growth_potential * 0.15 + (100 - red_flags) * 0.10)

    if overall_fit >= 80:
        fit_cat = 'high'
    elif overall_fit >= 65:
        fit_cat = 'medium'
    elif overall_fit >= 45:
        fit_cat = 'low'
    else:
        fit_cat = 'skip'

    strengths = []
    if high_hits:
        strengths.append(f"Strong tech stack match: {', '.join(high_hits[:4])}")
    elif med_hits:
        strengths.append(f"Core data/AI skill alignment: {', '.join(med_hits[:4])}")
        
    if exp_match >= 85:
        strengths.append(f"Leadership title alignment ({title})")
    if company_fit >= 80:
        strengths.append(f"Target industry fit ({company})")
    if growth_potential >= 80:
        strengths.append("High strategic impact & transformation opportunity")

    gaps = []
    if not high_hits:
        gaps.append("No explicit mention of Microsoft Fabric / Snowflake / Power BI")
    if company_fit < 75:
        gaps.append("Outside core Financial Services / FinTech / Enterprise Tech target")

    if fit_cat == 'high':
        rec = f"Strong Match ({overall_fit}%) - {title} at {company}. Recommended for immediate application."
    elif fit_cat == 'medium':
        rec = f"Moderate Match ({overall_fit}%) - {title} at {company}. Recommended for selective review."
    else:
        rec = f"Low/Skip Match ({overall_fit}%) - Outside target scope."

    hit_summary = f"Tech Hits: {', '.join(high_hits + med_hits)[:100]}"

    return {
        'title': title,
        'company': company,
        'skill_match': skill_match,
        'experience_level_match': exp_match,
        'company_fit': company_fit,
        'growth_potential': growth_potential,
        'red_flags': red_flags,
        'overall_fit': overall_fit,
        'fit_category': fit_cat,
        'key_strengths': strengths,
        'skill_gaps': gaps,
        'red_flags_list': red_flags_list,
        'recommendation': rec,
        'reason_summary': f"{title} at {company}: Overall Fit {overall_fit}% ({fit_cat}). Skills {skill_match}%, Exp {exp_match}%, Industry {company_fit}%. {hit_summary}",
        'evaluated_at': datetime.now().isoformat(),
        'model': 'Antigravity-Agent-Session'
    }

def main():
    profile_text = load_profile()
    inbox_file = 'data/inbox_queue.json'
    evaluations_file = 'data/job_evaluations.json'

    with open(inbox_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    now = datetime(2026, 8, 28)
    cutoff = now - timedelta(days=7)

    evaluations = []
    updated_queue = []

    for job in queue:
        dt = parse_job_date(job)
        if dt and dt >= cutoff:
            desc = job.get('description', '')
            title = job.get('title', '')
            if desc and desc != 'N/A' and not title.startswith(('1,000+', '7,000+', '9,000+', '10,000+', '11,000+')):
                ev = evaluate_job(job, profile_text)
                ev['url'] = job.get('url')
                job['evaluation'] = ev
                job['status'] = 'closed' if ev.get('fit_category') == 'closed' else 'evaluated'
                evaluations.append(ev)
        updated_queue.append(job)

    # Save to inbox_queue.json
    with open(inbox_file, 'w', encoding='utf-8') as f:
        json.dump(updated_queue, f, indent=2, ensure_ascii=False)

    # Save/Merge with data/job_evaluations.json
    existing_evals = []
    if os.path.exists(evaluations_file):
        try:
            with open(evaluations_file, 'r', encoding='utf-8') as f:
                existing_evals = json.load(f)
        except Exception:
            existing_evals = []

    eval_by_url = {e['url']: e for e in evaluations if e.get('url')}
    for ev in evaluations:
        url = ev.get('url')
        idx = next((i for i, item in enumerate(existing_evals) if item.get('url') == url or (item.get('title') == ev.get('title') and item.get('company') == ev.get('company'))), None)
        if idx is not None:
            existing_evals[idx] = ev
        else:
            existing_evals.append(ev)

    with open(evaluations_file, 'w', encoding='utf-8') as f:
        json.dump(existing_evals, f, indent=2, ensure_ascii=False)

    print(f"[✓] Successfully evaluated {len(evaluations)} jobs from the past 7 days.")

if __name__ == '__main__':
    main()
