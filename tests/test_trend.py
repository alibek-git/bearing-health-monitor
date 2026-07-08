"""Trend logic: baseline, ratios, sustained-crossing alarm (no dataset needed)."""

import numpy as np
import pytest

from analysis import baseline_scores, first_sustained_crossing, trend_ratios


def make_history(n=200, ramp_at=120, element="BPFO", seed=0, peak=30.0):
    """Score history: all elements jitter around their healthy level; one element
    ramps from `ramp_at` to `peak`x by the end (a developing fault)."""
    rng = np.random.default_rng(seed)
    levels = {"BPFO": 0.02, "BPFI": 0.03, "BSF": 0.01, "FTF": 0.015}
    hist = []
    for i in range(n):
        h = {k: v * float(rng.uniform(0.7, 1.4)) for k, v in levels.items()}
        if i >= ramp_at:
            growth = peak ** ((i - ramp_at) / (n - 1 - ramp_at))  # 1x .. peakx
            h[element] *= growth
        hist.append(h)
    return hist


def test_baseline_median_tolerates_outliers():
    hist = make_history()
    hist[5] = {k: v * 50 for k, v in hist[5].items()}  # one junk capture
    base = baseline_scores(hist, 50)
    assert base["BPFO"] == pytest.approx(0.02, rel=0.35)  # median unaffected


def test_baseline_requires_enough_captures():
    with pytest.raises(ValueError, match="baseline"):
        baseline_scores(make_history(n=10), 50)


def test_ratios_flat_then_rising():
    hist = make_history()
    _, ratios = trend_ratios(hist, 50)
    early = [r["BPFO"] for r in ratios[:100]]
    assert max(early) < 3  # healthy life hovers near 1
    assert ratios[-1]["BPFO"] > 15  # fault clearly out of the noise by the end
    assert ratios[-1]["BPFI"] < 3  # other elements stay flat


def test_first_sustained_crossing_finds_the_fault():
    hist = make_history()
    _, ratios = trend_ratios(hist, 50)
    idx, el = first_sustained_crossing(ratios, 10.0, sustain=3)
    assert el == "BPFO"
    assert 120 < idx < 199  # inside the ramp, not before it
    # and it is ordered: warn fires no later than alarm
    widx, wel = first_sustained_crossing(ratios, 4.0, sustain=3)
    assert wel == "BPFO"
    assert widx <= idx


def test_single_spike_does_not_alarm():
    hist = make_history(ramp_at=10**9)  # never ramps
    hist[80] = {k: v * 100 for k, v in hist[80].items()}  # one transient
    _, ratios = trend_ratios(hist, 50)
    idx, el = first_sustained_crossing(ratios, 10.0, sustain=3)
    assert idx is None and el is None
    # sustain=1 would have paged someone at snapshot 80
    idx1, _ = first_sustained_crossing(ratios, 10.0, sustain=1)
    assert idx1 == 80
