# SCRUM-12 / SCRUM-16 Funnel

Cheap, wide triage (SCRUM-12) feeds expensive, narrow depth (SCRUM-16) — they answer different questions and don't duplicate each other. See `design.md` for the full rationale.

```mermaid
flowchart TD
    A[Gmail LinkedIn/Indeed alerts] --> B["data/inbox_queue.json<br/>(pending jobs)"]

    subgraph S12["SCRUM-12 — cheap, wide triage (haiku, whole backlog)"]
        B --> C["job-evaluation capability<br/>skill_match / experience_level_match /<br/>company_fit / growth_potential / red_flags"]
        C --> D["data/job_evaluations.json<br/>overall_fit + fit_category"]
    end

    D -->|fit_category = low/skip| X[Logged, no further action]
    D -->|fit_category = high/medium| E{HIGH_FIT / FIT}

    subgraph S16["SCRUM-16 — expensive, narrow depth (only shortlisted jobs)"]
        E --> F["career-advisor (haiku)<br/>positioning rubric: title level / dual-threat /<br/>domain fit / comp signal / tech fit"]
        F --> G["positioning rationale +<br/>resume bullet diffs + verdict"]
        G --> V1{{"evidence-verifier (sonnet)<br/>PASS / BLOCKED vs data/profile.md"}}
        V1 -->|BLOCKED| G

        H["job_search_tracker.csv<br/>status = OFFER / FINAL_ROUND"] --> I["deal-architect (sonnet)<br/>3-lens interview sim +<br/>negotiation prep ($200K-$300K band)"]
        I --> V2{{"evidence-verifier (sonnet)<br/>PASS / BLOCKED vs data/profile.md"}}
        V2 -->|BLOCKED| I
    end

    V1 -->|PASS| J[Human review & approval]
    V2 -->|PASS| J
    D -.->|browse/filter, presentation only| K["SCRUM-13 eval-dashboard"]

    style S12 fill:#1e3a5f,color:#fff
    style S16 fill:#4a2f5f,color:#fff
    style X fill:#3a3a3a,color:#fff
```

The two `{{ }}` diamonds are the `evidence-verifier` gate (`specs/evidence-verification/spec.md`) — a third, independent subagent that checks every claim in a draft against `data/profile.md` before either `career-advisor` or `deal-architect`'s output reaches you.
