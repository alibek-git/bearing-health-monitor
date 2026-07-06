"""Validation against real labeled CWRU data (skipped when the files are absent).

Uses the 1-hp / 1772-rpm drive-end set, downloadable from
https://engineering.case.edu/sites/default/files/<n>.mat into data/:

  98.mat  - normal baseline          -> healthy
  106.mat - inner-race 0.007in fault -> faulted, BPFI
  119.mat - ball 0.007in fault       -> known-hard: healthy is NOT acceptable;
            with 98.mat as baseline it must be faulted (~50x over baseline)
  131.mat - outer-race 0.007in fault -> faulted, BPFO
"""

from pathlib import Path

import numpy as np
import pytest

from analysis import bearing_freqs, classify, detect, envelope_spectrum

DATA = Path(__file__).resolve().parent.parent / "data"
FILES = {n: DATA / f"{n}.mat" for n in (98, 106, 119, 131)}

pytestmark = pytest.mark.skipif(
    not all(p.exists() for p in FILES.values()),
    reason="CWRU .mat files not in data/ — see module docstring for the URLs",
)

FS = 12000.0
BAND = (2000.0, 5000.0)
FREQS = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)


def load(n):
    from scipy.io import loadmat

    mat = loadmat(FILES[n])
    key = next(k for k in mat if k.endswith("_DE_time"))
    return np.asarray(mat[key]).ravel()


def spectrum(n):
    return envelope_spectrum(load(n), FS, band=BAND)


def test_normal_is_healthy():
    det = detect(*spectrum(98), FREQS)
    assert det["verdict"] == "healthy"
    assert det["element"] is None


@pytest.mark.parametrize("n, element", [(106, "BPFI"), (131, "BPFO")])
def test_race_faults_detected_baseline_free(n, element):
    det = detect(*spectrum(n), FREQS)
    assert det["verdict"] == "faulted"
    assert det["element"] == element
    assert det["margin"] > 3  # detected with real margin, not borderline


def test_ball_fault_detected_with_baseline():
    # The 0.007in ball fault is the known-hard case: its energy smears across
    # 2xBSF + cage sidebands, so the baseline-free gate only reaches "suspect".
    # It must never read healthy, and baseline mode must flag it outright.
    f, amp = spectrum(119)
    assert detect(f, amp, FREQS)["verdict"] != "healthy"
    baseline = classify(*spectrum(98), FREQS)
    det = detect(f, amp, FREQS, baseline=baseline)
    assert det["verdict"] == "faulted"
    assert min(det["ratios"].values()) > 10  # every element far above baseline
