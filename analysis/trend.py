"""Degradation trending over a sequence of captures of the same machine.

The product signal is not one verdict but a *trend*: defect scores rising
against the asset's own early-life baseline. Absolute thresholds vary by
machine, mounting, and sensor; trends don't. This module turns a history of
per-capture ``classify()`` score dicts into baseline-relative ratio trajectories
and finds the first *sustained* alarm crossing — a single noisy snapshot must
never page anyone.
"""

from __future__ import annotations

import numpy as np

ELEMENTS = ("BPFO", "BPFI", "BSF", "FTF")


def baseline_scores(history, n_baseline):
    """Element-wise median of the first ``n_baseline`` score dicts.

    The median tolerates a few bad captures inside the assumed-healthy window
    (startup transients, a passing forklift).
    """
    if len(history) < n_baseline:
        raise ValueError(f"need >= {n_baseline} captures for a baseline, got {len(history)}")
    keys = history[0].keys()
    return {k: float(np.median([h[k] for h in history[:n_baseline]])) for k in keys}


def trend_ratios(history, n_baseline):
    """Score-over-baseline ratio per element for every capture in ``history``.

    Returns ``(baseline, ratios)`` where ``ratios`` is a list of dicts aligned
    with ``history``. Ratios inside the baseline window hover around 1 by
    construction; a developing fault shows a sustained rise in one element.
    """
    base = baseline_scores(history, n_baseline)
    ratios = [
        {k: h[k] / max(base[k], 1e-30) for k in base}
        for h in history
    ]
    return base, ratios


def first_sustained_crossing(ratios, threshold, sustain=3, element=None):
    """Index and element of the first ratio >= ``threshold`` held for ``sustain``
    consecutive captures. Returns ``(index, element)`` or ``(None, None)``.

    ``sustain`` is the false-alarm guard: one impulsive capture (impact, EMI
    burst) crosses once; a real developing fault stays crossed. The returned
    index is the *first* capture of the sustained run.
    """
    keys = (element,) if element else tuple(ratios[0].keys()) if ratios else ()
    best = (None, None)
    for k in keys:
        run = 0
        for i, r in enumerate(ratios):
            run = run + 1 if r[k] >= threshold else 0
            if run >= sustain:
                start = i - sustain + 1
                if best[0] is None or start < best[0]:
                    best = (start, k)
                break
    return best
