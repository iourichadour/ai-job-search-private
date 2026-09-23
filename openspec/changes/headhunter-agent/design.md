## Context

This repo already has one working example of the pattern this change extends: `.claude/agents/job-evaluator.md`, a Claude Code subagent pinned to a specific model, invoked headlessly via the Agent tool, that reads `data/profile.md` and scores jobs against a fixed rubric (documented in `MEMORY.md`). It is mirrored under `.gemini/` and `.agents/` per the repo's three-parallel-agent-ecosystem convention. This change follows that same shape rather than introducing new infrastructure.

Two open-source Claude Code career-agent projects were reviewed for reusable prompt/output design before drafting this change's agents (see proposal.md - Why): `matthewprice/JobFinderOS` (a `coach` persona: recruiter judgment, interview prep, mandatory candid verdict, anti-AI-tell drafting discipline, headless subagent report contract) and `srikar0805/career-agent` (`interview-panel`: three-lens adversarial simulation with per-lens reject triggers; `fact-checker`: evidence-traced PASS/BLOCKED gate; `resume-judge`: fresh-context grading so a model cannot inflate its own prior draft). Both use the identical `name`/`description`/`tools`/`model` frontmatter this repo already uses, so no format translation is needed — only content adaptation.

## Goals / Non-Goals

**Goals:**
- Reuse the existing subagent invocation pattern (Agent tool, headless report contract) rather than adding a new runtime.
- Reuse specific prompt/output structures from the two reviewed projects where they map cleanly, rather than redesigning from a blank page.
- Keep the evidence-verification gate structurally independent from the agents whose output it checks, so it cannot rationalize a hallucinated claim as acceptable.

**Non-Goals:**
- Porting JobFinderOS's `scout`/`mark` crawler and market-intel roles — out of scope per proposal.md, since this repo's ingestion stays Gmail-alert-only.
- Solving the target-compensation-band *input* problem — this design only surfaces the requirement that a band must be present and blocks if it isn't; it does not invent a default. (As of 2026-09-22, `data/profile.md` has one — `$200K-$300K`, confirmed current — but the block-if-absent behavior is a standing requirement independent of that, not conditioned on the input currently existing.)
- Changing anything in the existing `job-evaluation` capability's rubric, schema, or persistence rules.

## Decisions

### Three subagents, not two
The reviewed prior proposal specified two agents (Career Advisor, Deal Architect) with an ad hoc "don't hallucinate" instruction embedded in each. This design instead makes evidence verification a **third, separate subagent** (`evidence-verifier`), modeled on career-agent's `fact-checker.md` and `resume-judge.md`. Rationale: both of those source agents deliberately isolate the grading/checking role from the drafting role specifically so a model cannot grade its own homework leniently — a fresh, independently-invoked subagent checking a draft against `data/profile.md` is a stronger control than an instruction inline in the same prompt that produced the draft. `career-advisor` and `deal-architect` SHALL invoke `evidence-verifier` via the Agent tool on every draft before presenting it, not merge its logic into themselves.

Alternative considered: embed the evidence check as a self-review step inside each drafting agent's own prompt. Rejected — this is exactly the self-grading failure mode `resume-judge.md`'s design note warns about ("an LLM shown its own earlier draft grades the new one relative to the old one... the score climbs whether or not the document got better").

### Two separate rubrics, not one merged rubric
`opportunity-positioning`'s five-dimension rubric (title level, dual-threat fit, domain fit, comp signal, technology fit) is intentionally separate from the existing `job-evaluation` capability's five-dimension fit rubric (`skill_match`, `experience_level_match`, `company_fit`, `growth_potential`, `red_flags`). They answer different questions — "should I apply" versus "how do I position and negotiate this specific one" — and merging them would make the existing rubric's weights (documented in `MEMORY.md`, consumed by `job_search_tracker.csv`'s `fit_rating` column and the `upskill` skill) a moving target. `career-advisor` reads the existing `overall_fit`/`fit_category` as an input gate (only HIGH_FIT/FIT jobs get positioning-scored) but writes its own separate score, never overwriting the original.

### Rubric structure borrows JobFinderOS's format
JobFinderOS's `scoring_rubric.template.md` structure (named weights summing to 100%, per-dimension anchor descriptions at high/medium/low, explicit score-to-action thresholds) is more implementable and auditable than the flat 0-10-average-with-no-anchors structure in the originally reviewed CrewAI proposal. `opportunity-positioning`'s rubric file adopts this structure.

### Model assignment follows existing cost-consciousness precedent
- `career-advisor`: `haiku` — high-volume, lower-stakes scoring pass, consistent with `job-evaluator.md`'s existing model pin.
- `deal-architect`: `sonnet` — higher stakes (interview/negotiation prep the candidate will act on directly).
- `evidence-verifier`: `sonnet` — a false PASS here has real consequences (a candidate defending a claim they can't back up), so it is not the place to economize.

All three run inside the existing Claude Code/Gemini CLI/Antigravity interactive sessions at no marginal API cost, per the existing Pro-plan rationale already documented in `MEMORY.md` — this is the concrete answer to "be cost-conscious": the cost avoided is not agent count, it's avoiding a separate framework that would bill by the token outside the subscription.

### Context files, not code, hold the rubric and persona detail
Following both the existing `job-evaluator.md` pattern and the reviewed projects' `config_files`/context-file convention, the positioning rubric and comp-band input live in plain markdown files the agents read at invocation time (`data/positioning_rubric.md`, and the target compensation band as a new field expected in `data/profile.md`), not hardcoded in the agent prompt. This keeps the rubric user-editable without touching agent definitions, matching this repo's existing `data/profile.md`-as-source-of-truth convention.

## Risks / Trade-offs

- **[Risk]** A third subagent invocation per draft roughly triples the number of Agent-tool calls for a single positioning or interview-prep pass, adding latency. → **Mitigation**: acceptable given low job volume already documented in `MEMORY.md` ("not processing thousands of applications... no need for batch/unattended evaluation infrastructure"); this is an interactive, low-frequency workflow, not a batch job.
- **[Risk]** `evidence-verifier` checking against `data/profile.md`'s prose (rather than a structured evidence-with-IDs bank like career-agent's `evidence.yaml`) may under- or over-match claims if the profile's wording is loose. → **Mitigation**: start with prose matching; if false blocks or false passes turn out to be frequent in practice, a follow-up change can introduce a structured evidence log — not started speculatively here.
- **[Risk, now resolved]** Negotiation prep would have been fully blocked until a target compensation band was supplied. → **Resolution**: `data/profile.md` already has one (`$200K-$300K`, confirmed current 2026-09-22). The underlying precondition-check behavior (block rather than invent a number if the band is ever absent) remains a hard requirement per `specs/interview-negotiation-prep/spec.md`, and task 3.5 still verifies it — against a scratch copy with the band removed, since the live file now has a real value.

## Open Questions

None — the target compensation band already lives in `data/profile.md` ("Target Roles & Industries" section), which resolves the placement question this section previously left open.
