"""Synthetic bearing-vibration source for the demo dashboard.

Generates physics-faithful captures: broadband noise + shaft harmonics, plus a
fault-specific impact train ringing a structural resonance —

- outer race: impacts at BPFO, constant amplitude (defect fixed in the load zone)
- inner race: impacts at BPFI, amplitude-modulated at shaft rate (defect rides
  the shaft through the load zone) -> +-fr sidebands
- ball: impacts at 2xBSF (spall strikes both races per ball revolution),
  modulated at cage rate -> +-FTF sidebands

The train runs a couple of percent *below* kinematic frequency (cage slip), so
the demo also exercises the detector's slip alignment — the same effect that
produced the 2.5% miss on NASA's IMS rig. ``severity`` 0..1 scales the impact
energy; past ~0.7 the broadband floor rises too (end-of-life roughness).
"""

from __future__ import annotations

import numpy as np

from analysis import bearing_freqs

# Demo machine: a 1480-rpm pump motor with the CWRU-class 6205 bearing.
RPM = 1480.0
GEOMETRY = dict(n_balls=9, ball_dia=7.94, pitch_dia=39.04, contact_angle_deg=0.0)
FS = 25600.0
SECONDS = 1.0
RESONANCE_HZ = 3400.0
RING_TAU = 0.0009
SLIP = 0.982  # true cage slip of the simulated machine (detector must find it)

FREQS = bearing_freqs(RPM, **GEOMETRY)


def _impact_train(t, rate, amp_of_t):
    """Decaying-resonance impacts every 1/rate seconds, per-impact amplitude
    taken from ``amp_of_t`` evaluated at the impact instant."""
    x = np.zeros_like(t)
    n = int(t[-1] * rate) + 1
    for k in range(n):
        t0 = k / rate
        d = t - t0
        m = (d >= 0) & (d < 12 * RING_TAU)
        x[m] += amp_of_t(t0) * np.exp(-d[m] / RING_TAU) * np.sin(2 * np.pi * RESONANCE_HZ * d[m])
    return x


def capture(fault="none", severity=0.0, rng=None):
    """One ``SECONDS``-long capture (float array, arbitrary g-ish units)."""
    rng = rng or np.random.default_rng()
    t = np.arange(int(FS * SECONDS)) / FS
    fr = FREQS["fr"]

    noise = 0.30 * (1.0 + 2.0 * max(0.0, severity - 0.7)) * rng.standard_normal(t.size)
    shaft = 0.25 * np.sin(2 * np.pi * fr * t) + 0.10 * np.sin(2 * np.pi * 2 * fr * t + 1.0)
    x = noise + shaft
    if fault == "none" or severity <= 0.0:
        return x

    amp = 1.6 * severity
    jitter = lambda: 1.0 + 0.15 * (rng.random() - 0.5)  # noqa: E731 - impact-to-impact spread
    if fault == "outer":
        rate = FREQS["BPFO"] * SLIP
        x += _impact_train(t, rate, lambda t0: amp * jitter())
    elif fault == "inner":
        rate = FREQS["BPFI"] * SLIP
        x += _impact_train(t, rate, lambda t0: amp * jitter()
                           * (0.4 + 0.6 * 0.5 * (1 + np.sin(2 * np.pi * fr * t0))))
    elif fault == "ball":
        rate = 2.0 * FREQS["BSF"] * SLIP
        ftf = FREQS["FTF"] * SLIP
        x += _impact_train(t, rate, lambda t0: amp * jitter()
                           * (0.3 + 0.7 * abs(np.cos(2 * np.pi * ftf * t0))))
    else:
        raise ValueError(f"unknown fault {fault!r}")
    return x
