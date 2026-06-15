"""Head and antenna motion cues for voice session states."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import numpy as np

from engine.state_machine import EnginePhase

if TYPE_CHECKING:
    from reachy_mini import ReachyMini


logger = logging.getLogger(__name__)


def _head_pose(**kwargs: float):  # type: ignore[no-untyped-def]
    from reachy_mini.utils import create_head_pose

    return create_head_pose(degrees=True, **kwargs)


def set_ready(reachy: ReachyMini, duration: float = 0.5) -> None:
    """Neutral pose — waiting for the patient."""
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=0, roll=0),
            antennas=np.array([0.3, -0.3]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_ready failed: %s", exc)


def set_listening(reachy: ReachyMini, duration: float = 0.35) -> None:
    """Slight tilt — paying attention to the patient."""
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=-5, roll=8),
            antennas=np.array([0.5, -0.5]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_listening failed: %s", exc)


def set_thinking(reachy: ReachyMini, duration: float = 0.4) -> None:
    """Head up, antennas down — processing patient response."""
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=8, roll=0),
            antennas=np.array([-0.2, 0.2]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_thinking failed: %s", exc)


def set_speaking(reachy: ReachyMini, duration: float = 0.35) -> None:
    """Leaning in — robot is talking."""
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=-8, roll=0),
            antennas=np.array([0.4, -0.4]),
            duration=duration,
        )
    except Exception as exc:
        logger.debug("set_speaking failed: %s", exc)


def nod_confirm(reachy: ReachyMini) -> None:
    """Brief nod when the patient confirms understanding."""
    try:
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=-12, roll=0),
            duration=0.25,
        )
        time.sleep(0.3)
        reachy.goto_target(
            head=_head_pose(yaw=0, pitch=0, roll=0),
            duration=0.25,
        )
    except Exception as exc:
        logger.debug("nod_confirm failed: %s", exc)


def cue_for_phase(reachy: ReachyMini, phase: EnginePhase) -> None:
    """Pick a default pose for an engine phase."""
    if phase in (EnginePhase.AWAIT_CONFIRM, EnginePhase.QA):
        set_listening(reachy)
    elif phase in (EnginePhase.COMPLETE, EnginePhase.ESCALATED):
        set_ready(reachy)
    else:
        set_speaking(reachy)
