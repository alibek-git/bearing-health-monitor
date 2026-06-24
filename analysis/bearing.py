"""Bearing characteristic defect frequencies."""

from __future__ import annotations

import numpy as np


def bearing_freqs(rpm, n_balls, ball_dia, pitch_dia, contact_angle_deg=0.0):
    """Characteristic defect frequencies (Hz) for a rolling-element bearing.

    ``ball_dia`` and ``pitch_dia`` must share units (mm or in). Geometry comes from
    the bearing datasheet; if unknown, approximate ``BPFO ~= 0.4 * n * fr`` and
    ``BPFI ~= 0.6 * n * fr``.

    Returns a dict:
      fr   - shaft rotation (1x)
      FTF  - fundamental train (cage)
      BPFO - ball pass frequency, outer race
      BPFI - ball pass frequency, inner race
      BSF  - ball spin frequency
    """
    fr = rpm / 60.0
    r = (ball_dia / pitch_dia) * np.cos(np.radians(contact_angle_deg))
    return {
        "fr": fr,
        "FTF": 0.5 * fr * (1 - r),
        "BPFO": (n_balls / 2.0) * fr * (1 - r),
        "BPFI": (n_balls / 2.0) * fr * (1 + r),
        "BSF": (pitch_dia / (2.0 * ball_dia)) * fr * (1 - r * r),
    }
