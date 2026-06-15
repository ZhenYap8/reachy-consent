# Phase 2 — Voice

**Goal:** Spoken consent flow via Reachy Mini (sim or hardware); listening / speaking / thinking head states.

**Status:** Implemented — primary entry point is `scripts/run_consent_voice.py`.

## Files (Phase 2)

| Path | Role |
|------|------|
| `engine/voice_bridge.py` | Connects `ConsentEngine` to voice sessions |
| `engine/voice_cues.py` | Head/antenna poses: ready, listening, thinking, speaking, nod |
| `scripts/run_consent_voice.py` | OpenAI TTS + Whisper loop through Reachy media |
| `tests/test_voice_bridge.py` | Bridge unit tests |
| `.env.example` | `OPENAI_API_KEY`, `CONSENT_PACK_PATH` |
| `robot_app/.../instructions.txt` | Consent-only Realtime prompt |
| `robot_app/.../consent_status.py` | Tool: session phase + context |
| `robot_app/.../consent_record_response.py` | Tool: submit patient transcript |
| `robot_app/.../consent_session.py` | Loads `VoiceConsentBridge` for tools |
| `robot_app/.../consent_motion.py` | Motion cues for Realtime app |

## Run

```bash
# Prerequisites
cp .env.example .env   # set OPENAI_API_KEY
uv sync

# Text-only (no robot)
uv run python scripts/run_consent_voice.py --no-robot

# With sim — terminal 1
uv run mjpython -m reachy_mini.daemon.app.main --sim

# Terminal 2 — spoken walkthrough
uv run python scripts/run_consent_voice.py
```

## Phase 2 checklist

- [x] Voice bridge (`engine/voice_bridge.py`)
- [x] Consent-specific instructions + tools
- [x] Listening / speaking / thinking head states
- [x] OpenAI TTS/STT voice runner
- [ ] Live sim audio end-to-end verification
- [ ] Local STT/TTS from reference repo (future)
