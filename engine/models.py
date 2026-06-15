from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SectionType(str, Enum):
    SCRIPT = "script"
    QA = "qa"


@dataclass
class ConsentSection:
    id: str
    type: SectionType
    script: str
    confirm_prompt: str | None = None
    must_cover: list[str] = field(default_factory=list)


@dataclass
class ConsentPack:
    id: str
    title: str
    reading_level: str
    disclaimer: str
    sections: list[ConsentSection]


class SectionStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    ESCALATED = "escalated"
    SKIPPED = "skipped"


@dataclass
class SectionResult:
    section_id: str
    status: SectionStatus
    patient_utterances: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class ConsentSession:
    pack_id: str
    pack_title: str
    started_at: str
    section_results: list[SectionResult] = field(default_factory=list)
    completed_at: str | None = None
    escalated: bool = False
    escalation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "pack_title": self.pack_title,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
            "sections": [
                {
                    "section_id": r.section_id,
                    "status": r.status.value,
                    "patient_utterances": r.patient_utterances,
                    "notes": r.notes,
                }
                for r in self.section_results
            ],
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
