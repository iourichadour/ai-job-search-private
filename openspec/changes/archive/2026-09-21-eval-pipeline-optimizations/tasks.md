## 1. Ingestion Filtering (Upstream Digest Exclusion)

- [x] 1.1 Add search alert digest regex matching (`^\d+[\d,]*\+\s+.*Jobs`) and search-endpoint URL exclusion (`/jobs/search`) to `tools/fetch_inbox.py`
- [x] 1.2 Add counter and logging for dropped search digests in `tools/fetch_inbox.py` and verify behavior against representative email subjects

## 2. Validation & Score Auto-Clamping

- [x] 2.1 Implement automatic clamping of dimension scores and `overall_fit` to `[0, 100]` in `validate_evaluation_record()` in `tools/evaluate_jobs_gemini.py`
- [x] 2.2 Ensure `fit_category` defaults to `skip` when `overall_fit` clamps to `0`
- [x] 2.3 Verify validation accepts `antigravity-agent-session` and cleanly clamps negative scores (e.g., `-10` → `0`) without validation errors or failed entries

## 3. Batch Preparation CLI Orchestration

- [x] 3.1 Implement `--prepare-batches` CLI flag in `tools/evaluate_jobs_gemini.py` accepting `--batch-size` (default 60) and `--days`
- [x] 3.2 Implement batch partitioning logic that writes `data/eval_batches/batch_XX.json` and prints copy-pasteable subagent invocation prompts
- [x] 3.3 Verify `--prepare-batches` dry run on `data/inbox_queue.json`, confirming batch file generation and JSON schema compliance

## 4. Multi-File Glob Persistence & Subagent File Output

- [x] 4.1 Update `--save-evaluations` in `tools/evaluate_jobs_gemini.py` to resolve file globs (e.g. `"data/eval_batches/*.evaluated.json"`) and directories into a consolidated list of evaluations
- [x] 4.2 Update `.agents/agents/job-evaluator.agent.md` and `.claude/agents/job-evaluator.md` instructions to mandate direct output writing via `write_to_file` to `data/eval_batches/batch_XX.evaluated.json`
- [x] 4.3 Verify multi-file `--save-evaluations` with mock batch output files to ensure deduplication, queue status updating, and failure reporting function as expected

## 5. Queue Backlog Continuation & Workflow Prompt Updates

- [x] 5.1 Remove the silent 14-day default in `tools/evaluate_jobs_gemini.py` when `--filter-only` or `--prepare-batches` is called without `--days`, defaulting to all pending unevaluated jobs in the queue
- [x] 5.2 Update `.gemini/prompts/scan_inbox_workflow.md` and `prompts/scan_inbox_workflow.md` to document backlog continuation instructions when fetch is bypassed
- [x] 5.3 Update `.gemini/commands/scan-inbox.md`, `.claude/commands/scan-inbox.md`, and `.agents/skills/scan-inbox/SKILL.md` to clarify queue continuation behavior
- [x] 5.4 Verify that running `python tools/evaluate_jobs_gemini.py --filter-only` without `--days` exports all pending queue jobs without date cutoff
