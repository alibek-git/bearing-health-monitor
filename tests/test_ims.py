"""IMS set-2 run-to-failure trend validation (skipped when the data is absent).

Test set 2: 984 snapshots over ~7 days, 4 channels = bearings 1-4, 20 kHz.
Bearing 1 (channel 0) ends in an outer-race failure.

The product claim under test is a *lead-time* claim, not a silence claim. All four
bearings are identical ZA-2115s on one shaft and therefore share a BPFO, and as
bearing 1 disintegrates its casing-borne vibration drives the other three over the
alarm threshold too. What must hold is that bearing 1 alarms **first, by a wide
margin** — that is the whole product mechanic. An earlier version of this file
asserted only `h_idx is None or h_idx > f_idx` on a single surviving channel, which
is satisfied by a one-snapshot lead and let a false README claim stand for weeks.

Subsamples every 10th snapshot (~99 captures, ~100 min apart). All four channels are
computed once in a module-scoped fixture and shared by both tests.
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


FAILING = 0          # bearing 1 — the documented outer-race failure
SURVIVING = (1, 2, 3)  # bearings 2-4 — they alarm too, but late
MIN_LEAD = 20        # snapshots (~33 h) bearing 1 must lead the earliest neighbour by


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


@pytest.fixture(scope="module")
def all_channels():
    """All four channels' SNR trajectories — computed once, shared by both tests."""
    return {ch: channel_snrs(ch) for ch in range(4)}


def test_bearing1_outer_race_warning_days_ahead(all_channels):
    snrs = all_channels[FAILING]
    # sustained WARN: the "come look at this bearing" signal
    idx, el = first_sustained_crossing(snrs, 4.0, sustain=3)
    assert idx is not None, "bearing 1 never reached sustained warn — pipeline broken"
    assert el == "BPFO"  # the documented failure mode, correct element
    # ~100 min per snapshot: >= 25 snapshots =~ >= 1.7 days of warning
    assert len(snrs) - idx >= 25, f"warn too late: only {len(snrs) - idx} snapshots of lead"
    # and it eventually reaches sustained ALARM level before the end
    aidx, ael = first_sustained_crossing(snrs, 10.0, sustain=3)
    assert aidx is not None and ael == "BPFO"


def test_failing_bearing_alarms_well_before_every_neighbour(all_channels):
    """The discrimination margin, asserted at ALARM level on all three neighbours.

    Neighbours DO alarm (shared BPFO + casing crosstalk) — that is expected and is
    not a failure. What must hold is the lead time.
    """
    f_idx, f_el = first_sustained_crossing(all_channels[FAILING], 10.0, sustain=3)
    assert f_idx is not None and f_el == "BPFO"

    for ch in SURVIVING:
        h_idx, _ = first_sustained_crossing(all_channels[ch], 10.0, sustain=3)
        if h_idx is None:
            continue  # quieter than expected — strictly better than the claim
        lead = h_idx - f_idx
        assert lead >= MIN_LEAD, (
            f"bearing {ch + 1} alarmed only {lead} snapshots after bearing 1 "
            f"(need >= {MIN_LEAD}); per-bearing discrimination has degraded"
        )


def test_neighbours_do_alarm_as_documented(all_channels):
    """Pins the honest behaviour so the old 'survivors never alarm' claim cannot
    quietly come back. If a future change genuinely silences the neighbours, this
    test should fail loudly and the README should be updated to match."""
    alarmed = [ch for ch in SURVIVING
               if first_sustained_crossing(all_channels[ch], 10.0, sustain=3)[0] is not None]
    assert alarmed == list(SURVIVING), (
        f"expected all of bearings 2-4 to reach sustained alarm late in the run "
        f"(casing crosstalk), got {[c + 1 for c in alarmed]} — update analysis/README.md"
    )
