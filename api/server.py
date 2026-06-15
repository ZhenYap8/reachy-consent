"""FastAPI service for consent sessions and clinician dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from engine import ConsentEngine, load_consent_pack

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "consent_packs" / "lap_chole.yaml"
SESSIONS_DIR = ROOT / "sessions"

app = FastAPI(title="Reachy Consent API", version="0.1.0")
_engines: dict[str, ConsentEngine] = {}


class StartSessionResponse(BaseModel):
    session_id: str
    events: list[dict[str, Any]]


class InputRequest(BaseModel):
    text: str


class InputResponse(BaseModel):
    events: list[dict[str, Any]]
    session: dict[str, Any]
    done: bool


def _event_dict(event: Any) -> dict[str, Any]:
    return {
        "phase": event.phase.name,
        "text": event.text,
        "section_id": event.section.id if event.section else None,
    }


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Reachy Consent Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 840px; margin: 2rem auto; padding: 0 1rem; }
    button { margin-right: 0.5rem; }
    pre { background: #f4f4f5; padding: 1rem; overflow: auto; }
    .robot { background: #eef6ff; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .patient { background: #f0fdf4; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; }
  </style>
</head>
<body>
  <h1>Reachy Consent Dashboard</h1>
  <p>Phase 1 demo — keyboard-driven consent session.</p>
  <button onclick="startSession()">Start session</button>
  <div id="log"></div>
  <hr/>
  <input id="patient" placeholder="Patient response..." style="width:70%"/>
  <button onclick="sendInput()">Send</button>
  <button onclick="advance()">Advance (/next)</button>
  <h2>Session JSON</h2>
  <pre id="session">No session yet.</pre>
  <script>
    let sessionId = null;
    function logRobot(text, phase) {
      const el = document.createElement('div');
      el.className = 'robot';
      el.textContent = `[${phase}] ${text}`;
      document.getElementById('log').appendChild(el);
    }
    function logPatient(text) {
      const el = document.createElement('div');
      el.className = 'patient';
      el.textContent = `[PATIENT] ${text}`;
      document.getElementById('log').appendChild(el);
    }
    async function startSession() {
      document.getElementById('log').innerHTML = '';
      const res = await fetch('/sessions/start', { method: 'POST' });
      const data = await res.json();
      sessionId = data.session_id;
      data.events.forEach(e => logRobot(e.text, e.phase));
      await refreshSession();
    }
    async function sendInput() {
      const text = document.getElementById('patient').value;
      if (!sessionId || !text) return;
      logPatient(text);
      document.getElementById('patient').value = '';
      const res = await fetch(`/sessions/${sessionId}/input`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      data.events.forEach(e => logRobot(e.text, e.phase));
      document.getElementById('session').textContent = JSON.stringify(data.session, null, 2);
    }
    async function advance() {
      if (!sessionId) return;
      const res = await fetch(`/sessions/${sessionId}/advance`, { method: 'POST' });
      const data = await res.json();
      data.events.forEach(e => logRobot(e.text, e.phase));
      document.getElementById('session').textContent = JSON.stringify(data.session, null, 2);
    }
    async function refreshSession() {
      if (!sessionId) return;
      const res = await fetch(`/sessions/${sessionId}`);
      const data = await res.json();
      document.getElementById('session').textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>"""


@app.post("/sessions/start", response_model=StartSessionResponse)
def start_session() -> StartSessionResponse:
    pack = load_consent_pack(DEFAULT_PACK)
    engine = ConsentEngine(pack)
    session_id = engine.session.started_at
    _engines[session_id] = engine
    events = engine.start()
    return StartSessionResponse(
        session_id=session_id,
        events=[_event_dict(e) for e in events],
    )


@app.post("/sessions/{session_id}/input", response_model=InputResponse)
def post_input(session_id: str, body: InputRequest) -> InputResponse:
    engine = _engines.get(session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")
    events = engine.handle_input(body.text)
    done = engine.phase.name in ("COMPLETE", "ESCALATED")
    if done:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        out = SESSIONS_DIR / f"{session_id}.json"
        out.write_text(json.dumps(engine.session.to_dict(), indent=2), encoding="utf-8")
    return InputResponse(
        events=[_event_dict(e) for e in events],
        session=engine.session.to_dict(),
        done=done,
    )


@app.post("/sessions/{session_id}/advance", response_model=InputResponse)
def advance(session_id: str) -> InputResponse:
    engine = _engines.get(session_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Session not found")
    events = engine.advance()
    done = engine.phase.name in ("COMPLETE", "ESCALATED")
    return InputResponse(
        events=[_event_dict(e) for e in events],
        session=engine.session.to_dict(),
        done=done,
    )


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    engine = _engines.get(session_id)
    if engine is None:
        path = SESSIONS_DIR / f"{session_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        raise HTTPException(status_code=404, detail="Session not found")
    return engine.session.to_dict()
