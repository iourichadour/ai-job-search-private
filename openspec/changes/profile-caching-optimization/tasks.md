## 1. Extractor script

- [ ] 1.1 Create `tools/extract_profile.py` with a default (no-flag) mode that parses `data/profile.md` by its known `##`/`###` section headers and writes `data/profile.cache.json` per design.md Decision 3 (current role kept in full, pre-2020 roles condensed to one line each, Education/Certifications condensed to one line each, all other listed sections kept near-verbatim). Verify by running it and inspecting the generated `data/profile.cache.json` against `data/profile.md` section-by-section.
- [ ] 1.2 Add `_meta.source_hash` (SHA-256 of `data/profile.md` contents) and `_meta.generated_at` (ISO 8601 timestamp) to the generated cache. Verify by regenerating twice with no source change and confirming `source_hash` is identical both times.
- [ ] 1.3 Add a `--check` flag that hashes the current `data/profile.md`, compares against the cache's `_meta.source_hash`, and exits non-zero with a clear message if they differ or the cache file doesn't exist (exits 0 silently if current). Verify with three cases: cache missing, cache stale (edit `data/profile.md` after generating), cache current.
- [ ] 1.4 Make the extractor exit non-zero with a message naming the specific missing/unrecognized section if `data/profile.md`'s section headers don't match what it expects (design.md Decision 4). Verify by temporarily renaming a section header in a scratch copy and confirming the script fails loudly instead of silently omitting it.

## 2. Generate and commit the initial cache

- [ ] 2.1 Run `tools/extract_profile.py` against the current `data/profile.md` and commit the resulting `data/profile.cache.json`. Verify the file is tracked (not gitignored) via `git status`/`git add`.

## 3. Wire up the Gemini API fallback path

- [ ] 3.1 In `tools/evaluate_jobs_gemini.py`, replace `load_profile()`'s direct read of `data/profile.md` with a load of `data/profile.cache.json`, first running the `--check` logic (import and call directly, or shell out) and auto-regenerating via `extract_profile.py` if stale/missing, printing a one-line notice when it does (design.md Decision 2). Verify by running `evaluate_jobs_gemini.py` against a small batch with a deliberately stale cache present and confirming the notice prints and evaluation proceeds correctly.
- [ ] 3.2 Confirm `evaluate_job_api()`'s prompt construction now embeds the cache content (not the full `data/profile.md` text) per job. Verify by inspecting the constructed prompt string for one job.

## 4. Wire up the interactive-agent paths

- [ ] 4.1 Update `.claude/agents/job-evaluator.md` to instruct the agent to run `python tools/extract_profile.py --check` first, regenerate via `python tools/extract_profile.py` if it reports stale/missing, then read `data/profile.cache.json` instead of `data/profile.md` for scoring. Verify by re-reading the file and confirming no remaining reference to reading `data/profile.md` directly.
- [ ] 4.2 Apply the equivalent update to `.agents/agents/job-evaluator.agent.md`. Verify the same way.
- [ ] 4.3 Apply the equivalent update to `.gemini/GEMINI.md`'s inline-scoring instructions for the Standalone Gemini CLI path. Verify the same way.

## 5. Cross-check for stragglers

- [ ] 5.1 Grep the repo for remaining `data/profile.md` references in evaluator-facing instruction files (`.claude/`, `.agents/`, `.gemini/`) and confirm every evaluation-scoring reference now points at `data/profile.cache.json` (non-evaluation references — e.g. `/setup`, `/reset`, `/expand`, `job-application-assistant`, README/SETUP docs — are out of scope and SHALL NOT be changed, since they concern authoring/maintaining the profile itself, not scoring against it).

## 6. Live verification

- [ ] 6.1 Run a small live evaluation batch (5-10 pending jobs) through the interactive-agent path (Claude Code) using the cache and confirm scores are directionally consistent with what the same jobs would score using the full profile (spot-check `company_fit` and `growth_potential`, the two dimensions design.md flags as highest-risk for cache-compression quality loss).
- [ ] 6.2 Run a small live batch through the Gemini API fallback path (`tools/evaluate_jobs_gemini.py`) and confirm the auto-regeneration notice and evaluation both work end-to-end with a real `GEMINI_API_KEY`.
- [ ] 6.3 Confirm `openspec validate --changes profile-caching-optimization --strict` passes before archiving.
