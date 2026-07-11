"""WAV analysis path: PCM scaling, channel mixing, and detection roundtrip.

A synthetic BPFO impact train (from tests/test_detect.py) is quantized to
int16, written as a real WAV file, and read back through scripts/analyze_wav.py
— the detector must still call the fault after the roundtrip. synthetic_pair
generates at fs=51200 and the wav header simply carries that rate: the pipeline
is sample-rate-agnostic, which is the whole point of the phone-recording path.
"""

import os
import sys

import numpy as np
import pytest
from scipy.io import wavfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
from analyze_wav import load_wav, to_float  # noqa: E402

from analysis import bearing_freqs, detect, envelope_spectrum, pick_band  # noqa: E402
from test_detect import synthetic_pair  # noqa: E402

FS = 51200  # synthetic_pair generates at this rate; the wav header carries it
FREQS = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)


def as_int16(x, full_scale=0.5):
    """Quantize to int16 at ``full_scale`` of the PCM range (0.5 = -6 dBFS)."""
    x = np.asarray(x, dtype=float)
    return np.round(x / np.abs(x).max() * full_scale * 32767).astype(np.int16)


@pytest.fixture(scope="module")
def faulted():
    return synthetic_pair()[1]


def test_int_scaling_unit_range():
    assert to_float(np.array([-32768, 0, 32767], np.int16)) == pytest.approx(
        [-1.0, 0.0, 32767 / 32768])
    assert to_float(np.array([0, 128, 255], np.uint8)) == pytest.approx(
        [-1.0, 0.0, 127 / 128])
    assert to_float(np.array([-2 ** 31, 0, 2 ** 31 - 1], np.int32)) == pytest.approx(
        [-1.0, 0.0, (2 ** 31 - 1) / 2 ** 31])
    # float wavs pass through untouched
    assert to_float(np.array([-0.25, 0.75], np.float32)) == pytest.approx([-0.25, 0.75])


def test_mono_roundtrip_detects_bpfo(tmp_path, faulted):
    p = tmp_path / "faulted.wav"
    wavfile.write(p, FS, as_int16(faulted))
    fs, x = load_wav(p)
    assert fs == FS
    assert x.ndim == 1 and x.dtype == np.float64
    assert np.abs(x).max() <= 1.0
    assert np.abs(x).max() == pytest.approx(0.5, abs=0.01)  # -6 dBFS survived scaling
    band = pick_band(x, fs, FREQS)  # auto band, as the CLI default
    det = detect(*envelope_spectrum(x, fs, band=band), FREQS)
    assert det["verdict"] == "faulted"
    assert det["element"] == "BPFO"


def test_stereo_mixes_to_mono(tmp_path, faulted):
    ints = as_int16(faulted)
    p = tmp_path / "stereo.wav"
    wavfile.write(p, FS, np.stack([ints, ints], axis=1))
    fs, x = load_wav(p)  # default: mix all channels down
    assert fs == FS
    assert x.ndim == 1 and x.size == ints.size
    assert np.abs(x).max() <= 1.0
    # identical channels: the mix equals either single channel
    _, x1 = load_wav(p, channel=1)
    assert np.allclose(x, x1)


def test_cli_end_to_end(tmp_path, capsys, monkeypatch):
    import analyze_wav
    _, faulted2 = synthetic_pair(seconds=2.0)  # default --trim 0.5 leaves 1.5 s
    p = tmp_path / "rec.wav"
    wavfile.write(p, FS, as_int16(faulted2))
    monkeypatch.setattr(sys, "argv", ["analyze_wav.py", str(p), "--rpm", "1772"])
    analyze_wav.main()
    out = capsys.readouterr().out
    assert "VERDICT: FAULTED" in out
    assert "BPFO" in out
    assert "slip" in out and "band:" in out
