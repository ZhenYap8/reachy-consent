# Phase 1 — Sim + state machine

**Goal:** Walk through consent sections without hardware; export session logs.

**Status:** Mostly complete (MuJoCo connection verified locally; motion cues still TODO).

## Files (Phase 1)

| Path | Role |
|------|------|
| `consent_packs/lap_chole.yaml` | First procedure pack (lap cholecystectomy) |
| `engine/` | Consent state machine, models, YAML loader |
| `api/server.py` | Web dashboard (keyboard-driven, text only) |
| `scripts/run_consent_cli.py` | Interactive CLI demo |
| `tests/test_state_machine.py` | State machine tests |
| `main.py` | Package entry stub |
| `pyproject.toml`, `uv.lock` | Dependencies (`reachy-mini[mujoco]`) |
| `plan.md` | Roadmap |
| `README.md` | Setup and run instructions |

## Scaffolded for later phases (kept in tree from Phase 1)

| Path | Used in |
|------|---------|
| `robot_app/consent_assistant/` | Phase 2 voice + motion |

## Run (Phase 1)

```bash
cd reachy-consent
uv sync

# CLI (no robot)
uv run python scripts/run_consent_cli.py

# Web dashboard
uv run uvicorn api.server:app --reload --port 8091

# MuJoCo sim (separate terminal, macOS)
uv run mjpython -m reachy_mini.daemon.app.main --sim
```

## Not committed (by design)

| Path | Reason |
|------|--------|
| `sessions/` | Exported session JSON from demos |
| `.venv/` | Local virtual environment |

## Phase 1 checklist

- [x] Consent YAML pack + state machine
- [x] CLI demo + session export
- [x] Web dashboard
- [x] Robot app scaffold (`robot_app/consent_assistant/`)
- [x] MuJoCo daemon connection verified
- [ ] Motion cues (nod on confirm)
