#!/usr/bin/env python3
"""Interactive CLI demo for the consent state machine (no robot required)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine import ConsentEngine, load_consent_pack


def run_demo(pack_path: Path, export_path: Path | None) -> None:
    pack = load_consent_pack(pack_path)
    engine = ConsentEngine(pack)

    print(f"\n=== Reachy Consent Demo: {pack.title} ===\n")
    print("Type patient responses at the prompt. Commands: /next, /quit\n")

    events = engine.start()
    while events:
        for event in events:
            print(f"\n[ROBOT · {event.phase.name}]\n{event.text}\n")

        if engine.phase.name in ("COMPLETE", "ESCALATED"):
            break

        user_input = input("[PATIENT] ").strip()
        if user_input == "/quit":
            print("Session ended early.")
            break
        if user_input == "/next":
            events = engine.advance()
        else:
            events = engine.handle_input(user_input)

    session = engine.session
    print("\n=== Session summary ===")
    print(json.dumps(session.to_dict(), indent=2))

    if export_path:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")
        print(f"\nExported to {export_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run consent engine CLI demo")
    parser.add_argument(
        "--pack",
        type=Path,
        default=root / "consent_packs" / "lap_chole.yaml",
        help="Path to consent YAML pack",
    )
    parser.add_argument(
        "--export",
        type=Path,
        default=root / "sessions" / "last_session.json",
        help="Where to write session JSON",
    )
    args = parser.parse_args()
    run_demo(args.pack, args.export)


if __name__ == "__main__":
    main()
