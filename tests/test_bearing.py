"""Defect-frequency formulas against the published CWRU 6205-2RS values."""

import pytest

from analysis import bearing_freqs, fault_lines


def test_cwru_6205_defect_frequencies():
    # SKF 6205-2RS JEM at 1772 rpm — reference values from the CWRU fault-frequency
    # table (multiples of shaft speed: BPFO 3.5848x, BPFI 5.4152x, BSF 2.3568x,
    # FTF 0.39828x).
    fr = 1772 / 60.0
    freqs = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
    assert freqs["fr"] == pytest.approx(fr)
    assert freqs["BPFO"] == pytest.approx(3.5848 * fr, rel=1e-3)
    assert freqs["BPFI"] == pytest.approx(5.4152 * fr, rel=1e-3)
    assert freqs["BSF"] == pytest.approx(2.3568 * fr, rel=1e-3)
    assert freqs["FTF"] == pytest.approx(0.39828 * fr, rel=1e-3)


def test_inner_always_above_outer():
    # BPFI > BPFO for any physical geometry (rolling elements pass the inner race
    # faster than the outer), and all defect frequencies scale linearly with rpm.
    a = bearing_freqs(rpm=1000, n_balls=12, ball_dia=10.0, pitch_dia=60.0)
    b = bearing_freqs(rpm=2000, n_balls=12, ball_dia=10.0, pitch_dia=60.0)
    assert a["BPFI"] > a["BPFO"] > a["FTF"] > 0
    for k in a:
        assert b[k] == pytest.approx(2 * a[k])


def test_fault_lines_encode_modulation_physics():
    freqs = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
    lines = fault_lines(freqs, n_harmonics=2, n_sidebands=1)
    # BPFO: plain harmonics only
    assert lines["BPFO"] == pytest.approx([freqs["BPFO"], 2 * freqs["BPFO"]])
    # BPFI: each harmonic flanked by +-fr sidebands
    assert pytest.approx(lines["BPFI"][:3]) == [
        freqs["BPFI"], freqs["BPFI"] - freqs["fr"], freqs["BPFI"] + freqs["fr"]]
    # BSF: centered on 2xBSF (ball hits both races per revolution), +-FTF sidebands
    assert pytest.approx(lines["BSF"][:3]) == [
        2 * freqs["BSF"], 2 * freqs["BSF"] - freqs["FTF"], 2 * freqs["BSF"] + freqs["FTF"]]
    # all positive
    assert all(x > 0 for v in lines.values() for x in v)
