## Why

`/apply` and the standalone `generate-application-strategy` skill both produce `strategy.md` for an application, but with unequal rigor: the skill delegates to `career-advisor` (scored against `data/positioning_rubric.md`) and verifies every claim via `evidence-verifier`, while `/apply` writes `strategy.md` ad hoc from whatever context the drafter already has, with no dedicated rubric pass and no claim-level verification. `deal-architect` reads whichever version exists and treats them as equivalent inputs, so interview prep quality silently depends on which path produced the file. Unifying on one generation path removes that inconsistency without touching `deal-architect` (it already reads `strategy.md`/`strategy.json` generically) or the fit-evaluation rubrics used elsewhere.

## What Changes

- `/apply` Step 2 no longer writes `strategy.md` ad hoc. It delegates strategy generation to the `generate-application-strategy` skill's flow (invoke `career-advisor` with the job-evaluations-file override, then `evidence-verifier`), producing both `strategy.json` and `strategy.md`.
- Before generating, `/apply` checks whether `private/applications/YYYY-MM_Company/strategy.json` already exists for the target folder. If it does, it reuses the existing file instead of regenerating (avoids paying for `career-advisor` + `evidence-verifier` again when the standalone skill already produced one for this company, or on a re-run of `/apply` for the same folder).
- No automatic staleness detection (no profile/JD hashing or mtime comparison). Regeneration only happens when the cached file is absent, or the user explicitly asks to refresh it.
- `/apply`'s Step 1 fit-evaluation gate (`04-job-evaluation.md`) is unchanged — this change does not consolidate it with `career-advisor`'s or `job-evaluator`'s rubrics.
- The standalone `generate-application-strategy` skill's own behavior is unchanged: invoking it directly always regenerates (the explicit re-run is itself the refresh signal).
- When `/apply` delegates strategy generation, it passes the job posting's URL (already extracted in Step 0, or known from the tracker) through to `career-advisor` and ensures the resulting `strategy.json`'s `url` field is populated, rather than left blank. This preserves the URL as the linking key back to `private/inbox_queue.json` / `private/job_evaluations.json` / `private/job_search_tracker.csv`, all of which are already keyed by URL — today `strategy.json.url` is frequently left empty (confirmed in the `2026-08_Trace3` artifact) even though the schema has always had the field.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `job-application`: The "Application files are written to a per-application folder" requirement changes from "the system writes a strategy log" (unspecified generation method) to "the system delegates strategy log generation to the `generate-application-strategy` skill, reusing an existing `strategy.json` for the folder when present instead of regenerating, and passing the job's URL through so `strategy.json.url` is populated rather than left blank."

## Impact

- **Affected code**: `.claude/commands/apply.md` (Step 2's Strategy Log section, Step 6's file list) and its Antigravity equivalent, if one exists.
- **No changes**: `career-advisor`, `evidence-verifier`, `deal-architect`, `job-evaluator`, `data/positioning_rubric.md`, `.claude/skills/job-application-assistant/04-job-evaluation.md`, the `generate-application-strategy` skill itself.
- **Output change**: `/apply` now writes `strategy.json` in addition to `strategy.md` (previously `strategy.md` only), with its `url` field populated.
- **No change** to the `generate-application-strategy` skill's own instructions — the URL fix is scoped to what `/apply` passes into the delegation call, not the skill's standalone invocation path (which the user did not ask to reopen).
