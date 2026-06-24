"""Scalar condition features: ISO velocity, kurtosis, crest factor, RMS.

These complement the envelope spectrum: the envelope says *which* element is failing,
these say *how severe* and feed trending.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

G = 9.80665  # m/s^2 per g


def rms(x):
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x * x)))


def crest_factor(x):
    """Peak / RMS. Rises early with impulsive (bearing) faults, then falls as the
    fault matures and the signal becomes broadband."""
    x = np.asarray(x, dtype=float)
    r = rms(x)
    return float(np.max(np.abs(x)) / r) if r else 0.0


def kurtosis(x):
    """Fourth standardized moment. ~3 for healthy (Gaussian) vibration; rises with
    impulsiveness from early bearing damage."""
    x = np.asarray(x, dtype=float)
    s = x.std()
    return float(np.mean(((x - x.mean()) / s) ** 4)) if s else 0.0


def velocity_rms_iso(accel_g, fs, band=(10.0, 1000.0)):
    """ISO 10816 / 20816 broadband velocity RMS in mm/s, from acceleration in g.

    Band-passes to the standard 10-1000 Hz band, integrates acceleration to velocity,
    re-band-passes to remove integration drift, and returns the RMS (the value the
    standard's A/B/C/D severity zones are defined on).
    """
    a = (np.asarray(accel_g, dtype=float) - np.mean(accel_g)) * G  # g -> m/s^2
    sos = butter(4, band, btype="bandpass", fs=fs, output="sos")
    a = sosfiltfilt(sos, a)
    v = np.cumsum(a) / fs            # integrate to velocity (m/s)
    v = sosfiltfilt(sos, v)          # kill integration drift
    return float(np.sqrt(np.mean(v * v)) * 1000.0)  # m/s -> mm/s
