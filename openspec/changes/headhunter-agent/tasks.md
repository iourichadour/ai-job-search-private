## 1. Context and rubric files

- [ ] 1.1 Verify the target compensation band already present in `data/profile.md` ("Target Roles & Industries" section: `$200K-$300K` total comp, confirmed current by the user 2026-09-22) is in a location and format `evidence-verifier` and `deal-architect` can reliably detect; no new field needs to be added — if the format needs adjusting for detection, adjust it in place rather than duplicating a second field
- [ ] 1.2 Verify `data/positioning_rubric.md` (already drafted, tracked 2026-09-22) against `specs/opportunity-positioning/spec.md`: confirm weights (title level 20%, dual-threat 25%, domain 20%, comp signal 15%, technology 20%) sum to exactly 100, each dimension has named High/Medium/Low anchors, and the file's `## Output Schema` (positioning_score, positioning_rationale, resume_bullet_diffs, verdict) matches the spec's required fields field-for-field — no new file needs to be written

## 2. `career-advisor` subagent

- [ ] 2.1 Write `.claude/agents/career-advisor.md` (frontmatter: `name`, `description`, `model: haiku`) that reads `data/job_evaluations.json`, filters to `fit_category` in `{high, medium}`, scores each against `data/positioning_rubric.md`, and drafts a bridging rationale (execution detail → cost/risk/revenue/scale) and 3-5 resume bullet diff proposals; verify by invoking it against 3-5 historical HIGH_FIT records from `data/job_evaluations.json` and confirming output shape matches `specs/opportunity-positioning/spec.md`
- [ ] 2.2 Add the mandatory 2-5 sentence unsoftened verdict to `career-advisor`'s output contract; verify by confirming the verdict in a sample run adds a judgment not already stated in the score/rationale
- [ ] 2.3 Wire `career-advisor` to invoke `evidence-verifier` (task 4.1) on its own draft before presenting it, and to withhold presentation if verification returns BLOCKED; verify by forcing an unmapped claim into a test draft and confirming it is not presented
- [ ] 2.4 Mirror `career-advisor` under `.gemini/` and `.agents/` per this repo's three-parallel-agent-ecosystem convention; verify all three definitions produce equivalent output shape against the same sample job

## 3. `deal-architect` subagent

- [ ] 3.1 Write `.claude/agents/deal-architect.md` (frontmatter: `name`, `description`, `model: sonnet`) implementing the three-lens (hiring manager / peer engineer / bar raiser) adversarial interview simulation, each producing an independent verdict; verify by running it against one tracked opportunity's job description and confirming three distinct, potentially-disagreeing verdicts are present
- [ ] 3.2 Ensure every simulated question includes a named follow-up that exposes a gap in the candidate's draft answer; verify by confirming each question's output includes a "where this answer is exposed" line naming a specific unanswered follow-up
- [ ] 3.3 Ensure minimum topic coverage (90-day roadmap, budget/resource ownership, operational scaling) across the generated questions; verify by checking a sample run covers all three topics
- [ ] 3.4 Implement the OFFER/FINAL_ROUND status gate on negotiation prep, reading status from `job_search_tracker.csv`; verify by confirming no compensation range is produced for an opportunity at `APPLIED` or `INTERVIEWING` status
- [ ] 3.5 Implement the target-compensation-band precondition: if `data/profile.md` has no compensation band set, `deal-architect` reports that a band must be supplied and does not produce a range; verify against a scratch copy of `data/profile.md` with the compensation band line removed (the live file now has a real value per task 1.1, so the negative case must be tested against a copy, not the live file) and confirm it blocks rather than inventing a number
- [ ] 3.6 Wire `deal-architect` to invoke `evidence-verifier` (task 4.1) on drafted interview answers and negotiation talking points before presenting them; verify same as 2.3
- [ ] 3.7 Mirror `deal-architect` under `.gemini/` and `.agents/`; verify as in 2.4

## 4. `evidence-verifier` subagent

- [ ] 4.1 Write `.claude/agents/evidence-verifier.md` (frontmatter: `name`, `description`, `model: sonnet`) that takes a drafted text block, decomposes it into atomic factual claims (technologies, metrics, scope, ownership), checks each against `data/profile.md`, and returns PASS or BLOCKED with the specific unmapped claim(s) named; verify by running it against one known-good draft (expect PASS) and one draft with a deliberately fabricated claim (expect BLOCKED naming that claim)
- [ ] 4.2 Confirm `evidence-verifier` cannot be argued into clearing a block by re-assertion alone (per `specs/evidence-verification/spec.md`); verify by re-running 4.1's BLOCKED case with an added instruction asserting the claim is true, and confirming the block persists
- [ ] 4.3 Mirror `evidence-verifier` under `.gemini/` and `.agents/`; verify as in 2.4

## 5. Validation

- [ ] 5.1 Run `openspec validate --strict` against this change and fix any reported issues
- [ ] 5.2 Dry-run `career-advisor` against 3-5 historical HIGH_FIT/FIT records and review output for accuracy and adherence to `specs/opportunity-positioning/spec.md`
- [ ] 5.3 Dry-run `deal-architect` against one real tracked opportunity (any status) to confirm the OFFER/FINAL_ROUND gate behaves correctly at that opportunity's actual status
- [ ] 5.4 Confirm no artifact from any of the three subagents is sent, submitted, or written to a resume/outreach file without explicit human review, consistent with existing human-in-the-loop conventions

## 6. Archive

- [ ] 6.1 Update `MEMORY.md` with the positioning-rubric/evidence-verification conventions introduced by this change
- [ ] 6.2 `openspec archive headhunter-agent -y` once specs are implemented and validated
