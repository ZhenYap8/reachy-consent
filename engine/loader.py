from __future__ import annotations

from pathlib import Path

import yaml

from engine.models import ConsentPack, ConsentSection, SectionType


def load_consent_pack(path: Path | str) -> ConsentPack:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    procedure = data["procedure"]
    sections = [
        ConsentSection(
            id=section["id"],
            type=SectionType(section.get("type", "script")),
            script=section["script"].strip(),
            confirm_prompt=section.get("confirm_prompt"),
            must_cover=list(section.get("must_cover", [])),
        )
        for section in data["sections"]
    ]
    return ConsentPack(
        id=procedure["id"],
        title=procedure["title"],
        reading_level=procedure.get("reading_level", "grade_8"),
        disclaimer=procedure.get("disclaimer", "").strip(),
        sections=sections,
    )
