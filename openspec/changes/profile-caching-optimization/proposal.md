## Why

`data/profile.md` (139 lines, ~10KB, ~2,000-2,500 tokens) is currently read in full by every evaluator, once per job in the Gemini API fallback path (`evaluate_job_api()` embeds the entire profile text in each per-job prompt) and once per subagent/session invocation in the interactive-agent paths (Claude Code, Gemini CLI, Antigravity). At current evaluation volume (850+ evaluations run to date, e.g. 423 jobs scored across 22 parallel batches in the SCRUM-12 pass), this redundant full-profile inclusion is a real, recurring token cost with no caching in place today. A smaller, purpose-built extraction of the profile's fit-relevant facts, generated once and reused until the source profile changes, would cut this cost without requiring any change to the scoring rubric or record schema.

## What Changes

- Add `tools/extract_profile.py`, a rule-based (non-LLM) parser that reads `data/profile.md` and extracts the facts the evaluation rubric actually scores against (technical skills/tools, target roles/industries/companies, target compensation band, deal-breakers/avoid-patterns, seniority level) into a compact `data/profile.cache.json`.
- Check `data/profile.cache.json` into git (not gitignored) alongside `data/profile.md`, since it is a small derived artifact evaluators depend on directly.
- Define and implement a freshness mechanism so evaluators never silently score against a stale cache when `data/profile.md` has changed since the cache was last generated (exact mechanism — hash/mtime check vs. required manual regen step — is a design decision, not finalized here).
- Update every evaluator entry point that currently reads the full `data/profile.md` to read `data/profile.cache.json` instead: `.claude/agents/job-evaluator.md`, `.agents/agents/job-evaluator.agent.md`, `.gemini/GEMINI.md` (interactive-agent paths), and `tools/evaluate_jobs_gemini.py`'s `load_profile()` / `evaluate_job_api()` (Gemini API fallback path).
- No change to the scoring rubric, the 5-dimension weighting, the `overall_fit` formula, or the evaluation record schema — this is purely an input-source optimization.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `job-evaluation`: the "Interactive-agent evaluation is the primary path" requirement currently names `data/profile.md` as the literal scoring input (both directly and via the Gemini-API-fallback requirement, which shares the same profile-loading mechanism). This changes the required input artifact to a generated cache, and adds a new requirement that the cache must be regenerated (or evaluation must be blocked/warned) whenever `data/profile.md` changes, so no evaluation silently scores against stale profile data.

## Impact

- **New file**: `tools/extract_profile.py` (parser/generator, tracked).
- **New file**: `data/profile.cache.json` (generated output, tracked).
- **Modified**: `tools/evaluate_jobs_gemini.py` (`load_profile()`, `evaluate_job_api()` prompt construction).
- **Modified**: `.claude/agents/job-evaluator.md`, `.agents/agents/job-evaluator.agent.md`, `.gemini/GEMINI.md` — each currently instructs its evaluator to "read `data/profile.md`"; each is repointed at the cache.
- **Risk to manage in design**: the current rubric's `company_fit` and `growth_potential` dimensions draw on narrative sections of `data/profile.md` (behavioral profile, "thrives in", key AI-driven project narratives) that a purely structured-fact extraction could flatten or drop, potentially degrading scoring quality for those two dimensions. Design must decide what is safe to compress to structured fields versus what must be carried through as short verbatim text.
- **No change** to `data/inbox_queue.json`, `data/job_evaluations.json`, the evaluation record schema, or any downstream consumer of evaluation results.
- **No dependency** on `centralize-config-and-private-store`, `headhunter-agent`, or `eval-dashboard` — this change is independent and can land in any order relative to those, though if `centralize-config-and-private-store` lands first and moves `data/profile.md` under `private/`, the cache's source/output paths will need the same relocation (noted for whichever change lands second, not a blocker for this one).
