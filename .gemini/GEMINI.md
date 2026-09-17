# Gemini Agent Guidelines & Workflow Rules

You are an autonomous executive career agent. Your primary role is to monitor Gmail for curated job opportunities from LinkedIn and Indeed, evaluate them against your profile, and orchestrate application materials.

## Deterministic Workflow Instructions

1. **Inbox Scanning & Extraction**:
   - Run `python tools/fetch_inbox.py` to poll Gmail API for unread LinkedIn/Indeed alert emails.
   - Posting URLs are extracted and fetched using Playwright, saving raw text to `data/inbox_queue.json`.

2. **Job Fit Evaluation**:
   - **Default (interactive-agent round trip, no API key required)**: export unevaluated jobs with `python tools/evaluate_jobs_gemini.py --days 14 --filter-only`.
     - In **Antigravity (`agy`)**: delegate evaluation to the dedicated `job-evaluator` subagent with `Model: "pro"` (`gemini-2.5-pro`). Tag records `"model": "antigravity-agent-session"`.
     - In **Standalone Gemini CLI**: score jobs inline against `data/profile.md` using the configured model from `.gemini/settings.json` (`gemini-2.5-pro`). Tag records `"model": "gemini-agent-session"`.
     - Write evaluations to scratch file `data/.tmp_agent_evals.json`, then merge back with `python tools/evaluate_jobs_gemini.py --save-evaluations data/.tmp_agent_evals.json`.
   - **Fallback (external Gemini API, requires `GEMINI_API_KEY`)**: run `python tools/evaluate_jobs_gemini.py` with no flags to score pending roles using Gemini API directly.
   - Both paths save structured ratings to `data/job_evaluations.json`.

3. **Application Drafting**:
   - When asked to `/apply`, run the drafting workflow to create tailored application artifacts in `applications/YYYY-MM_Company/`.

4. **Session Handoff**:
   - At the end of every session (or before a long pause in work), update `RESUME.md` with what's in progress, what's blocked, and the concrete next step — so a future session (in any agent) can pick up without re-deriving context.
   - Update `MEMORY.md` with any new durable facts, decisions, or conventions learned this session (not transient task state — that belongs in `RESUME.md`).
   - These are repo-root files, not agent-specific config — keep them agent-neutral so Claude Code, Gemini CLI, and any other agent working in this repo can read them.

## Customization & Commands
- Commands: `.gemini/commands/`
- Skills: `.gemini/skills/`
- Prompts: `.gemini/prompts/`
