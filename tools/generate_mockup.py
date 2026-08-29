import json
import csv
import os

evals = json.load(open('data/job_evaluations.json', encoding='utf-8'))
queue = json.load(open('data/inbox_queue.json', encoding='utf-8'))

# Filter past week evals
past_week_evals = [e for e in evals if e.get('model') == 'Antigravity-Agent-Session']

high_fits = [e for e in past_week_evals if e.get('overall_fit', 0) >= 80 and e.get('fit_category') != 'closed']
med_fits = [e for e in past_week_evals if 65 <= e.get('overall_fit', 0) < 80 and e.get('fit_category') != 'closed']
low_fits = [e for e in past_week_evals if e.get('overall_fit', 0) < 65 and e.get('fit_category') != 'closed']
closed_fits = [e for e in past_week_evals if e.get('fit_category') == 'closed' or e.get('status') == 'closed']

# Application tracker log
tracker_rows = []
if os.path.exists('job_search_tracker.csv'):
    with open('job_search_tracker.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('company'):
                tracker_rows.append(row)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Job Search & Career Analytics - Power BI Mockup</title>
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
    </style>
</head>
<body>

    <header>
        <div class="header-title">
            <h1>Executive Job Search & Career Analytics</h1>
            <p>Candidate Profile: Iouri "Yuri" Chadour — AVP / VP / SVP Data Analytics & AI</p>
        </div>
        <div class="controls">
            <button class="btn-theme" onclick="toggleTheme()">🌓 Toggle Light/Dark</button>
        </div>
    </header>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('landing')">📊 Executive Landing</button>
        <button class="tab-btn" onclick="switchTab('fit')">🎯 5-Dimension Fit Analytics</button>
        <button class="tab-btn" onclick="switchTab('tracker')">🚀 Application Funnel</button>
    </div>

    <!-- TAB 1: EXECUTIVE LANDING -->
    <div id="tab-landing" class="tab-content active">
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Jobs Scanned</div>
                <div class="kpi-value">{len(past_week_evals)}</div>
                <div class="kpi-subtext">Past 7 days inbox alerts</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Active Open Roles</div>
                <div class="kpi-value">{len(high_fits) + len(med_fits) + len(low_fits)}</div>
                <div class="kpi-subtext">Excludes closed postings</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">High-Fit Roles (80%+)</div>
                <div class="kpi-value">{len(high_fits)}</div>
                <div class="kpi-subtext">Top executive target match</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Overall Fit Score</div>
                <div class="kpi-value">68%</div>
                <div class="kpi-subtext">Across active evaluated roles</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Applications Submitted</div>
                <div class="kpi-value">{len(tracker_rows)}</div>
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
                                <th>Tech Match</th>
                                <th>Seniority</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
"""

for e in high_fits:
    html_content += f"""
                            <tr>
                                <td><span class="badge badge-high">{e['overall_fit']}%</span></td>
                                <td><strong>{e['title']}</strong></td>
                                <td>{e['company']}</td>
                                <td>{e['skill_match']}%</td>
                                <td>{e['experience_level_match']}%</td>
                                <td><a href="{e.get('url','#')}" target="_blank" class="job-link">View Job ↗</a></td>
                            </tr>
"""

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
                    <div class="card-title" style="margin-bottom: 16px;">Source Channel Breakdown</div>
                    <div class="chart-container">
                        <canvas id="sourceBarChart"></canvas>
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
                <div class="kpi-value">76%</div>
                <div class="kpi-subtext">Fabric, Snowflake, Power BI</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-title">Avg Seniority Level Match</div>
                <div class="kpi-value">88%</div>
                <div class="kpi-subtext">VP / Director / Head of</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">Avg Company / Industry Fit</div>
                <div class="kpi-value">82%</div>
                <div class="kpi-subtext">Fintech, Tech, Consulting</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Growth Potential</div>
                <div class="kpi-value">85%</div>
                <div class="kpi-subtext">AI transformation & scale</div>
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
                    <canvas id="techStackChart"></canvas>
                </div>
            </div>

            <div class="card full-width">
                <div class="card-title" style="margin-bottom: 16px;">Key Strengths & Skill Gaps Explorer</div>
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

for e in high_fits[:15]:
    strengths_str = "<br>• ".join(e.get('key_strengths', []))
    gaps_str = "<br>• ".join(e.get('skill_gaps', [])) or "None identified"
    html_content += f"""
                            <tr>
                                <td><span class="badge badge-high">{e['overall_fit']}%</span></td>
                                <td><strong>{e['title']}</strong><br><small style="color:var(--text-secondary)">{e['company']}</small></td>
                                <td style="font-size:12px; color:var(--accent-cyan)">• {strengths_str}</td>
                                <td style="font-size:12px; color:var(--text-secondary)">{gaps_str}</td>
                                <td style="font-size:12px;">{e.get('recommendation','')}</td>
                            </tr>
"""

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
                <div class="kpi-value">{len(tracker_rows)}</div>
                <div class="kpi-subtext">Logged in job_search_tracker.csv</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-title">Active In-Progress</div>
                <div class="kpi-value">{len(tracker_rows)}</div>
                <div class="kpi-subtext">Awaiting recruiter feedback</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Response Rate</div>
                <div class="kpi-value">0%</div>
                <div class="kpi-subtext">Initial tracking phase</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Latest Submission Date</div>
                <div class="kpi-value" style="font-size:22px;">{tracker_rows[0]['date'] if tracker_rows else 'N/A'}</div>
                <div class="kpi-subtext">Recent activity</div>
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

for row in tracker_rows:
    html_content += f"""
                        <tr>
                            <td>{row.get('date')}</td>
                            <td><strong>{row.get('company')}</strong></td>
                            <td>{row.get('role')}</td>
                            <td><span class="badge badge-high">{row.get('channel')}</span></td>
                            <td><span class="badge badge-med">{row.get('status')}</span></td>
                            <td>{row.get('fit_rating')}</td>
                            <td>{row.get('source')}</td>
                        </tr>
"""

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

        // Donut Chart
        new Chart(document.getElementById('fitDonutChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['High Fit (80%+)', 'Medium Fit (65-79%)', 'Low Fit (<65%)', 'Closed / Expired'],
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

        // Source Bar Chart
        new Chart(document.getElementById('sourceBarChart'), {{
            type: 'bar',
            data: {{
                labels: ['LinkedIn Job Alerts', 'Indeed Alerts'],
                datasets: [{{
                    label: 'Job Count',
                    data: [{len(past_week_evals)}, 0],
                    backgroundColor: ['#00E5FF', '#3B82F6'],
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2E3545' }} }},
                    x: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ display: false }} }}
                }}
            }}
        }});

        // Dimensions Chart
        new Chart(document.getElementById('dimensionsChart'), {{
            type: 'bar',
            data: {{
                labels: ['Technical Skill', 'Seniority Level', 'Company Fit', 'Growth Potential', 'Red Flags (Lower=Better)'],
                datasets: [{{
                    label: 'Average Score (%)',
                    data: [76, 88, 82, 85, 15],
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

        // Tech Stack Chart
        new Chart(document.getElementById('techStackChart'), {{
            type: 'bar',
            data: {{
                labels: ['Microsoft Fabric', 'Snowflake', 'Power BI', 'Azure Data Factory', 'Python', 'DAX / Tabular', 'Data Mesh'],
                datasets: [{{
                    label: 'Match Count',
                    data: [14, 28, 35, 22, 38, 18, 12],
                    backgroundColor: '#FFD700',
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2E3545' }} }},
                    x: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

os.makedirs('_brief', exist_ok=True)
with open('_brief/mockup.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
print("[OK] Generated interactive HTML mockup at _brief/mockup.html")
