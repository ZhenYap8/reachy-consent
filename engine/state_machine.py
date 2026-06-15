from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto

from engine.models import (
    ConsentPack,
    ConsentSession,
    ConsentSection,
    SectionResult,
    SectionStatus,
    utc_now_iso,
)


class EnginePhase(Enum):
    DISCLAIMER = auto()
    SECTION_SCRIPT = auto()
    AWAIT_CONFIRM = auto()
    QA = auto()
    COMPLETE = auto()
    ESCALATED = auto()


class PatientResponse(Enum):
    CONFIRM = auto()
    QUESTION = auto()
    DECLINE = auto()
    UNSURE = auto()
    EMPTY = auto()


@dataclass
class EngineEvent:
    phase: EnginePhase
    text: str
    section: ConsentSection | None = None
    session: ConsentSession | None = None


YES_PATTERNS = re.compile(
    r"\b(yes|yeah|yep|yup|correct|understand|understood|got it|i do|okay|ok)\b",
    re.I,
)
NO_PATTERNS = re.compile(
    r"\b(no|nope|don't|do not|refuse|decline|not ready)\b",
    re.I,
)
UNSURE_PATTERNS = re.compile(
    r"\b(not sure|unsure|confused|don't understand|do not understand|what do you mean)\b",
    re.I,
)
QUESTION_PATTERNS = re.compile(r"\?|\b(what|why|how|when|where|can you explain)\b", re.I)


def classify_response(text: str) -> PatientResponse:
    cleaned = text.strip()
    if not cleaned:
        return PatientResponse.EMPTY
    if NO_PATTERNS.search(cleaned):
        return PatientResponse.DECLINE
    if UNSURE_PATTERNS.search(cleaned):
        return PatientResponse.UNSURE
    if QUESTION_PATTERNS.search(cleaned):
        return PatientResponse.QUESTION
    if YES_PATTERNS.search(cleaned):
        return PatientResponse.CONFIRM
    return PatientResponse.QUESTION


