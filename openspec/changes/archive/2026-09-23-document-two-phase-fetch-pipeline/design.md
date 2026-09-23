## Context

`tools/fetch_inbox.py` was rewritten at some point into a two-phase pipeline (this was tracked only in an ad-hoc planning note under `documents/plans/`, never as a formal spec requirement). The current implementation already matches the design: collect all URLs from Gmail first with no browser cost, deduplicate within the batch and against the existing queue, then browser-fetch descriptions only for genuinely new URLs, writing a scratch file and a timestamped per-run log along the way.

This change exists purely to close the spec gap — no code changes are needed, since the shipped implementation already satisfies the new requirement (verified directly against the current `tools/fetch_inbox.py` source during `centralize-config-and-private-store`'s implementation).

## Goals / Non-Goals

**Goals:**
- Give the already-shipped two-phase pipeline a formal spec requirement so a future rewrite has a documented contract to be checked against.

**Non-Goals:**
- No behavior change. This is a documentation-only change.
- Not re-litigating dashboard/reporting architecture — see the note below on a superseded alternative, kept only for historical context.

## Decisions

### Decision: Document the shipped two-phase architecture, not an alternative that was never built
**Chosen**: Formalize only the two-phase collect-then-fetch pipeline, since it is what actually shipped and is verifiably live in `tools/fetch_inbox.py` today.
**Context (not a decision, historical record only)**: The same planning notes that described this two-phase rewrite also proposed a separate, unrelated Power BI Desktop (PBIP) project as the evaluation dashboard — a multi-page report with a `Jobs` table, expanded strength/gap/red-flag tables, and DAX measures. That PBIP approach was never built. The dashboard need was instead met by a simpler single-file HTML dashboard (`tools/generate_mockup.py` writing `_brief/mockup.html`), which shipped and is in active use, with further dashboard enhancements tracked separately by the already-existing `eval-dashboard` OpenSpec change (deferred, unrelated to this change). Because the PBIP alternative was never implemented, it does not get a spec requirement here — there is nothing shipped to document a contract for.

## Migration Plan

None — this is a documentation-only change. Sequencing: apply (mark the single task complete, since the described behavior is already live) and archive.
