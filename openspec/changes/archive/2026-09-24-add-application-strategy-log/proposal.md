## Why

Currently, when the `career-advisor` evaluates an application and generates a positioning strategy, this context is presented to the user but not persisted. When a tracked opportunity advances to an interview and the `deal-architect` is invoked for prep, it must re-evaluate the raw job description, the entire CV, and the profile from scratch. Storing a concise strategic decision log (`strategy.md`) with each application creates a memory loop that dramatically reduces context token costs and ensures continuity of strategy during final negotiations.

## What Changes

- The `/apply` workflow (job-application) will be updated to output a `strategy.md` file alongside `cv.md` and `cover_letter.md` in the `private/applications/YYYY-MM_Company/` folder.
- `strategy.md` will contain the positioning rationale, highlighted strengths, obfuscated gaps, compensation anchors, and interview probing areas (red flags).
- The `interview-negotiation-prep` workflow will be updated to require reading the `strategy.md` file for the tracked opportunity (if it exists) to ground its adversarial simulation and negotiation talking points.

## Capabilities

### New Capabilities

- (None)

### Modified Capabilities

- `job-application`: Requires the system to write `strategy.md` containing positioning and decision logs into the application folder.
- `interview-negotiation-prep`: Requires the system to read `strategy.md` to inform its interview simulation and negotiation prep.

## Impact

- **Affected workflows**: `/apply` (job-application drafter) and the `deal-architect` simulation (interview-negotiation-prep).
- **Storage**: Introduces a new persistent markdown file per application.
- **Cost**: Expected to significantly optimize token consumption for the `deal-architect` by replacing raw context inference with structured state.
