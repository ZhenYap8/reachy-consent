# Reachy Consent

Surgical **informed consent assistant** for [Reachy Mini](https://github.com/pollen-robotics/reachy_mini).

The robot walks patients through surgeon-approved consent sections, confirms understanding,
and exports an audit-ready session log. It educates — it does not replace clinician
discussion or legal signature.

## Workspace layout

This project lives alongside the official SDK:

```
~/Documents/Github/reachy/
├── reachy_mini/       # upstream SDK (separate git repo)
├── reachy-consent/    # this project
└── _reference/        # optional voice pipeline reference
```

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

```bash
cd ~/Documents/Github/reachy/reachy-consent
uv sync   # or: source .venv/bin/activate after uv add
```

## Phase 1 — Run without hardware

### CLI demo

```bash
uv run python scripts/run_consent_cli.py
```

Type `yes` at prompts, or ask questions. Commands: `/next`, `/quit`.

### Web dashboard

```bash
uv run uvicorn api.server:app --reload --port 8091
```

Open http://127.0.0.1:8091

## Phase 2 — Voice (current)

```bash
cd ~/Documents/Github/reachy/reachy-consent
cp .env.example .env   # add OPENAI_API_KEY
uv sync

# Text-only smoke test (no robot)
uv run python scripts/run_consent_voice.py --no-robot

# With MuJoCo sim — terminal 1:
uv run mjpython -m reachy_mini.daemon.app.main --sim

# Terminal 2 — spoken consent walkthrough:
uv run python scripts/run_consent_voice.py

# Or OpenAI Realtime robot app (Gradio UI in sim):
cd robot_app/consent_assistant
export REACHY_MINI_CUSTOM_PROFILE=_consent_assistant_locked_profile
export CONSENT_PACK_PATH=../../consent_packs/lap_chole.yaml
uv run consent-assistant --gradio
```

## Robot app (Phase 2)

Scaffolded at `robot_app/consent_assistant/` using the conversation template.
Customize `profiles/_consent_assistant_locked_profile/instructions.txt` for consent-only behavior.

## Reference repos (cloned alongside)

| Path | Purpose |
|------|---------|
| `../reachy_mini/` | Official SDK, examples, MuJoCo |
| `../_reference/Robotic-medical-AI-assistant/` | Local voice pipeline reference |

## Phase history

All phases are tracked in one repo. See [`docs/phases/`](docs/phases/README.md) for which files belong to Phase 1, 2, and 3.

## Status

- [x] Project scaffold + dependencies
- [x] Lap chole consent pack
- [x] State machine + CLI + dashboard
- [x] MuJoCo daemon connection verified
- [ ] MuJoCo motion cues (nod on confirm) — partial via voice runner
- [x] Voice pipeline (`scripts/run_consent_voice.py`)
- [x] Consent-specific robot app prompts + tools
- [ ] Full bridge testing on sim hardware audio
- [ ] RAG Q&A from consent document

See `plan.md` for the full roadmap.
