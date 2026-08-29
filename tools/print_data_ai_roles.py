import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

evals = json.load(open('data/job_evaluations.json', encoding='utf-8'))
past_week = [e for e in evals if e.get('model') == 'Antigravity-Agent-Session']

data_ai_roles = []
for e in past_week:
    t = e['title'].lower()
    if any(k in t for k in ['data', 'analytics', 'ai', 'intelligence', 'business intelligence', 'bi', 'machine learning', 'platform']):
        if not any(r in t for r in ['racquet', 'parent', 'logistics', 'burger king', 'salt', 'beef']):
            data_ai_roles.append(e)

data_ai_roles.sort(key=lambda x: x['overall_fit'], reverse=True)

print(f"Total Data/Analytics/AI roles found in past 7 days: {len(data_ai_roles)}")
print("\nTop Data & AI Positions:\n")
for i, e in enumerate(data_ai_roles[:35], 1):
    print(f"{i}. [{e['overall_fit']}% | {e['fit_category'].upper()}] {e['title']}")
    print(f"   Company: {e['company']}")
    print(f"   URL: {e.get('url')}")
    print(f"   Strengths: {', '.join(e['key_strengths'])}")
    print(f"   Gaps: {', '.join(e['skill_gaps'])}")
    print(f"   Summary: {e['reason_summary']}\n")
