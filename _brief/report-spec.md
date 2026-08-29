# Executive Career & Job Search Analytics Report Spec

## Report identity
- Report name: Executive Job Search & Career Analytics
- Semantic model: Local Power Query Model (`JobSearch_SemanticModel`) consuming `data/job_evaluations.json`, `data/inbox_queue.json`, and `job_search_tracker.csv`
- Audience: Executive Candidate (Iouri "Yuri" Chadour - AVP/VP/SVP Data & AI)
- Primary purpose: Executive monitoring of job alert pipeline, 5-dimension fit analytics, high-fit opportunity filtering, and application submission lifecycle tracking
- Delivery target: Interactive HTML Dashboard Mockup (`_brief/mockup.html`) for preview & approval before PBIP building

## User decisions and constraints
- Scope: 3-Page Executive Suite (Executive Landing + Fit Analytics + Application Funnel)
- Page count: 3 pages
- Interactivity: Tabbed navigation between pages, global filter controls, interactive data tables, search, fit score distribution charts
- Design direction: Executive HTML Mockup (Modern Executive Slate Dark & Clean Light options, crisp cards, interactive visuals)
- Delivery constraint: **Build HTML Mockup FIRST; NO PBIP building until HTML mockup approval.**

## Page plan

### 1. Executive Landing (Overview & High-Fit Opportunities)
- KPI Banner: Total Jobs Scanned (452), Active Open Roles (420), High-Fit Roles 80%+ (35), Avg Overall Fit Score (68%), Applications Submitted (1)
- Donut Chart: Opportunity Fit Score Distribution (High, Medium, Low, Closed)
- Main Table: Top Target Opportunities (80%+ Fit) with Title, Company, Overall Fit %, Tech Match %, Seniority Match %, Direct LinkedIn Link
- Bar Chart: Job Source Alert Breakdown (LinkedIn vs Indeed)

### 2. Fit Analytics & Skill Gaps
- KPI Banner: Avg Tech Match (76%), Avg Seniority Match (88%), Avg Company Fit (82%), Avg Growth Score (85%)
- Clustered Bar Chart: Average Score across 5 Evaluation Dimensions (Technical Skill, Experience Level, Company Fit, Growth Potential, Red Flags)
- Tech Stack Breakdown: Alignment frequency across Microsoft Fabric, Snowflake, Power BI, Azure, Python, DAX, SQL
- Explorer Matrix: Key Strengths vs Skill Gaps by Position

### 3. Application Funnel & Tracker
- KPI Banner: Applications Submitted (1), Active In-Progress (1), Response Rate (0%), Recent Submission Date (2026-08-27)
- Status Funnel Chart: Applied, Phone Screen, Technical Interview, Offer, Closed
- Activity Log Table: Date, Company, Role, Channel, Status, Fit Score, Notes, CV File

---

## Canonical design contract

```yaml
Design Brief:
  generated_by: powerbi-report-design
  contract_version: "1.0"
  report_name: Executive Job Search & Career Analytics
  deliverable: HTML_MOCKUP_FIRST
  pages:
    - page_name: Executive Landing
    - page_name: Fit Analytics & Skill Gaps
    - page_name: Application Funnel & Tracker
```
