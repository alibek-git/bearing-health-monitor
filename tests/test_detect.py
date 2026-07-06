"""Decision-gate behavior on fabricated spectra and synthetic signals.

Fabricated spectra give exact, deterministic SNR values (peak/floor), so the
healthy/suspect/faulted zone boundaries are tested without any randomness. The
synthetic-signal test then exercises the full pipeline (band-pass -> Hilbert ->
Welch -> gate) end to end with a seeded RNG.
"""

import numpy as np
import pytest

from analysis import (bearing_freqs, classify, detect, envelope_spectrum,
                      harmonic_snr)

FREQS = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)


def comb_spectrum(target, peak, n_harmonics=4, floor=1.0, df=0.25, fmax=800.0):
    """Flat floor with `peak`-height bins at target*1..n — harmonic SNR is exactly
    peak/floor."""
    f = np.arange(0.0, fmax, df)
    amp = np.full_like(f, floor)
    for h in range(1, n_harmonics + 1):
        amp[np.argmin(np.abs(f - target * h))] = peak
    return f, amp


def test_harmonic_snr_exact():
    f, amp = comb_spectrum(FREQS["BPFO"], peak=20.0)
    assert harmonic_snr(f, amp, FREQS["BPFO"]) == pytest.approx(20.0)
    # flat spectrum -> SNR 1
    assert harmonic_snr(f, np.ones_like(f), FREQS["BPFO"]) == pytest.approx(1.0)


def test_zone_boundaries():
    for peak, verdict in [(2.0, "healthy"), (5.0, "suspect"), (20.0, "faulted")]:
        f, amp = comb_spectrum(FREQS["BPFO"], peak=peak)
        det = detect(f, amp, FREQS)
        assert det["verdict"] == verdict, f"peak={peak}"
        if verdict == "healthy":
            assert det["element"] is None
        else:
            assert det["element"] == "BPFO"


def test_baseline_mode_escalates():
    # A comb too weak for the baseline-free gate (SNR 3 < warn 4) but 30x the
    # stored healthy baseline -> product mode must escalate it to faulted.
    f, amp = comb_spectrum(FREQS["BSF"], peak=3.0)
    scores = classify(f, amp, FREQS)
    baseline = dict(scores)            # every element at its healthy level (ratio 1)
    baseline["BSF"] = scores["BSF"] / 30.0  # ...except BSF, which rose 30x
    assert detect(f, amp, FREQS)["verdict"] == "healthy"
    det = detect(f, amp, FREQS, baseline=baseline)
    assert det["verdict"] == "faulted"
    assert det["element"] == "BSF"
    assert det["margin"] == pytest.approx(3.0)  # 30x over a 10x alarm


def test_baseline_mode_never_downgrades():
    # The reverse of escalation: a comb that is unambiguously faulted baseline-free
    # (SNR 20) judged against a DEGRADED stored baseline (the faulted scores
    # themselves, so every ratio is ~1) must stay faulted with the baseline-free
    # element and margin. Kills the mutant that overwrites the verdict
    # unconditionally instead of taking the more severe of the two modes.
    f, amp = comb_spectrum(FREQS["BPFO"], peak=20.0)
    baseline = classify(f, amp, FREQS)
    det = detect(f, amp, FREQS, baseline=baseline)
    assert det["verdict"] == "faulted"
    assert det["element"] == "BPFO"
    assert det["margin"] == pytest.approx(2.0)  # SNR 20 / alarm 10, not ratio 1/10


def test_rejects_evidence_free_verdicts():
    # A safety gate must fail loudly rather than return a confident verdict built
    # on no evidence.
    f, amp = comb_spectrum(FREQS["BPFO"], peak=1.0)
    # non-finite spectrum (dropped samples / sensor glitch -> NaN propagates)
    bad = amp.copy()
    bad[10] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        detect(f, bad, FREQS)
    # every defect frequency beyond the spectrum (wrong fs / rpm / geometry) —
    # even the slowest element (FTF ~996 Hz at this rpm) is past the 800 Hz span
    too_fast = bearing_freqs(rpm=150000, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
    with pytest.raises(ValueError, match="no defect frequency"):
        detect(f, amp, too_fast)
    # baseline that is not a healthy classify() dict
    with pytest.raises(ValueError, match="baseline"):
        detect(f, amp, FREQS, baseline={"BPFO": 1.0, "BPFI": 1.0, "FTF": 1.0})


def synthetic_pair(fs=51200, seconds=1.0, seed=0, noise=0.35):
    """(healthy, faulted) accelerations: broadband noise + shaft 1x, and the same
    plus a BPFO impact train ringing a 3.8 kHz resonance. ``noise=0.35`` puts the
    faulted comb comfortably past the alarm threshold (robust SNR ~15) while the
    healthy leg stays at the noise floor — this tests the pipeline, not the
    threshold knife-edge."""
    t = np.arange(int(fs * seconds)) / fs
    rng = np.random.default_rng(seed)
    shaft = 0.2 * np.sin(2 * np.pi * FREQS["fr"] * t)
    healthy = noise * rng.standard_normal(t.size) + shaft
    impacts = np.zeros_like(t)
    for k in range(int(seconds * FREQS["BPFO"])):
        d = t - k / FREQS["BPFO"]
        m = d >= 0
        impacts[m] += np.exp(-d[m] / 8e-4) * np.sin(2 * np.pi * 3800.0 * d[m])
    faulted = impacts + noise * rng.standard_normal(t.size) + shaft
    return healthy, faulted


def test_synthetic_end_to_end():
    healthy, faulted = synthetic_pair()
    fh, ah = envelope_spectrum(healthy, 51200, band=(2000, 6000))
    ff, af = envelope_spectrum(faulted, 51200, band=(2000, 6000))
    assert detect(fh, ah, FREQS)["verdict"] == "healthy"
    det = detect(ff, af, FREQS)
    assert det["verdict"] == "faulted"
    assert det["element"] == "BPFO"
    # and the classifier ranks the true element first
    scores = classify(ff, af, FREQS)
    assert max(scores, key=scores.get) == "BPFO"
