## Why

During large-scale job evaluation passes (e.g., evaluating hundreds of jobs across the past 30 days), the interactive agent workflow encountered six major operational bottlenecks:
1. **Upstream Noise**: 10–15% of ingested items were aggregated search digests (e.g., "9,000+ Director Jobs") or broken search links, polluting the queue and wasting agent tokens.
2. **Batch & Swarm Friction**: Small batch sizes (~20 jobs) caused excessive subagent proliferation (22 subagents over 4 waves), resulting in high latency, transcript bloat, and context fragmentation.
3. **Brittle Transcript Scraping**: Subagents output JSON into chat messages, requiring brittle regex and bracket parsing of multi-megabyte transcript logs to recover evaluations.
4. **Validation Failures on Red-Flag Penalties**: Jobs with 100% red flags produced negative `overall_fit` scores (e.g., -10%), failing rigid schema validation and requiring manual repair cycles.
5. **Lack of Native Batch Preparation**: Preparing batch slices required ad-hoc Python scripts rather than a first-class CLI command.
6. **Silent Date Truncation & Backlog Conflation**: Calling `--filter-only` silently defaulted to `--days 14`, causing jobs older than two weeks to be ignored. Furthermore, workflow prompts conflated inbox fetching with evaluation, causing agents to evaluate only "today's" incoming alerts rather than continuing evaluation on all pending jobs in `data/inbox_queue.json` when the fetch phase is bypassed.

Optimizing these stages will make future inbox evaluations ~5x faster, fully automated, and resilient against schema rejection and accidental backlog truncation.

## What Changes

- **Upstream Digest Filtering**: Update `tools/fetch_inbox.py` to filter out search alert digest emails, aggregated listings, and invalid search URLs during Gmail ingestion.
- **Auto-Clamping in Validation**: Update `tools/evaluate_jobs_gemini.py` to automatically clamp `overall_fit` (and all individual dimensions) to the valid range `[0, 100]` prior to schema validation, eliminating rejections from negative weighted scores.
- **Batch Preparation CLI**: Add `--prepare-batches` CLI option to `tools/evaluate_jobs_gemini.py` that slices pending jobs into optimal batch sizes (50–70 jobs), saves them to `data/eval_batches/`, and generates ready-to-run subagent task specifications.
- **Direct File Output & Multi-File Save**: Update `--save-evaluations` to accept glob patterns (e.g., `data/eval_batches/*.evaluated.json`) or directories, and update subagent instructions to output evaluation arrays directly to disk rather than chat transcripts.
- **Queue Backlog Continuation & No Silent Date Cutoff**: Remove the silent 14-day default in `evaluate_jobs_gemini.py` so that `--filter-only` and `--prepare-batches` process all pending unevaluated jobs in the queue unless an explicit date range is passed. Update workflow prompts and commands across `.gemini/`, `.claude/`, and `.agents/` to explicitly instruct agents that bypassing the fetch phase means evaluating the full pending backlog in `data/inbox_queue.json`, not just today's jobs.
- **Proven Model Provenance**: Formally codify `antigravity-agent-session` alongside `claude-agent-session` and `gemini-agent-session` in the spec.

## Capabilities

### New Capabilities
- `inbox-ingestion`: Upstream Gmail alert parsing rules that detect and discard search digest aggregations and non-posting links before adding them to `data/inbox_queue.json`.

### Modified Capabilities
- `job-evaluation`: Enhance evaluation schema handling with automatic 0–100 score clamping, add multi-file/glob persistence to `--save-evaluations`, add automated batch slicing CLI support (`--prepare-batches`), and remove silent date truncation to evaluate all pending queue backlog by default.

## Impact

- **Code files affected**:
  - `tools/fetch_inbox.py` (digest link pattern matching and filtering)
  - `tools/evaluate_jobs_gemini.py` (clamping in `validate_evaluation_record`, glob parsing in `--save-evaluations`, new `--prepare-batches` flag, remove silent 14-day default)
  - `.agents/agents/job-evaluator.agent.md` & `.claude/agents/job-evaluator.md` (instructions updated to write evaluations directly to file)
- **Prompt & Command files affected**:
  - `.gemini/prompts/scan_inbox_workflow.md` & `prompts/scan_inbox_workflow.md` (backlog continuation instructions)
  - `.gemini/commands/scan-inbox.md`, `.claude/commands/scan-inbox.md`, `.agents/skills/scan-inbox/SKILL.md` (explicit queue backlog handling)
- **Data files affected**:
  - `data/inbox_queue.json` (cleaner ingestion without search alert noise)
- **APIs & Dependencies**: No new external dependencies; uses standard library `glob`, `re`, `os`, `argparse`.
