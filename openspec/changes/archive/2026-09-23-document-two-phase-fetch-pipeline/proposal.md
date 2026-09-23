## Why

`tools/fetch_inbox.py`'s current implementation already runs a two-phase pipeline (collect all candidate URLs from Gmail first with no browser cost, deduplicate against the existing queue, then browser-fetch descriptions only for genuinely new jobs — plus a timestamped per-run log file) and a scratch-write step for auditability. None of this is captured as a formal requirement in `openspec/specs/inbox-ingestion/spec.md` — the architecture shipped without ever being speced, so there's no documented contract a future rewrite of this script would be checked against.

This gap was discovered while reviewing legacy planning notes (`documents/plans/`) as part of the `centralize-config-and-private-store` change's `documents/` audit. Those notes (an implementation plan for exactly this two-phase rewrite, since fully implemented) also proposed a separate, never-built Power BI Desktop (PBIP) report for the evaluation dashboard — abandoned in favor of the single-file HTML dashboard that shipped instead (`tools/generate_mockup.py` / `_brief/mockup.html`, itself covered by the existing `eval-dashboard` OpenSpec change). That abandoned alternative is noted here for the historical record but does not warrant its own spec, since nothing shipped from it.

## What Changes

- **New requirement** added to `openspec/specs/inbox-ingestion/spec.md`: the ingestion pipeline SHALL run in two phases (collect-and-dedupe, then fetch-only-new) with a per-run log file, rather than fetching descriptions inline during the Gmail scan.
- No code changes — this documents already-shipped, already-verified behavior. `tools/fetch_inbox.py`'s current structure (scratch write → intra-batch dedup → filter against existing queue → browser-fetch phase → per-run `logs/fetch_inbox_<timestamp>.log`) already satisfies the new requirement.

## Capabilities

### Modified Capabilities
- `inbox-ingestion`: adds a requirement documenting the two-phase collect-then-fetch pipeline architecture and per-run logging, which the shipped code already implements.

## Impact

- **Affected specs**: `openspec/specs/inbox-ingestion/spec.md` (one new requirement, delta-applied then archived).
- **Affected code**: none — retroactive documentation of shipped behavior, verified against the current `tools/fetch_inbox.py` implementation.
- **Origin**: superseded, now-deleted planning notes under `documents/plans/` (removed as part of `centralize-config-and-private-store`'s `documents/` personal-content audit — those notes predated this repo's `private/` convention and contained candidate-identifying content that didn't belong tracked in git).
