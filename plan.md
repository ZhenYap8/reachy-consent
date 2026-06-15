# Reachy Consent — Project Plan

## Goal

Build a **surgical informed consent assistant** on Reachy Mini that walks patients through
surgeon-approved consent sections, confirms understanding, answers bounded questions, and
produces an audit-ready session log.

The robot **educates and documents** — it does not replace clinician discussion or legal signature.

## User decisions (fill in as we go)

- **First procedure:** Laparoscopic cholecystectomy (`consent_packs/lap_chole.yaml`)
- **Hardware path:** MuJoCo sim first → Reachy Mini Lite/Wireless later
- **Inference:** Phase 1 keyboard/CLI; Phase 2 voice (local STT/TTS)
- **Robot app:** `robot_app/consent_assistant` (conversation template)

## Architecture

```
consent_packs/*.yaml  →  engine/state_machine.py  →  FastAPI dashboard
                              ↓
                    robot_app/consent_assistant (voice + motion, later)
                              ↓
                    reachy-mini-daemon (--sim or hardware)
```

## Phase file history

Each phase’s files are documented in [`docs/phases/`](docs/phases/README.md). All phases live in **one repo** — git tracks changes; manifests record which paths belong to which phase.

## Phases

### Phase 1 — Sim + state machine (current)
- [x] Clone SDK + create project
- [x] Install `reachy_mini[mujoco]`
- [x] Scaffold conversation robot app
- [x] Consent YAML pack + state machine
- [x] CLI demo + session export
- [x] Verify MuJoCo daemon connection
- [ ] Wire motion cues (nod on confirm)

### Phase 2 — Voice (current)
- [x] `engine/voice_bridge.py` — state machine ↔ voice sessions
- [x] `engine/voice_cues.py` — listening / thinking / speaking / nod
- [x] `scripts/run_consent_voice.py` — OpenAI TTS + Whisper + Reachy audio
- [x] Consent-specific `instructions.txt` and consent tools for robot app
- [x] Head motion hooks in OpenAI Realtime handler
- [ ] End-to-end sim test with live audio
- [ ] Adapt local STT/TTS from reference repo (optional)

### Phase 3 — RAG Q&A
- [ ] Embed consent document chunks
- [ ] Guardrailed answers (no invented risks)
- [ ] Escalation to clinician on off-script questions

## Open questions

1. Target deployment: research lab, hospital pilot, or personal demo?
2. Do you have Reachy Mini hardware yet (Lite vs Wireless)?
3. Local GPU available for voice stack, or start with cloud APIs in dev?
