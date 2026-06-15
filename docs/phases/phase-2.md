# Phase 2 — Voice

**Goal:** Spoken consent flow via Reachy Mini (sim or hardware); listening / speaking / thinking head states.

**Status:** Planned — scaffold exists from Phase 1; wiring and consent-specific prompts TODO.

## Files (Phase 2 — existing scaffold)

| Path | Role |
|------|------|
| `robot_app/consent_assistant/src/consent_assistant/main.py` | App entrypoint |
| `robot_app/consent_assistant/src/consent_assistant/openai_realtime.py` | OpenAI Realtime voice session |
| `robot_app/consent_assistant/src/consent_assistant/console.py` | Mic/speaker ↔ robot media |
| `robot_app/consent_assistant/src/consent_assistant/audio/` | Head wobble from speech |
| `robot_app/consent_assistant/src/consent_assistant/moves.py` | Movement manager |
| `robot_app/consent_assistant/src/consent_assistant/profiles/_consent_assistant_locked_profile/` | Consent prompts + tools |
| `robot_app/consent_assistant/.env.example` | API key template |
| `robot_app/consent_assistant/tests/` | Voice/audio tests |

## Files to add (Phase 2)

| Path | Role |
|------|------|
| `engine/voice_bridge.py` (planned) | Connect state machine ↔ robot app |
| Consent-specific `instructions.txt` edits | Lock behavior to consent-only |
| Reference: `../_reference/Robotic-medical-AI-assistant/` | Local voice pipeline example (separate clone) |

## Run (Phase 2 — when wired)

```bash
# Terminal 1: sim or hardware daemon
uv run mjpython -m reachy_mini.daemon.app.main --sim

# Terminal 2: voice app (requires OPENAI_API_KEY)
cd robot_app/consent_assistant
# follow robot_app/consent_assistant/README.md
```

## Phase 2 checklist

- [ ] Adapt voice pipeline from reference repo
- [ ] Customize `instructions.txt` for consent-only behavior
- [ ] Listening / speaking / thinking head states
- [ ] Bridge Phase 1 state machine to voice app
