"""Generate the executive job-search dashboard as a single static HTML file.

Reads private/job_evaluations.json and private/job_search_tracker.csv, computes
every KPI/chart value from real data (no placeholders), and writes _brief/mockup.html.
"""
import json
import csv
import os
import re
import sys

import config

TECH_KEYWORDS = [
    "Microsoft Fabric", "OneLake", "Snowflake", "Power BI", "Azure Data Factory",
    "Python", "DAX", "Data Mesh", "SQL",
]

TERMINAL_STATUSES = {"rejected", "withdrawn", "closed", "declined"}


def load_evaluations(path=None):
    path = path or config.JOB_EVALUATIONS_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_tracker(path=None):
    path = path or config.JOB_SEARCH_TRACKER_PATH
    rows = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("company"):
                    rows.append(row)
    return rows


def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return round(sum(values) / len(values)) if values else 0


def tech_stack_counts(evals):
    haystacks = []
    for e in evals:
        text = " ".join([
            e.get("title", ""),
            " ".join(e.get("key_strengths", []) or []),
            " ".join(e.get("skill_gaps", []) or []),
            e.get("reason_summary", "") or "",
        ]).lower()
        haystacks.append(text)
    counts = {}
    for kw in TECH_KEYWORDS:
        pattern = re.escape(kw.lower())
        counts[kw] = sum(1 for h in haystacks if re.search(pattern, h))
    return counts


