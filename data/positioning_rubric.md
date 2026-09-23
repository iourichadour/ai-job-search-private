# Positioning Rubric: Executive Data & Analytics Leadership

## Purpose

Scores HIGH_FIT/FIT opportunities for positioning strategy, resume tailoring, and negotiation readiness. Distinct from and independent of the job-evaluation rubric (which answers "should I apply?"), this rubric answers "how do I position myself and negotiate this specific role?"

## Scoring Dimensions

Each dimension is scored 0-100 with named anchors. Weights sum to 100%.

### 1. Title Level Fit (20%)

Alignment between the role's seniority/scope and the candidate's demonstrated experience level.

- **High (80-100)**: Role is VP/SVP/C-suite or equivalent director-level with executive scope; candidate has held similar or higher titles with comparable scope (built teams, drove strategy, enterprise-wide impact).
- **Medium (50-79)**: Role is senior manager/principal/director level; candidate has some equivalent experience but may need to emphasize a specific dimension (e.g., has senior IC experience but limited P&L ownership).
- **Low (0-49)**: Role is mid-level IC or coordinator; candidate is overqualified or lacks clear title-level precedent.

### 2. Dual-Threat Fit (25%)

The role's need for both strategic leadership AND hands-on technical depth, and the candidate's credibility in both.

- **High (80-100)**: Role explicitly expects both C-suite strategic thinking AND modern technical hands-on work (e.g., "VP Data who codes in DAX/Python"; "Chief Data Officer building Fabric platforms"); candidate has proven track record doing both (not just hiring people to do it).
- **Medium (50-79)**: Role values both but leans one direction (e.g., mostly strategic with some technical review; mostly hands-on with some mentoring); candidate has both but stronger in one area.
- **Low (0-49)**: Role is purely strategic or purely tactical; candidate's strength is in the opposite domain.

### 3. Domain Fit (20%)

Alignment between the role's data/analytics/technology domain and the candidate's core expertise.

- **High (80-100)**: Role centers on Fabric, Power BI, Snowflake, data mesh, or modern cloud data platforms the candidate has deep, recent experience with; or roles leading analytics engineering, data strategy, or data governance in similar company stage/vertical.
- **Medium (50-79)**: Role touches relevant domains but also includes legacy tools, ERP, or other systems the candidate has experience with but is not primary focus; or similar domain but earlier career stage.
- **Low (0-49)**: Role's primary domain (e.g., pure ML engineering, DevOps infrastructure, BI-only front-end) differs materially from candidate's background.

### 4. Compensation Signal (15%)

Fit between the role's indicated compensation and the candidate's stated target band ($200K-$300K total comp, per `data/profile.md`).

- **High (80-100)**: Role's indicated comp (salary + bonus + equity typical range) is clearly in or above the target band; no negotiation friction expected.
- **Medium (50-79)**: Role's comp is at the lower end of the band or slightly below typical ranges; some negotiation likely or trade-offs expected.
- **Low (0-49)**: Role's comp is significantly below the target band with no clear upside; or comp data is missing and company stage suggests a below-band norm.

### 5. Technology Fit (20%)

Alignment between the role's required/preferred technology stack and the candidate's current expertise.

- **High (80-100)**: Role's stack closely matches candidate's primary tools (Fabric, Power BI, Snowflake, Azure, DAX, Python/SQL, MCP/AI agents); minimal ramp needed.
- **Medium (50-79)**: Role uses 3-4 of candidate's primary tools plus 1-2 secondary/adjacent areas (e.g., Salesforce, Databricks, dbt); ramp is manageable.
- **Low (0-49)**: Role's stack is primarily outside candidate's documented expertise (e.g., pure legacy ERP, Tableau/Qlik without modern cloud, Java backend).

## Scoring Formula

```
positioning_score = round(
    title_level_fit * 0.20
  + dual_threat_fit * 0.25
  + domain_fit * 0.20
  + compensation_signal * 0.15
  + technology_fit * 0.20
)
```

Positioning scores range 0-100. No red-flag deduction (unlike the job-evaluation rubric) — those are already filtered out by the upstream `fit_category` gate before a job reaches this rubric.

## Output Schema

For each scored job, produce:

```json
{
  "title": "string, non-empty",
  "company": "string, non-empty",
  "url": "string, if available",
  "title_level_fit": "integer 0-100",
  "dual_threat_fit": "integer 0-100",
  "domain_fit": "integer 0-100",
  "compensation_signal": "integer 0-100",
  "technology_fit": "integer 0-100",
  "positioning_score": "integer 0-100, computed per formula above",
  "positioning_rationale": "string, max one paragraph, names a specific executed outcome/technology from data/profile.md and maps it to cost/risk/revenue/scale for this role",
  "resume_bullet_diffs": [
    "string, 3-5 proposed replacements in 'CHANGE: [old] -> [new]' format — proposals only, not file edits"
  ],
  "verdict": "string, 2-5 sentences, a judgment on whether and how strongly to pursue — must add something not already stated in the rationale"
}
```

All fields are required. `resume_bullet_diffs` must contain 3-5 entries.
