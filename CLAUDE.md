# Job Application Assistant for [YOUR_NAME]

<!-- SETUP: This file is populated by running /setup -->
<!-- After running /setup, all [PLACEHOLDER] tokens will be replaced with your actual information -->

## Role
This repo is a job application workspace. Claude acts as a career advisor and application assistant for [YOUR_NAME], helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

<!-- This section is auto-populated by /setup. You can also fill it in manually. -->

### Identity
- **Name:** Iouri "Yuri" Chadour
- **Location:** Miami-Fort Lauderdale Area, FL
- **Phone:** (718) 431-3717
- **Email:** iouri.chadour@gmail.com
- **Languages:** English (fluent), Russian (native)
- **Status:** Employed at Bayview Asset Management (AVP, Data Analytics & AI); actively exploring
- **LinkedIn headline:** "Data Analytics & AI Leader | Modern Data Platforms (Fabric, Snowflake) | Data Mesh Architecture | Team Builder"

### Education
- **B.S. in Computer Technology** (2005-2007) - Globe Institute of Technology, New York

### Professional Experience
- **AVP, Data Analytics & AI** (09/2024 - Present) - **Bayview Asset Management** (Ft. Lauderdale, FL)
  - Head of Data & Analytics Strategy for enterprise-wide data and analytics vision
  - Led BI framework implementation with standardized processes, templates, and self-service model
  - Architected Investor Database and Asset Management Portfolio Dashboard serving Senior Management
  
- **Technology Manager (SVP)** (04/2020 - 09/2024) - **Lazard Frères** (Remote)
  - Technology leader across Finance, Testing Automation, Risk Management business areas
  - Led PowerBI and Power Platform rollout and adoption; established design patterns and templates
  - Delivered multiple end-to-end data analytics solutions (pipelines, warehousing, dashboards)

- **Senior Software Developer (VP)** (01/2015 - 04/2020) - **Lazard Frères** (New York, NY)
  - Led ERP Financial system upgrades and enhancements across multiple modules
  - Custom AP automation with document scanning, OCR, workflows, mobile interface
  - Built and led team of data engineers and report developers

- **Technical Manager** (04/2011 - 12/2014) - **Guardian Life** (New York, NY)
  - Managed application development teams supporting Corporate Finance, Compliance, Audit, Information Security
  - Led ERP customizations, platform upgrades, and new module implementations

- **Senior Developer** (04/2005 - 10/2011) - **Guardian Life** (New York, NY)
  - Designed and implemented software solutions for corporate systems
  - Managed team of internal and consulting staff

- **Lead Developer** (01/2001 - 04/2005) - **AXA Financial** (New York, NY)
  - Led design and implementation of highly effective software solutions
  - Managed team of 3-4 developers during design and development phases

### Technical Skills
- **Primary:** Data Analytics, Business Intelligence, Modern Data Platforms (PowerBI, Microsoft Fabric, Snowflake), Data Architecture (data mesh, semantic models, lakehouse patterns), Cloud (Azure, AWS), Python, SQL, Team Leadership
- **Secondary:** ERP Systems (Oracle Financials, PeopleSoft), Custom Application Development, Data Governance, Vendor Management, Project Management
- **Domain:** Enterprise data analytics, financial systems, compliance and audit technology, cloud migration, analytics modernization
- **Software:** PowerBI, Microsoft Fabric, Snowflake, Azure Data Factory, Power Automate, Informatica, Alteryx, Snaplogic, Python (Pandas, NumPy), SQL Server, Tabular Editor, DAX, Shell Scripting

### Certifications
- **Microsoft Certified: Power BI Data Analyst Associate** - 2024
- **AWS Certified Solutions Architect – Associate** - 2020
- **SnowPro Core Certification** - 2021
- **PeopleTools 8 Advanced Developer Certified Expert** - 2010
- **R Programming Certification** - 2019

### Behavioral Profile
- **Strategic Vision + Hands-On Execution** - Balances enterprise-wide data architecture thinking with pragmatic implementation and team leadership
- **Empowering Teams** - Passionate about enabling business stakeholders and technical teams with tools, knowledge, and autonomy to achieve their goals
- **Innovation-Driven** - Constantly adopting and championing cutting-edge technologies (Fabric, data mesh, AI agents); establishes scalable frameworks and best practices
- **Cross-Functional Collaborator** - Works effectively across business units, vendor partnerships, and global teams to align on vision and drive transformation

**Strengths:** Deep technical expertise in modern data platforms combined with architecture and strategy; proven ability to build high-performing teams; track record of large-scale technology transformations; excellent at translating complex business problems into elegant technical solutions; comfortable balancing hands-on work with strategic leadership

**Growth areas:** Generative AI and Copilot integration (theoretical knowledge strong; production experience emerging); accelerating speed to learning in rapidly evolving AI/ML landscape

