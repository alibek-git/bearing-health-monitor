"""Validation against real labeled CWRU data (skipped when the files are absent).

Drive-end sets at 1772 rpm, downloadable from
https://engineering.case.edu/sites/default/files/<n>.mat into data/:

12 kHz: 98=normal, 106=inner 0.007in, 119=ball 0.007in, 131=outer 0.007in
48 kHz: 110=inner 0.007in, 123=ball 0.007in, 136=outer 0.007in

The 0.007in ball fault is the known-hard case (cf. the Smith & Randall CWRU
benchmark, which classes B007 as non-diagnosable by conventional envelope
analysis): baseline-free at a fixed band it reads healthy; the kurtogram
auto-band lifts it to suspect at 12 kHz; baseline-relative mode flags it
outright. The tests below pin exactly that, no more.
"""

from pathlib import Path

import numpy as np
import pytest

from analysis import bearing_freqs, classify, detect, envelope_spectrum, pick_band

DATA = Path(__file__).resolve().parent.parent / "data"
FILES12 = {n: DATA / f"{n}.mat" for n in (98, 106, 119, 131)}
FILES48 = {n: DATA / f"{n}.mat" for n in (110, 123, 136)}

need12 = pytest.mark.skipif(
    not all(p.exists() for p in FILES12.values()),
    reason="CWRU 12k .mat files not in data/ — see module docstring for the URLs",
)
need48 = pytest.mark.skipif(
    not all(p.exists() for p in FILES48.values()),
    reason="CWRU 48k .mat files not in data/ — see module docstring for the URLs",
)

BAND = (2000.0, 5000.0)
FREQS = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)


def load(n):
    from scipy.io import loadmat

    mat = loadmat(DATA / f"{n}.mat")
    key = next(k for k in mat if k.endswith("_DE_time"))
    return np.asarray(mat[key]).ravel()


def spectrum(n, fs=12000.0, band=BAND):
    return envelope_spectrum(load(n), fs, band=band)


@need12
def test_normal_is_healthy():
    det = detect(*spectrum(98), FREQS)
    assert det["verdict"] == "healthy"
    assert det["element"] is None


@need12
def test_normal_is_healthy_with_auto_band():
    # The band search maximizes over ~40 candidate bands — the robust (drop-top)
    # comb SNR must keep that selection bias from flagging a healthy machine.
    x = load(98)
    band = pick_band(x, 12000.0, FREQS)
    det = detect(*envelope_spectrum(x, 12000.0, band=band), FREQS)
    assert det["verdict"] == "healthy"


@need12
@pytest.mark.parametrize("n, element", [(106, "BPFI"), (131, "BPFO")])
def test_race_faults_detected_baseline_free(n, element):
    det = detect(*spectrum(n), FREQS)
    assert det["verdict"] == "faulted"  # at alarm level (margin >= 1)
    assert det["element"] == element


@need48
@pytest.mark.parametrize("n, element", [(110, "BPFI"), (136, "BPFO")])
def test_race_faults_detected_at_48k_auto_band(n, element):
    x = load(n)
    band = pick_band(x, 48000.0, FREQS)
    det = detect(*envelope_spectrum(x, 48000.0, band=band), FREQS)
    assert det["verdict"] == "faulted"
    assert det["element"] == element


@need12
def test_ball_fault_12k():
    # Baseline-free at the fixed band: reads healthy (documented miss). The
    # kurtogram auto-band lifts it to suspect. Baseline mode flags it outright.
    x = load(119)
    band = pick_band(x, 12000.0, FREQS)
    det = detect(*envelope_spectrum(x, 12000.0, band=band), FREQS)
    assert det["verdict"] != "healthy"
    baseline = classify(*spectrum(98), FREQS)
    det = detect(*spectrum(119), FREQS, baseline=baseline)
    assert det["verdict"] == "faulted"
    assert min(det["ratios"].values()) > 10  # every element far above baseline


@need48
def test_ball_fault_48k_is_the_known_miss():
    # B007 at 48 kHz stays undetected baseline-free even with auto-band — the
    # Smith & Randall benchmark classes it non-diagnosable by envelope analysis.
    # If this test ever fails with element == "BSF", that is an IMPROVEMENT:
    # celebrate, then update this pin.
    x = load(123)
    band = pick_band(x, 48000.0, FREQS)
    det = detect(*envelope_spectrum(x, 48000.0, band=band), FREQS)
    assert det["verdict"] in ("healthy", "suspect")
