---
name: generate-application-strategy
description: Generate a strategy log (strategy.md and strategy.json) for a job opportunity by invoking the career-advisor subagent. Use this skill when the user wants to backfill or update a strategy cache for a specific application.
allowed-tools: Bash, write_to_file, invoke_subagent
---

Generate an application strategy log cache.

**Input**: A job description and company name, OR a tracker URL for a job. If omitted, prompt the user for the job details.

**Steps**:

1. **Extract Job Information**
   - Identify the company name, role title, and job description from the user's request.
   - If the job description is not provided but a URL or tracker reference is, retrieve the job description.

2. **Invoke `career-advisor`**
   - Use the `invoke_subagent` tool to launch the `career-advisor` subagent.
   - **Crucial**: The `career-advisor` expects the job to be in `job_evaluations.json`. You must override this in the prompt.
   - Example prompt: `Please read the following job description for "[Role]" at "[Company]" and generate your standard strategy report. You may ignore rule #1 about reading from job_evaluations.json. Use the private/profile.md for the candidate. Job description: ...`

3. **Wait for Output**
   - Stop and wait for the `career-advisor` subagent to respond with its headless JSON strategy report.

4. **Persist the Strategy Cache**
   - Format the `YYYY-MM_Company` string (e.g. `2026-09_Acme-Corp`).
   - Create the directory `private/applications/<YYYY-MM_Company>/` if it does not exist.
   - Save the raw JSON output from the subagent directly to `private/applications/<YYYY-MM_Company>/strategy.json`.
   - Parse the JSON output and create a human-readable markdown file at `private/applications/<YYYY-MM_Company>/strategy.md` using the following format:

   ```markdown
   # Strategy Log
   
   **Positioning Angle**: [Insert positioning_rationale]
   
   **Highlighted Strengths**: 
   - [Extract strengths/highlights from the rationale/diffs]
   
   **Gaps & Mitigations**: 
   - [Extract any gaps or mitigations mentioned]
   
   **Compensation Target**: [Insert from compensation_signal or verdict]
   
   **Red Flags / Probing Areas**: [Insert any recruiter bias or red flags mentioned in the verdict]
   ```

5. **Display Summary**
   - Inform the user that the strategy log cache has been generated and saved to both `strategy.md` and `strategy.json`.
