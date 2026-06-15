"""Motion cues for consent voice states (mirrors engine.voice_cues)."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from reachy_mini import ReachyMini


logger = logging.getLogger(__name__)


def _head_pose(**kwargs: float):  # type: ignore[no-untyped-def]
    from reachy_mini.utils import create_head_pose

    return create_head_pose(degrees=True, **kwargs)


def set_ready(reachy: ReachyMini, duration: float = 0.5) -> None:
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=0, roll=0),
            antennas=np.array([0.3, -0.3]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_ready: %s", exc)


def set_thinking(reachy: ReachyMini, duration: float = 0.4) -> None:
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=8, roll=0),
            antennas=np.array([-0.2, 0.2]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_thinking: %s", exc)


def set_speaking(reachy: ReachyMini, duration: float = 0.35) -> None:
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=-8, roll=0),
            antennas=np.array([0.4, -0.4]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_speaking: %s", exc)


def nod_confirm(reachy: ReachyMini) -> None:
    try:
        reachy.goto_target(head=_head_pose(yaw=0, pitch=-12, roll=0), duration=0.25)
        time.sleep(0.3)
        reachy.goto_target(head=_head_pose(yaw=0, pitch=0, roll=0), duration=0.25)
    except Exception as exc:
        logger.debug("nod_confirm: %s", exc)
