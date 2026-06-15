"""Bridge the deterministic consent engine to voice-driven sessions."""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.models import ConsentPack, ConsentSession
from engine.state_machine import ConsentEngine, EngineEvent, EnginePhase


@dataclass
class VoiceConsentBridge:
    """Orchestrate :class:`ConsentEngine` for spoken consent walkthroughs."""

    pack: ConsentPack
    engine: ConsentEngine = field(init=False)

    def __post_init__(self) -> None:
        self.engine = ConsentEngine(self.pack)

    @property
    def session(self) -> ConsentSession:
        return self.engine.session

    @property
    def is_finished(self) -> bool:
        return self.engine.phase in (EnginePhase.COMPLETE, EnginePhase.ESCALATED)

    @property
    def waits_for_patient(self) -> bool:
        return self.engine.phase in (EnginePhase.AWAIT_CONFIRM, EnginePhase.QA)

    def start(self) -> list[EngineEvent]:
        return self.engine.start()

    def events_after_robot_spoke(self) -> list[EngineEvent]:
        """Advance scripted phases after the robot finishes speaking."""
        phase = self.engine.phase
        if phase in (EnginePhase.DISCLAIMER, EnginePhase.SECTION_SCRIPT):
            return self.engine.advance()
        return []

    def handle_patient_transcript(self, text: str) -> list[EngineEvent]:
        return self.engine.handle_input(text)

    def llm_context(self) -> str:
        """Dynamic context for OpenAI Realtime when co-piloting the flow."""
        section = self.engine.current_section
        section_line = (
            f"Current section: {section.id} ({section.type.value})."
            if section
            else "No active section."
        )
        return (
            f"Procedure: {self.pack.title} ({self.pack.id}).\n"
            f"Engine phase: {self.engine.phase.name}.\n"
            f"{section_line}\n"
            "Follow surgeon-approved consent content only. "
            "Do not invent risks, benefits, or alternatives. "
            "Escalate to a clinician when the patient declines or remains confused."
        )
