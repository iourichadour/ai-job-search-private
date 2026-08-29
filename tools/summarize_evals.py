import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

evals = json.load(open('data/job_evaluations.json', encoding='utf-8'))
past_week_evals = [e for e in evals if e.get('model') == 'Antigravity-Agent-Session']

print(f"Total past week evaluated: {len(past_week_evals)}")

high = sorted([e for e in past_week_evals if e['overall_fit'] >= 80], key=lambda x: x['overall_fit'], reverse=True)
med = sorted([e for e in past_week_evals if 65 <= e['overall_fit'] < 80], key=lambda x: x['overall_fit'], reverse=True)
low = [e for e in past_week_evals if 45 <= e['overall_fit'] < 65]
skip = [e for e in past_week_evals if e['overall_fit'] < 45]

print(f"High Fit (80%+): {len(high)}")
print(f"Medium Fit (65-79%): {len(med)}")
print(f"Low Fit (45-64%): {len(low)}")
print(f"Skip (<45%): {len(skip)}")

print("\n=== TOP HIGH FIT JOBS ===")
for i, e in enumerate(high, 1):
    print(f"{i}. [{e['overall_fit']}%] {e['title']} @ {e['company']}")
    print(f"   URL: {e.get('url')}")
    print(f"   Strengths: {', '.join(e['key_strengths'])}")
    print(f"   Reason: {e['reason_summary']}\n")

print("\n=== TOP MEDIUM FIT JOBS (Sample Top 20) ===")
for i, e in enumerate(med[:20], 1):
    print(f"{i}. [{e['overall_fit']}%] {e['title']} @ {e['company']}")
    print(f"   URL: {e.get('url')}")
    print(f"   Strengths: {', '.join(e['key_strengths'])}")
    print(f"   Reason: {e['reason_summary']}\n")
