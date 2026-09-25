# generate-application-strategy

## Description
Generate a strategy log (strategy.md and strategy.json) for a job opportunity by invoking the career-advisor agent.

## Instructions
1. **Extract Job Information**
   - Identify the company name, role title, and job description from the user's request.
   - If the job description is not provided but a URL or tracker reference is, retrieve the job description.

2. **Invoke `career-advisor`**
   - Delegate to the `career-advisor` agent.
   - **Crucial**: Override its default instructions to read from `job_evaluations.json` by providing the job description inline.
   - Prompt: `Please read the following job description for "[Role]" at "[Company]" and generate your standard strategy report. You may ignore rule #1 about reading from job_evaluations.json. Use the private/profile.md for the candidate. Job description: ...`

3. **Persist the Strategy Cache**
   - Format the `YYYY-MM_Company` string (e.g. `2026-09_Acme-Corp`).
   - Create the directory `private/applications/<YYYY-MM_Company>/` if it does not exist.
   - Save the raw JSON output from the subagent directly to `private/applications/<YYYY-MM_Company>/strategy.json`.
   - Parse the JSON output and create a human-readable markdown file at `private/applications/<YYYY-MM_Company>/strategy.md` following the standard Strategy Log format (Positioning Angle, Highlighted Strengths, Gaps & Mitigations, Compensation Target, Red Flags / Probing Areas).