class ConsentEngine:
    """Deterministic consent flow with bounded Q&A placeholders."""

    MAX_REPROMPTS = 2

    def __init__(self, pack: ConsentPack) -> None:
        self.pack = pack
        self.session = ConsentSession(
            pack_id=pack.id,
            pack_title=pack.title,
            started_at=utc_now_iso(),
        )
        self._section_index = 0
        self._phase = EnginePhase.DISCLAIMER
        self._reprompt_count = 0
        self._current_result: SectionResult | None = None

    @property
    def phase(self) -> EnginePhase:
        return self._phase

    @property
    def current_section(self) -> ConsentSection | None:
        if 0 <= self._section_index < len(self.pack.sections):
            return self.pack.sections[self._section_index]
        return None

    def start(self) -> list[EngineEvent]:
        return [
            EngineEvent(
                phase=EnginePhase.DISCLAIMER,
                text=self.pack.disclaimer,
                session=self.session,
            )
        ]

    def advance(self) -> list[EngineEvent]:
        if self._phase == EnginePhase.DISCLAIMER:
            return self._begin_section()

        if self._phase == EnginePhase.SECTION_SCRIPT:
            return self._after_script()

        if self._phase == EnginePhase.AWAIT_CONFIRM:
            return [
                EngineEvent(
                    phase=EnginePhase.AWAIT_CONFIRM,
                    text="Please say yes if you understand, or ask a question.",
                    section=self.current_section,
                    session=self.session,
                )
            ]

        if self._phase == EnginePhase.QA:
            return [
                EngineEvent(
                    phase=EnginePhase.QA,
                    text="What else would you like to know?",
                    section=self.current_section,
                    session=self.session,
                )
            ]

        return [
            EngineEvent(
                phase=self._phase,
                text="Session finished.",
                session=self.session,
            )
        ]

    def handle_input(self, text: str) -> list[EngineEvent]:
        if self._phase == EnginePhase.COMPLETE:
            return [
                EngineEvent(
                    phase=EnginePhase.COMPLETE,
                    text="This consent session is already complete.",
                    session=self.session,
                )
            ]

        if self._phase == EnginePhase.ESCALATED:
            return [
                EngineEvent(
                    phase=EnginePhase.ESCALATED,
                    text="A clinician has been flagged. Please wait for your care team.",
                    session=self.session,
                )
            ]

        if self._phase == EnginePhase.DISCLAIMER:
            return self._begin_section()

        if self._phase == EnginePhase.SECTION_SCRIPT:
            return self._after_script()

        if self._phase in (EnginePhase.AWAIT_CONFIRM, EnginePhase.QA):
            return self._handle_confirm_or_question(text)

        return []

    def _begin_section(self) -> list[EngineEvent]:
        section = self.current_section
        if section is None:
            return self._complete_session()

        self._current_result = SectionResult(section_id=section.id, status=SectionStatus.PENDING)
        self._reprompt_count = 0
        self._phase = EnginePhase.SECTION_SCRIPT
        return [
            EngineEvent(
                phase=EnginePhase.SECTION_SCRIPT,
                text=section.script,
                section=section,
                session=self.session,
            )
        ]

    def _after_script(self) -> list[EngineEvent]:
        section = self.current_section
        assert section is not None and self._current_result is not None

        self._current_result.status = SectionStatus.DELIVERED

        if section.confirm_prompt:
            self._phase = EnginePhase.QA if section.type.value == "qa" else EnginePhase.AWAIT_CONFIRM
            return [
                EngineEvent(
                    phase=self._phase,
                    text=section.confirm_prompt,
                    section=section,
                    session=self.session,
                )
            ]

        return self._finish_section(SectionStatus.CONFIRMED)

    def _handle_confirm_or_question(self, text: str) -> list[EngineEvent]:
        section = self.current_section
        assert section is not None and self._current_result is not None

        self._current_result.patient_utterances.append(text)
        response = classify_response(text)

        if response == PatientResponse.CONFIRM:
            return self._finish_section(SectionStatus.CONFIRMED)

        if response == PatientResponse.DECLINE:
            return self._escalate("Patient declined or refused to proceed.")

        if response in (PatientResponse.UNSURE, PatientResponse.QUESTION, PatientResponse.EMPTY):
            self._reprompt_count += 1
            if self._reprompt_count > self.MAX_REPROMPTS:
                return self._escalate("Patient needs clinician clarification after multiple attempts.")

            if section.type.value == "qa":
                reply = (
                    "That is a good question. For now I can only explain what is in your "
                    "consent materials. A clinician can give you a personal answer. "
                    "Do you have any other questions, or are you ready to continue?"
                )
            else:
                reply = (
                    "Let me repeat the key point briefly, then you can ask a question. "
                    f"{section.script[:280]}... "
                    f"{section.confirm_prompt or 'Do you understand?'}"
                )

            return [
                EngineEvent(
                    phase=self._phase,
                    text=reply,
                    section=section,
                    session=self.session,
                )
            ]

        return self._finish_section(SectionStatus.CONFIRMED)

    def _finish_section(self, status: SectionStatus) -> list[EngineEvent]:
        assert self._current_result is not None
        self._current_result.status = status
        self.session.section_results.append(self._current_result)
        self._section_index += 1
        self._current_result = None
        self._reprompt_count = 0
        return self._begin_section()

    def _complete_session(self) -> list[EngineEvent]:
        self._phase = EnginePhase.COMPLETE
        self.session.completed_at = utc_now_iso()
        return [
            EngineEvent(
                phase=EnginePhase.COMPLETE,
                text="Consent walkthrough complete. Please meet your care team to sign the form.",
                session=self.session,
            )
        ]

    def _escalate(self, reason: str) -> list[EngineEvent]:
        assert self._current_result is not None
        self._current_result.status = SectionStatus.ESCALATED
        self._current_result.notes = reason
        self.session.section_results.append(self._current_result)
        self.session.escalated = True
        self.session.escalation_reason = reason
        self.session.completed_at = utc_now_iso()
        self._phase = EnginePhase.ESCALATED
        return [
            EngineEvent(
                phase=EnginePhase.ESCALATED,
                text=(
                    f"I will ask a member of your care team to join us. Reason: {reason}"
                ),
                section=self.current_section,
                session=self.session,
            )
        ]
