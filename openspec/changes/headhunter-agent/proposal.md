## Why

The existing job-evaluation pipeline (`job-evaluation` capability) answers "is this job a fit" but stops there — it produces no positioning rationale for HIGH_FIT/FIT jobs, no interview preparation, and no negotiation support once an opportunity reaches OFFER/FINAL_ROUND. A separately-reviewed CrewAI-based proposal (`build-executive-headhunter-agent`, not adopted) proposed closing this gap but assumed a framework dependency (CrewAI) and file/module names that don't exist in this repo, and included unverified capability claims (Copilot Studio, "Hermes", "OpenClaw") not backed by `data/profile.md`. This change replaces that proposal with a Claude-Code-native design, reusing the existing subagent pattern already proven by `job-evaluator.md`, and reuses concrete prompt/output patterns found in two open-source Claude Code career-agent projects (JobFinderOS's `coach.md`, career-agent's `interview-panel.md` and `fact-checker.md`) instead of designing from scratch.

## What Changes

- **New**: `career-advisor` subagent (`.claude/agents/career-advisor.md`, mirrored under `.gemini/` and `.agents/` per this repo's three-parallel-agent-ecosystem convention) — scores HIGH_FIT/FIT jobs from `data/job_evaluations.json` against a second, positioning-specific weighted rubric (role/title level, dual-threat fit, domain fit, comp signal, technology fit), and drafts a positioning rationale plus resume bullet diff requests.
- **New**: `deal-architect` subagent — for opportunities at `OFFER`/`FINAL_ROUND` status in `job_search_tracker.csv`, runs a three-lens adversarial interview simulation (hiring manager / peer engineer / bar raiser) and produces compensation negotiation talking points.
- **New**: an evidence-verification gate — every factual claim in text either subagent drafts (positioning rationale, resume bullet, interview answer) must trace to something literally present in `data/profile.md`; unmapped claims are blocked, not warned, consistent with this repo's existing `CLAUDE.md` rule against hallucinating skills.
- **Explicitly excluded**: CrewAI or any other multi-agent framework dependency; any LinkedIn/job-board scraping (the crawler/market-intel roles from the reviewed prior art are not being ported — ingestion stays Gmail-alert-only); the Copilot Studio / "Hermes" / "OpenClaw" capability claims from the earlier reviewed proposal; any auto-send/auto-apply behavior (human-in-the-loop only).
- **Resolved input**: target compensation band is defined in `data/profile.md` ("Target Roles & Industries" section: `$200K-$300K` total comp), confirmed current by the user on 2026-09-22. The negotiation-prep requirement's precondition is satisfied — `tasks.md` task 1.1 now verifies the existing value rather than sourcing a new one.

## Capabilities

### New Capabilities
- `opportunity-positioning`: Scores HIGH_FIT/FIT jobs against a positioning-specific rubric distinct from the existing fit-evaluation rubric, and drafts a positioning rationale plus resume bullet diff requests bridging one hands-on execution detail to a C-suite outcome.
- `interview-negotiation-prep`: Three-lens adversarial interview simulation and compensation negotiation talking points for opportunities at OFFER/FINAL_ROUND status.
- `evidence-verification`: Blocks any drafted claim (positioning rationale, resume bullet, interview answer) that does not trace to `data/profile.md`.

### Modified Capabilities
<!-- No existing capabilities are being modified. This change is additive: it reads data/job_evaluations.json and job_search_tracker.csv but does not change the job-evaluation capability's scoring rubric, schema, or persistence rules. -->

## Impact

- **Affected code**: New files only — `.claude/agents/career-advisor.md`, `.claude/agents/deal-architect.md` (mirrored under `.gemini/` and `.agents/`), plus their supporting rubric/context markdown files. No existing tool (`tools/fetch_inbox.py`, `tools/evaluate_jobs_gemini.py`) is modified.
- **Data**: Reads `data/job_evaluations.json`, `job_search_tracker.csv`, and `data/profile.md` (read-only for all three). Additive columns may be needed on `job_search_tracker.csv` for positioning score/status — to be confirmed in design.md.
- **Dependencies**: None added. No CrewAI, no new Python packages.
- **Jira**: Tracked as SCRUM-16, depends on SCRUM-15 (profile update, done). Not blocked by SCRUM-12 (re-evaluate ~995-job backlog): `opportunity-positioning` only needs some already-evaluated HIGH_FIT/FIT jobs to build and test against, and 423+ already exist in `data/job_evaluations.json`. SCRUM-12 keeps the full backlog current for the eval-dashboard (SCRUM-13) but is not a functional prerequisite for this capability.
