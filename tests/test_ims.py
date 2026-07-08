"""IMS set-2 run-to-failure trend validation (skipped when the data is absent).

Test set 2: 984 snapshots over ~7 days, 4 channels = bearings 1-4, 20 kHz.
Bearing 1 (channel 0) ends in an outer-race failure. The product claim under
test: its BPFO score rises against the early-life baseline and crosses alarm
*days* before the end, while a surviving bearing stays quiet (or alarms only
later, from casing-borne vibration of the dying neighbor).

Subsamples every 10th snapshot to keep runtime reasonable (~10 s).
"""

from pathlib import Path

import numpy as np
import pytest

from analysis import (bearing_freqs, detect, envelope_spectrum, pick_band,
                      first_sustained_crossing)

IMS2 = Path(__file__).resolve().parent.parent / "data" / "ims" / "2nd_test"

pytestmark = pytest.mark.skipif(
    not (IMS2.is_dir() and len(list(IMS2.iterdir())) > 900),
    reason="IMS 2nd_test snapshots not in data/ims/2nd_test — see data/README.md",
)

FS = 20000.0
FREQS = bearing_freqs(2000.0, n_balls=16, ball_dia=8.407, pitch_dia=71.501,
                      contact_angle_deg=15.17)
EVERY = 10  # ~99 snapshots, ~100 min apart; the two tests take ~40 s together


def channel_snrs(channel):
    """Per-snapshot slip-aware comb SNR with a matched band pick per capture —
    the product-mode screening trajectory."""
    files = sorted(p for p in IMS2.iterdir() if not p.name.startswith("."))[::EVERY]
    hist = []
    for p in files:
        x = np.loadtxt(p, usecols=channel)
        band = pick_band(x, FS, FREQS)
        hist.append(detect(*envelope_spectrum(x, FS, band=band), FREQS)["snr"])
    return hist


def test_bearing1_outer_race_warning_days_ahead():
    snrs = channel_snrs(0)
    # sustained WARN: the "come look at this bearing" signal
    idx, el = first_sustained_crossing(snrs, 4.0, sustain=3)
    assert idx is not None, "bearing 1 never reached sustained warn — pipeline broken"
    assert el == "BPFO"  # the documented failure mode, correct element
    # ~100 min per snapshot: >= 25 snapshots =~ >= 1.7 days of warning
    assert len(snrs) - idx >= 25, f"warn too late: only {len(snrs) - idx} snapshots of lead"
    # and it eventually reaches sustained ALARM level before the end
    aidx, ael = first_sustained_crossing(snrs, 10.0, sustain=3)
    assert aidx is not None and ael == "BPFO"


def test_surviving_bearing_alarms_later_or_never():
    healthy = channel_snrs(2)  # bearing 3 survives set 2
    failing = channel_snrs(0)
    h_idx, _ = first_sustained_crossing(healthy, 4.0, sustain=3)
    f_idx, _ = first_sustained_crossing(failing, 4.0, sustain=3)
    assert f_idx is not None
    assert h_idx is None or h_idx > f_idx  # discrimination: the dying bearing pages first
