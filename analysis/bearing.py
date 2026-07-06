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


def fault_lines(freqs, n_harmonics=4, n_sidebands=1):
    """Expected envelope-spectrum lines per element, encoding the modulation physics.

    - BPFO: plain harmonics (outer-race defect is fixed in the load zone).
    - BPFI: harmonics with +-fr sidebands (defect rides the shaft through the load
      zone once per rev, amplitude-modulating the impacts).
    - BSF:  harmonics of **2xBSF** with +-FTF sidebands (a ball spall strikes both
      races each ball revolution; the cage carries it through the load zone). Plain
      1xBSF combs are rarely visible in practice - this is why naive BSF scoring
      misses ball faults.
    - FTF:  plain harmonics.

    ``freqs`` is the dict from :func:`bearing_freqs`. Returns ``{element: [Hz, ...]}``.
    """
    fr, ftf = freqs["fr"], freqs["FTF"]
    sb = range(1, n_sidebands + 1)

    def comb(center, spacing):
        lines = []
        for h in range(1, n_harmonics + 1):
            c = h * center
            lines.append(c)
            for k in sb:
                lines.extend((c - k * spacing, c + k * spacing))
        return [x for x in lines if x > 0]

    return {
        "BPFO": [h * freqs["BPFO"] for h in range(1, n_harmonics + 1)],
        "BPFI": comb(freqs["BPFI"], fr),
        "BSF": comb(2.0 * freqs["BSF"], ftf),
        "FTF": [h * ftf for h in range(1, n_harmonics + 1)],
    }
