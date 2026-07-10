"""Envelope-band selection by spectral kurtosis (coarse kurtogram).

Bearing impacts excite whichever structural resonance happens to ring on that
machine — a fixed band-pass window misses it on real plant signals. The kurtogram
idea: the most *impulsive* band (highest kurtosis of the band-passed signal)
is where the impacts live; demodulate there. This is the single biggest accuracy
lever of envelope analysis in the field.

This is the coarse, dependable version: a grid of overlapping candidate bands
rather than the full binary-tree fast kurtogram — adequate for P0 and easy to
reason about.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

from .features import kurtosis


def band_grid(fs, f_lo=500.0, n_octaves_min=None, widths=(1 / 3, 2 / 3, 1.0)):
    """Overlapping candidate bands between ``f_lo`` and ~0.45*fs.

    For a set of center frequencies (quarter-octave spaced) and relative widths
    (band = center*width), yields (lo, hi) pairs clipped to the valid range.
    """
    f_hi = 0.45 * fs
    bands = []
    c = f_lo * 1.5
    while c < f_hi:
        for w in widths:
            lo, hi = c - c * w / 2.0, c + c * w / 2.0
            if lo >= f_lo * 0.5 and hi <= f_hi and hi - lo >= 200.0:
                bands.append((round(lo, 1), round(hi, 1)))
        c *= 2 ** 0.25
    return bands


def pick_band(x, fs, freqs=None, f_lo=500.0):
    """Return ``(lo, hi)`` of the best demodulation band.

    Two criteria:

    - **Matched** (``freqs`` given — the dict from ``bearing_freqs``): pick the
      band whose envelope spectrum shows the strongest defect-line comb (max
      per-element :func:`analysis.detect.comb_snr`). Directly optimizes what the
      detector reads, and is robust to non-bearing impulsivity (electrical
      spikes, cocks) that fools plain kurtosis.
    - **Blind** (no ``freqs``): kurtosis of the band-passed *signal*, the classic
      spectral-kurtosis proxy — ~3 for in-band Gaussian noise, high where an
      impact train rings. Use when bearing geometry/RPM are unknown.

    Note: the matched criterion maximizes over ~40 bands, which inflates the
    winning SNR on pure noise (selection bias). Verify the healthy ceiling on a
    baseline capture before trusting borderline verdicts from auto-banded runs.
    """
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    best, best_score = None, -np.inf
    slips = (1.0, 0.99, 0.975, 0.96)  # coarse; detect() refines afterwards
    for lo, hi in band_grid(fs, f_lo):
        sos = butter(4, (lo, hi), btype="bandpass", fs=fs, output="sos")
        xb = sosfiltfilt(sos, x)
        if freqs is None:
            score = kurtosis(xb) + 0.1 * np.log2((hi - lo) / 200.0)  # wide tiebreak
        else:
            from .bearing import fault_lines
            from .detect import comb_snr
            from .envelope import envelope_spectrum

            # Evaluate the comb at a few slip factors: on a slipping machine the
            # true comb sits a few % below nominal, and judging bands only at
            # the kinematic lines makes the search near-blind (band choice then
            # degenerates to noise). detect() re-estimates slip finely later.
            f, amp = envelope_spectrum(xb, fs, band=None)
            score = max(comb_snr(f, amp, lines)
                        for s in slips
                        for lines in fault_lines(
                            {k: v * s for k, v in freqs.items()}).values())
        if score > best_score:
            best, best_score = (lo, hi), score
    return best
