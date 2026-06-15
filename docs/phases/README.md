# Phase history (file map)

This repo keeps **all phases in one tree**. Git history tracks how files change over time; this folder documents **which files belong to which phase** so nothing gets lost when later phases add code.

| Phase | Status | Manifest |
|-------|--------|----------|
| [Phase 1 — Sim + state machine](phase-1.md) | In progress | CLI, dashboard, consent engine, robot app scaffold |
| [Phase 2 — Voice](phase-2.md) | Planned | OpenAI Realtime app, audio/head motion |
| [Phase 3 — RAG Q&A](phase-3.md) | Planned | Document retrieval, guardrailed answers |

## How we preserve history

1. **Do not delete Phase 1 files** when Phase 2 lands — extend or wire new modules instead.
2. **Update the phase manifest** when you add or move files (`docs/phases/phase-N.md`).
3. **Tag milestones** on GitHub, e.g. `git tag phase-1` after Phase 1 is complete.
4. **Session exports** stay local (`sessions/`, gitignored) — not committed.

## Repo layout (all phases)

```
reachy-consent/
├── consent_packs/          # Procedure content (all phases)
├── engine/                 # Phase 1 state machine
├── api/                    # Phase 1 web dashboard
├── scripts/                # Phase 1 CLI demo
├── robot_app/              # Phase 2 voice + motion (scaffolded in Phase 1)
├── tests/                  # Phase 1 unit tests (+ later phases)
├── docs/phases/            # This folder — phase file map
└── plan.md                 # Roadmap checklist
```

See also [`plan.md`](../../plan.md) for the living roadmap.
