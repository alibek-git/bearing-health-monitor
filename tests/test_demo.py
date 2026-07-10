"""Demo simulator sanity: the synthetic machine must be detectable by the real
pipeline (correct element per fault type), and quiet when healthy.

Imports only demo/simulator.py (pure numpy) — no FastAPI needed to run tests.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import detect, envelope_spectrum, pick_band  # noqa: E402
from demo.simulator import FREQS, FS, capture  # noqa: E402


def verdict(fault, severity, seed=1):
    x = capture(fault, severity, np.random.default_rng(seed))
    band = pick_band(x, FS, FREQS)
    return detect(*envelope_spectrum(x, FS, band=band), FREQS)


def test_healthy_machine_reads_healthy():
    det = verdict("none", 0.0)
    assert det["verdict"] == "healthy"


@pytest.mark.parametrize("fault, element", [
    ("outer", "BPFO"), ("inner", "BPFI"), ("ball", "BSF"),
])
def test_seeded_fault_detected_with_correct_element(fault, element):
    det = verdict(fault, 0.85)
    assert det["verdict"] != "healthy"
    assert max(det["snr"], key=det["snr"].get) == element


def test_slip_is_found():
    # the simulated machine runs 1.8% slow; the detector's estimate must land
    # near it once the fault is strong enough to define the comb
    det = verdict("outer", 0.9)
    assert det["slip"] == pytest.approx(0.982, abs=0.012)


def test_unknown_fault_rejected():
    with pytest.raises(ValueError):
        capture("gearbox", 0.5)
