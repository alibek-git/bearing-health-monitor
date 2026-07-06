"""Envelope (demodulation) analysis for rolling-element bearing diagnostics.

A spalled bearing produces periodic impacts that ring the surrounding structure at
its high-frequency resonances. Band-passing that resonance band and taking the
amplitude envelope (Hilbert) demodulates the impact train; its spectrum then shows a
clear peak (plus harmonics) at the characteristic defect frequency of the failing
element.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt, welch


def envelope_spectrum(x, fs, band=(2000.0, 6000.0), nperseg=1 << 15):
    """Band-pass the resonance band, Hilbert-demodulate, return its spectrum.

    Returns ``(freqs, amplitude)``. ``band`` is the high-frequency window the bearing
    impacts excite; pick it with :func:`analysis.kurtogram.pick_band`, or start with
    a fixed window (e.g. 1-6 kHz) and refine. ``band`` upper edge must be < fs/2.
    Pass ``band=None`` when ``x`` is already band-passed.
    """
    x = np.asarray(x, dtype=float)
    xb = x - x.mean()
    if band is not None:
        sos = butter(4, band, btype="bandpass", fs=fs, output="sos")
        xb = sosfiltfilt(sos, xb)
    env = np.abs(hilbert(xb))          # amplitude demodulation
    env -= env.mean()
    f, p = welch(env, fs=fs, nperseg=min(len(env), nperseg), scaling="spectrum")
    return f, np.sqrt(p)               # amplitude vs frequency


def line_score(f, amp, lines, tol=0.01):
    """Summed envelope amplitude at a list of expected spectral lines (Hz)."""
    f = np.asarray(f)
    amp = np.asarray(amp)
    df = (f[1] - f[0]) if len(f) > 1 else 1.0
    s = 0.0
    for ft in lines:
        m = np.abs(f - ft) <= max(tol * ft, df)
        if m.any():
            s += float(amp[m].max())
    return s


def defect_score(f, amp, target, n_harmonics=4, tol=0.01):
    """Summed envelope amplitude at a defect frequency and its first harmonics.

    A developing fault shows a *comb* of harmonics, not just the fundamental, so
    summing harmonics is more robust than a single-bin read.
    """
    return line_score(f, amp, [target * h for h in range(1, n_harmonics + 1)], tol)


def classify(f, amp, freqs, n_harmonics=4):
    """Score each element; the largest score names the likely failing element.

    ``freqs`` is the dict from :func:`analysis.bearing.bearing_freqs`. Scores are
    summed over each element's physics-informed line set (harmonics + modulation
    sidebands; see :func:`analysis.bearing.fault_lines` — in particular ball
    faults are scored at 2xBSF +- FTF, not the rarely-visible 1xBSF comb).
    Returns ``{element: score}`` for BPFO / BPFI / BSF / FTF (shaft ``fr`` excluded).
    """
    from .bearing import fault_lines

    return {
        k: line_score(f, amp, lines)
        for k, lines in fault_lines(freqs, n_harmonics).items()
    }
