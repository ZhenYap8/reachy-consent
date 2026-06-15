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

## MuJoCo simulation

Terminal 1:

```bash
# macOS may require:
mjpython -m reachy_mini.daemon.app.main --sim
# or:
uv run reachy-mini-daemon --sim
```

Terminal 2 — smoke test:

```bash
uv run python -c "from reachy_mini import ReachyMini; 
with ReachyMini(media_backend='no_media') as m: print('Connected')"
```

Use `media_backend='no_media'` in sim when you don't need camera/audio — it connects faster and avoids GStreamer warnings on macOS.

## Robot app (Phase 2)

Scaffolded at `robot_app/consent_assistant/` using the conversation template.
Customize `profiles/_consent_assistant_locked_profile/instructions.txt` for consent-only behavior.

## Reference repos (cloned alongside)

| Path | Purpose |
|------|---------|
| `../reachy_mini/` | Official SDK, examples, MuJoCo |
| `../_reference/Robotic-medical-AI-assistant/` | Local voice pipeline reference |

## Status

- [x] Project scaffold + dependencies
- [x] Lap chole consent pack
- [x] State machine + CLI + dashboard
- [ ] MuJoCo motion cues (nod on confirm)
- [ ] Voice pipeline integration
- [ ] RAG Q&A from consent document

See `plan.md` for the full roadmap.
