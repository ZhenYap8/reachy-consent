"""Return current consent session status."""

from __future__ import annotations

import logging
from typing import Any

from consent_assistant.consent_session import get_voice_bridge
from consent_assistant.tools.core_tools import Tool, ToolDependencies

logger = logging.getLogger(__name__)


class ConsentStatus(Tool):
    name = "consent_status"
    description = (
        "Get the current consent session phase, procedure title, and context "
        "for the active consent section."
    )
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        bridge = get_voice_bridge()
        section = bridge.engine.current_section
        return {
            "procedure": bridge.pack.title,
            "phase": bridge.engine.phase.name,
            "section_id": section.id if section else None,
            "context": bridge.llm_context(),
            "finished": bridge.is_finished,
            "waits_for_patient": bridge.waits_for_patient,
        }
