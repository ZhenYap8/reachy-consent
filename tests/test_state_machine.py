from pathlib import Path

from engine import ConsentEngine, load_consent_pack


def test_lap_chole_happy_path() -> None:
    pack_path = Path(__file__).resolve().parents[1] / "consent_packs" / "lap_chole.yaml"
    pack = load_consent_pack(pack_path)
    engine = ConsentEngine(pack)

    events = engine.start()
    assert events[0].phase.name == "DISCLAIMER"

    events = engine.handle_input("ok")
    assert events[0].phase.name == "SECTION_SCRIPT"

    while engine.phase.name not in ("COMPLETE", "ESCALATED"):
        if engine.phase.name in ("AWAIT_CONFIRM", "QA"):
            events = engine.handle_input("yes")
        else:
            events = engine.advance()
        assert events

    assert engine.phase.name == "COMPLETE"
    assert not engine.session.escalated
    assert len(engine.session.section_results) == len(pack.sections)


def test_escalation_on_decline() -> None:
    pack = load_consent_pack(
        Path(__file__).resolve().parents[1] / "consent_packs" / "lap_chole.yaml"
    )
    engine = ConsentEngine(pack)
    engine.start()
    engine.handle_input("continue")  # disclaimer -> greeting
    engine.handle_input("ok")  # greeting -> overview script
    engine.handle_input("ok")  # overview script -> await confirm
    events = engine.handle_input("no I refuse")
    assert events[-1].phase.name == "ESCALATED"
    assert engine.session.escalated
