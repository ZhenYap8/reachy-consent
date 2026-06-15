"""Shared consent engine bridge for the Reachy conversation app."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine import VoiceConsentBridge, load_consent_pack  # noqa: E402


@lru_cache(maxsize=1)
def get_voice_bridge() -> VoiceConsentBridge:
    """Load or reuse the consent voice bridge for tool calls."""
    pack_env = os.getenv("CONSENT_PACK_PATH")
    if pack_env:
        pack_path = Path(pack_env)
    else:
        pack_path = REPO_ROOT / "consent_packs" / "lap_chole.yaml"
    pack = load_consent_pack(pack_path)
    bridge = VoiceConsentBridge(pack)
    bridge.start()
    return bridge


def reset_voice_bridge() -> None:
    get_voice_bridge.cache_clear()
