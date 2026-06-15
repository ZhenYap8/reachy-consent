"""Tests for voice session bridge."""

from pathlib import Path

from engine import VoiceConsentBridge, load_consent_pack
from engine.state_machine import EnginePhase


def test_voice_bridge_auto_advances_scripted_phases() -> None:
    pack = load_consent_pack(
        Path(__file__).resolve().parents[1] / "consent_packs" / "lap_chole.yaml"
    )
    bridge = VoiceConsentBridge(pack)

    events = bridge.start()
    assert events[0].phase == EnginePhase.DISCLAIMER
    assert not bridge.waits_for_patient

    events = bridge.events_after_robot_spoke()
    assert events[0].phase == EnginePhase.SECTION_SCRIPT
    assert not bridge.waits_for_patient

    events = bridge.events_after_robot_spoke()
    assert events
    assert bridge.engine.phase in (EnginePhase.SECTION_SCRIPT, EnginePhase.AWAIT_CONFIRM)


def test_voice_bridge_patient_confirm_advances() -> None:
    pack = load_consent_pack(
        Path(__file__).resolve().parents[1] / "consent_packs" / "lap_chole.yaml"
    )
    bridge = VoiceConsentBridge(pack)
    bridge.start()
    bridge.events_after_robot_spoke()  # disclaimer -> greeting script
    bridge.events_after_robot_spoke()  # greeting -> next section

    while bridge.engine.phase == EnginePhase.SECTION_SCRIPT:
        bridge.events_after_robot_spoke()

    assert bridge.waits_for_patient
    events = bridge.handle_patient_transcript("yes I understand")
    assert events
    assert bridge.engine.phase in (
        EnginePhase.SECTION_SCRIPT,
        EnginePhase.AWAIT_CONFIRM,
        EnginePhase.COMPLETE,
    )


def test_llm_context_includes_procedure() -> None:
    pack = load_consent_pack(
        Path(__file__).resolve().parents[1] / "consent_packs" / "lap_chole.yaml"
    )
    bridge = VoiceConsentBridge(pack)
    bridge.start()
    ctx = bridge.llm_context()
    assert pack.title in ctx
    assert "DISCLAIMER" in ctx
