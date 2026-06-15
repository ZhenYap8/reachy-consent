# Phase 3 — RAG Q&A

**Goal:** Answer patient questions from surgeon-approved consent documents; escalate off-script questions.

**Status:** Planned — no implementation files yet.

## Files to add (Phase 3)

| Path | Role |
|------|------|
| `engine/rag/` (planned) | Chunking, embedding, retrieval |
| `consent_packs/*/sources/` (planned) | Source PDFs / markdown per procedure |
| `engine/guardrails.py` (planned) | No invented risks; escalation rules |
| `tests/test_rag.py` (planned) | Retrieval + guardrail tests |

## Depends on

- Phase 1 state machine (`engine/`) for session flow and escalation
- Phase 2 voice (optional) for spoken Q&A

## Phase 3 checklist

- [ ] Embed consent document chunks
- [ ] Guardrailed answers (no invented risks)
- [ ] Escalation to clinician on off-script questions
