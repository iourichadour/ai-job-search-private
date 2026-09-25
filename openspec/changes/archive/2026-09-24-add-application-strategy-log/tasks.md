## 1. Application Drafter Modification (job-application)

- [x] 1.1 Update the `/apply` workflow or `career-advisor` agent instructions to construct the `strategy.md` file and output it to `private/applications/YYYY-MM_Company/strategy.md` alongside the CV and cover letter. Verify by running the workflow on a test job and checking that the file is created with the required sections (positioning, strengths, gaps, comp target, red flags).

## 2. Interview Prep Modification (interview-negotiation-prep)

- [x] 2.1 Update the `deal-architect` agent instructions or the interview prep pre-flight logic to check for the existence of `strategy.md` in the target application directory. Verify by running a unit test or manual test simulating a missing file to ensure graceful fallback.
- [x] 2.2 Modify the context-loading step for `deal-architect` to ingest `strategy.md` when it exists, instructing the agent to ground its simulation and negotiation talking points using this file. Verify by running the simulation on a test opportunity with a dummy `strategy.md` and observing the output reflects the dummy strategy.

## 3. End-to-End Verification

- [x] 3.1 Run an end-to-end test starting from a mock HIGH_FIT job evaluation to generate the `cv.md`, `cover_letter.md`, and `strategy.md`.
- [x] 3.2 Update the test opportunity's status to `FINAL_ROUND` in `private/job_search_tracker.csv` and trigger the interview negotiation prep, verifying that it correctly pulls context from the generated `strategy.md`.
