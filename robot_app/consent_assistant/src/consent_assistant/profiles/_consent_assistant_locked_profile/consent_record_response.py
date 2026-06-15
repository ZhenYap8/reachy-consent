"""Record patient responses into the consent state machine."""

from __future__ import annotations

import logging
from typing import Any

from consent_assistant.consent_session import get_voice_bridge
from consent_assistant.tools.core_tools import Tool, ToolDependencies

logger = logging.getLogger(__name__)


class ConsentRecordResponse(Tool):
    name = "consent_record_response"
    description = (
        "Submit the patient's spoken response to the consent state machine. "
        "Returns the robot lines to speak next."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "transcript": {
                "type": "string",
                "description": "What the patient said, transcribed verbatim.",
            },
        },
        "required": ["transcript"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        transcript = str(kwargs.get("transcript", "")).strip()
        bridge = get_voice_bridge()
        logger.info("consent_record_response: %r", transcript)

        if bridge.waits_for_patient:
            events = bridge.handle_patient_transcript(transcript)
        else:
            events = bridge.events_after_robot_spoke()

        return {
            "events": [
                {"phase": event.phase.name, "text": event.text}
                for event in events
            ],
            "phase": bridge.engine.phase.name,
            "finished": bridge.is_finished,
            "escalated": bridge.session.escalated,
        }