def main():
    evals = load_evaluations()
    tracker_rows = load_tracker()

    active_evals = [e for e in evals if e.get("fit_category") != "closed"]
    high_fits = sorted(
        (e for e in active_evals if e.get("fit_category") == "high"),
        key=lambda e: e.get("overall_fit", 0), reverse=True,
    )
    med_fits = [e for e in active_evals if e.get("fit_category") == "medium"]
    low_fits = [e for e in active_evals if e.get("fit_category") in ("low", "skip")]
    closed_fits = [e for e in evals if e.get("fit_category") == "closed"]

    avg_overall = avg([e.get("overall_fit") for e in active_evals])
    avg_skill = avg([e.get("skill_match") for e in active_evals])
    avg_experience = avg([e.get("experience_level_match") for e in active_evals])
    avg_company = avg([e.get("company_fit") for e in active_evals])
    avg_growth = avg([e.get("growth_potential") for e in active_evals])
    avg_red_flags = avg([e.get("red_flags") for e in active_evals])

    tech_counts = tech_stack_counts(active_evals)

    total_submitted = len(tracker_rows)
    active_in_progress = sum(
        1 for r in tracker_rows if (r.get("status") or "").strip().lower() not in TERMINAL_STATUSES
    )
    responded = sum(
        1 for r in tracker_rows if (r.get("status") or "").strip().lower() not in ({"applied"} | TERMINAL_STATUSES)
    )
    response_rate = round(100 * responded / total_submitted) if total_submitted else 0
    latest_submission = tracker_rows[-1]["date"] if tracker_rows else "N/A"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Job Search & Career Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-canvas: #12151C;
            --bg-card: #1E222D;
            --bg-card-hover: #262B39;
            --text-primary: #F0F4F8;
            --text-secondary: #94A3B8;
            --accent-gold: #FFD700;
            --accent-cyan: #00E5FF;
            --accent-green: #10B981;
            --accent-red: #EF4444;
            --border-color: #2E3545;
        }}

        .light-mode {{
            --bg-canvas: #F8FAFC;
            --bg-card: #FFFFFF;
            --bg-card-hover: #F1F5F9;
            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --accent-gold: #D97706;
            --accent-cyan: #0284C7;
            --accent-green: #059669;
            --accent-red: #DC2626;
            --border-color: #E2E8F0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}

        body {{
            background-color: var(--bg-canvas);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
            transition: background-color 0.3s, color 0.3s;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 24px;
        }}

        .header-title h1 {{
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .header-title p {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .controls {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .btn-theme {{
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
        }}

        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            background: var(--bg-card);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            width: fit-content;
        }}

        .tab-btn {{
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .tab-btn.active {{
            background: var(--accent-cyan);
            color: #000;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
        }}

        .kpi-title {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 32px;
            font-weight: 800;
            color: var(--accent-cyan);
        }}

        .kpi-card.gold .kpi-value {{
            color: var(--accent-gold);
        }}

        .kpi-card.green .kpi-value {{
            color: var(--accent-green);
        }}

        .kpi-subtext {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 6px;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}

        .card-title {{
            font-size: 16px;
            font-weight: 700;
        }}

        .search-box {{
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--bg-canvas);
            color: var(--text-primary);
            font-size: 13px;
            width: 240px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}

        tr:hover td {{
            background: var(--bg-card-hover);
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }}

        .badge-high {{ background: rgba(255, 215, 0, 0.15); color: var(--accent-gold); border: 1px solid var(--accent-gold); }}
        .badge-med {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-closed {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }}

        .job-link {{
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
        }}

        .job-link:hover {{
            text-decoration: underline;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .chart-container {{
            position: relative;
            height: 280px;
        }}

        .empty-state {{
            color: var(--text-secondary);
            font-size: 13px;
            padding: 24px;
            text-align: center;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-title">
            <h1>Executive Job Search & Career Analytics</h1>
            <p>Candidate Profile: Iouri "Yuri" Chadour — AVP / VP / SVP Data Analytics & AI</p>
        </div>
        <div class="controls">
            <button class="btn-theme" onclick="toggleTheme()">Toggle Light/Dark</button>
        </div>
    </header>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('landing')">Executive Landing</button>
        <button class="tab-btn" onclick="switchTab('fit')">5-Dimension Fit Analytics</button>
        <button class="tab-btn" onclick="switchTab('tracker')">Application Funnel</button>
    </div>

    <!-- TAB 1: EXECUTIVE LANDING -->
    <div id="tab-landing" class="tab-content active">
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Jobs Evaluated</div>
                <div class="kpi-value">{len(evals)}</div>
                <div class="kpi-subtext">All evaluated roles, all time</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Active Open Roles</div>
                <div class="kpi-value">{len(active_evals)}</div>
                <div class="kpi-subtext">Excludes closed postings</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">High-Fit Roles (80%+)</div>
                <div class="kpi-value">{len(high_fits)}</div>
                <div class="kpi-subtext">Top executive target match</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Overall Fit Score</div>
                <div class="kpi-value">{avg_overall}%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Applications Submitted</div>
                <div class="kpi-value">{total_submitted}</div>
                <div class="kpi-subtext">Logged in tracker</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Top High-Fit Target Opportunities (80%+ Fit)</div>
                    <input type="text" id="searchHigh" class="search-box" placeholder="Search title or company..." onkeyup="filterHighTable()">
                </div>
                <div style="max-height: 480px; overflow-y: auto;">
                    <table id="highTable">
                        <thead>
                            <tr>
                                <th>Overall Fit</th>
                                <th>Role Title</th>
                                <th>Company</th>
                                <th>Skill Match</th>
                                <th>Experience Match</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
"""

    if high_fits:
        for e in high_fits:
            html_content += f"""
                            <tr>
                                <td><span class="badge badge-high">{e.get('overall_fit', 0)}%</span></td>
                                <td><strong>{e.get('title', '')}</strong></td>
                                <td>{e.get('company', '')}</td>
                                <td>{e.get('skill_match', 0)}%</td>
                                <td>{e.get('experience_level_match', 0)}%</td>
                                <td><a href="{e.get('url', '#')}" target="_blank" class="job-link">View Job</a></td>
                            </tr>
"""
    else:
        html_content += '<tr><td colspan="6" class="empty-state">No high-fit (80%+) roles in the current evaluation set.</td></tr>'

    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 24px;">
                <div class="card">
                    <div class="card-title" style="margin-bottom: 16px;">Fit Category Distribution</div>
                    <div class="chart-container">
                        <canvas id="fitDonutChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title" style="margin-bottom: 16px;">Tech Stack Alignment Frequency</div>
                    <div class="chart-container">
                        <canvas id="techStackChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: FIT ANALYTICS -->
    <div id="tab-fit" class="tab-content">
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Avg Technical Skill Match</div>
                <div class="kpi-value">{avg_skill}%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Avg Experience/Seniority Match</div>
                <div class="kpi-value">{avg_experience}%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">Avg Company / Industry Fit</div>
                <div class="kpi-value">{avg_company}%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Growth Potential</div>
                <div class="kpi-value">{avg_growth}%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-title" style="margin-bottom: 16px;">Average Score Across 5 Evaluation Dimensions</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="dimensionsChart"></canvas>
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="margin-bottom: 16px;">Core Tech Stack Alignment Frequency</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="techStackChart2"></canvas>
                </div>
            </div>

            <div class="card full-width">
                <div class="card-title" style="margin-bottom: 16px;">Key Strengths & Skill Gaps Explorer (Top 15 High-Fit)</div>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Fit</th>
                                <th>Title & Company</th>
                                <th>Key Technical & Leadership Strengths</th>
                                <th>Identified Skill Gaps</th>
                                <th>Recommendation</th>
                            </tr>
                        </thead>
                        <tbody>
"""

    if high_fits:
        for e in high_fits[:15]:
            strengths_str = "<br>&bull; ".join(e.get("key_strengths", []) or []) or "None listed"
            gaps_str = "<br>&bull; ".join(e.get("skill_gaps", []) or []) or "None identified"
            html_content += f"""
                            <tr>
                                <td><span class="badge badge-high">{e.get('overall_fit', 0)}%</span></td>
                                <td><strong>{e.get('title', '')}</strong><br><small style="color:var(--text-secondary)">{e.get('company', '')}</small></td>
                                <td style="font-size:12px; color:var(--accent-cyan)">&bull; {strengths_str}</td>
                                <td style="font-size:12px; color:var(--text-secondary)">{gaps_str}</td>
                                <td style="font-size:12px;">{e.get('recommendation', '')}</td>
                            </tr>
"""
    else:
        html_content += '<tr><td colspan="5" class="empty-state">No high-fit roles to explore yet.</td></tr>'

    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 3: APPLICATION TRACKER -->
    <div id="tab-tracker" class="tab-content">
        <div class="kpi-grid">
            <div class="kpi-card green">
                <div class="kpi-title">Total Applications Submitted</div>
                <div class="kpi-value">{total_submitted}</div>
                <div class="kpi-subtext">Logged in private/job_search_tracker.csv</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">Active In-Progress</div>
                <div class="kpi-value">{active_in_progress}</div>
                <div class="kpi-subtext">Not rejected/withdrawn/closed</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Response Rate</div>
                <div class="kpi-value">{response_rate}%</div>
                <div class="kpi-subtext">Progressed beyond initial application</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Latest Submission Date</div>
                <div class="kpi-value" style="font-size:22px;">{latest_submission}</div>
                <div class="kpi-subtext">Most recent tracker entry</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card full-width">
                <div class="card-title" style="margin-bottom: 16px;">Application Submission Activity Log</div>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Company</th>
                            <th>Role</th>
                            <th>Channel</th>
                            <th>Status</th>
                            <th>Fit Score</th>
                            <th>Source</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    if tracker_rows:
        for row in tracker_rows:
            html_content += f"""
                        <tr>
                            <td>{row.get('date', '')}</td>
                            <td><strong>{row.get('company', '')}</strong></td>
                            <td>{row.get('role', '')}</td>
                            <td><span class="badge badge-high">{row.get('channel', '')}</span></td>
                            <td><span class="badge badge-med">{row.get('status', '')}</span></td>
                            <td>{row.get('fit_rating', '')}</td>
                            <td>{row.get('source', '')}</td>
                        </tr>
"""
    else:
        html_content += '<tr><td colspan="7" class="empty-state">No applications logged yet in private/job_search_tracker.csv.</td></tr>'

    tech_labels = json.dumps(list(tech_counts.keys()))
    tech_values = json.dumps(list(tech_counts.values()))

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function toggleTheme() {{
            document.body.classList.toggle('light-mode');
        }}

        function switchTab(tabName) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }}

        function filterHighTable() {{
            const input = document.getElementById('searchHigh').value.toLowerCase();
            const rows = document.querySelectorAll('#highTable tbody tr');
            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(input) ? '' : 'none';
            }});
        }}

        const techLabels = {tech_labels};
        const techValues = {tech_values};

        function techStackChartConfig() {{
            return {{
                type: 'bar',
                data: {{
                    labels: techLabels,
                    datasets: [{{
                        label: 'Mentions across active evaluations',
                        data: techValues,
                        backgroundColor: '#FFD700',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2E3545' }} }},
                        x: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ display: false }} }}
                    }}
                }}
            }};
        }}

        // Donut Chart
        new Chart(document.getElementById('fitDonutChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['High Fit (80%+)', 'Medium Fit (60-79%)', 'Low Fit (<60%)', 'Closed / Expired'],
                datasets: [{{
                    data: [{len(high_fits)}, {len(med_fits)}, {len(low_fits)}, {len(closed_fits)}],
                    backgroundColor: ['#FFD700', '#10B981', '#64748B', '#EF4444'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#94A3B8' }} }} }}
            }}
        }});

        // Tech Stack Chart (Tab 1)
        new Chart(document.getElementById('techStackChart'), techStackChartConfig());

        // Tech Stack Chart (Tab 2, same data)
        new Chart(document.getElementById('techStackChart2'), techStackChartConfig());

        // Dimensions Chart
        new Chart(document.getElementById('dimensionsChart'), {{
            type: 'bar',
            data: {{
                labels: ['Technical Skill', 'Experience Level', 'Company Fit', 'Growth Potential', 'Red Flags (Lower=Better)'],
                datasets: [{{
                    label: 'Average Score (%)',
                    data: [{avg_skill}, {avg_experience}, {avg_company}, {avg_growth}, {avg_red_flags}],
                    backgroundColor: ['#00E5FF', '#10B981', '#FFD700', '#8B5CF6', '#EF4444'],
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ max: 100, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2E3545' }} }},
                    y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    os.makedirs("_brief", exist_ok=True)
    with open("_brief/mockup.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"[OK] Generated dashboard at _brief/mockup.html "
          f"({len(evals)} evals, {len(high_fits)} high-fit, {total_submitted} applications)")


if __name__ == "__main__":
    main()