**Thrives in:** Collaborative environments with executive sponsorship for modernization; roles valuing both strategic vision and hands-on technical depth; teams embracing change and experimentation; business partnership models (not siloed IT); autonomy to drive architecture decisions

### What Excites You
- Designing and implementing modern data architectures (data mesh, semantic models, lakehouse) that scale across enterprises
- Leveraging AI and Copilot to democratize analytics and empower business users
- Building and mentoring technical teams that deliver excellence
- Driving organizational transformation through technology adoption and cultural change
- Solving complex business problems with elegant, maintainable technical solutions

### Target Sectors & Roles
**Industries:** Financial Services (JP Morgan, Goldman Sachs, BlackRock), Technology & Cloud (Microsoft, Databricks, Palantir), Consulting (Accenture, Deloitte, McKinsey), Enterprise SaaS (Salesforce, monday.com), any organization with strong data culture and modern cloud stack

**Target Roles:** VP Data Analytics, Chief Data Officer, Principal Data Architect, Head of Data Engineering, Director of Analytics Engineering, SVP Technology

### Deal-Breakers
- Legacy-only environments with no path to modernization or adoption of current-generation tools
- Siloed IT roles without business partnership or strategic influence
- Organizations resistant to cloud migration or modern data practices
- Purely operational/maintenance-focused roles without innovation component
- Micromanagement or cultures that devalue technical expertise

## Repo Structure
- `cv/` - LaTeX CV variants (moderncv template, banking style)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.claude/skills/` - AI skill definitions for the application workflow
- `.agents/skills/` - Job search CLI tools

## Workflow for New Job Applications
1. User provides a job posting (URL or text)
2. **Always evaluate fit first**: skills match, experience match, behavioral/culture match. Present this assessment to the user before proceeding.
3. If good fit: create targeted CV (`cv/main_<company>.tex`) and cover letter (`cover_letters/cover_<company>_<role>.tex`)
4. **Verify both documents** (see Verification Checklist below)
5. Prepare interview talking points based on the role requirements and your strengths

**Important:** When mentioning agentic coding or AI tooling in CVs/cover letters, explicitly reference **Claude Code** by name.

## Verification Checklist
After creating or updating a CV or cover letter, re-read the generated file and verify **all** of the following before presenting to the user. Report the results as a pass/fail checklist.

### Factual accuracy
- [ ] All claims match actual profile (CLAUDE.md / candidate profile) - no fabricated skills, experience, or achievements
- [ ] Job titles, dates, company names, and locations are correct
- [ ] Contact details are correct
- [ ] All company-specific claims (partnerships, products, technology, expansions) have been independently verified via WebFetch/WebSearch - do not trust reviewer agent research without verification

### Targeting
- [ ] Profile statement / opening paragraph is tailored to the specific role (not generic)
- [ ] Skills and experience bullets are reframed to match the job requirements
- [ ] Key job requirements are addressed (with gaps acknowledged where relevant)
- [ ] Nice-to-have requirements are highlighted where there is a match

### Consistency
- [ ] CV follows the standard 2-page moderncv/banking format
- [ ] Cover letter uses cover.cls template and established structure
- [ ] Tone is consistent across CV and cover letter
- [ ] No contradictions between CV and cover letter content

### Quality
- [ ] No LaTeX syntax errors (balanced braces, correct commands)
- [ ] No spelling or grammar errors
- [ ] Agentic coding / AI tooling references mention **Claude Code** by name
- [ ] Cover letter is addressed to the correct person (or "Dear Hiring Manager" if unknown)
- [ ] Cover letter fits approximately one page

### Compiled PDF verification (MANDATORY - never skip)
Both documents MUST be compiled and visually inspected via the Read tool on the PDF output. "Looks fine in the .tex" is not acceptable - LaTeX page-break decisions are unpredictable. Iterate until these all pass:
- [ ] CV compiled with **lualatex** (pdflatex often fails on modern MiKTeX with fontawesome5 font-expansion errors). Cover letter compiled with **xelatex** (cover.cls requires fontspec).
- [ ] **CV is exactly 2 pages** - not 1, not 3
- [ ] **No orphaned `\cventry` titles** - a job/education title must never sit at the bottom of a page with its bullets spilling to the next page. Use `\needspace{5\baselineskip}` before each `\cventry` to prevent this, and `\enlargethispage{2-3\baselineskip}` to rescue a trailing section that just barely spills
- [ ] **Cover letter is exactly 1 page** - signature block must fit with the body, never overflow
- [ ] **Cover letter bullet font matches body font** - `\lettercontent{}` must not wrap `\begin{itemize}...\end{itemize}` (the command's trailing `\\` errors on `\end{itemize}`, and moving itemize outside loses the Raleway font). Standard pattern: close `\lettercontent{}`, then wrap the list in `{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont \begin{itemize}...\end{itemize}\par}`
