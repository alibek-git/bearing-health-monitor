"""Frame protocol of the Teensy recorder (pure host-side logic, no hardware).

The wire format is defined twice — in the firmware (p0_sampler.ino) and in
scripts/record_teensy.py — so these tests pin the host implementation against
frames built by its own encoder, plus every corruption mode the serial link
can realistically produce: split reads, garbage, bit-flips, lost blocks.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
from record_teensy import assemble, build_frame, parse_frames  # noqa: E402


def blocks(n_frames=4, n=256, seed=0):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, 4096, n).astype("<u2") for _ in range(n_frames)]


def test_roundtrip():
    payloads = blocks()
    stream = b"".join(build_frame(i, p) for i, p in enumerate(payloads))
    frames, rest = parse_frames(stream)
    assert rest == b""
    assert [f[0] for f in frames] == [0, 1, 2, 3]
    for (_, _, got), want in zip(frames, payloads):
        assert np.array_equal(got, want)


def test_partial_frame_stays_in_remainder():
    payloads = blocks(2)
    stream = build_frame(0, payloads[0]) + build_frame(1, payloads[1])
    cut = len(stream) - 100  # split mid-frame, as serial reads do
    frames, rest = parse_frames(stream[:cut])
    assert len(frames) == 1
    frames2, rest2 = parse_frames(rest + stream[cut:])
    assert len(frames2) == 1 and rest2 == b""
    assert np.array_equal(frames2[0][2], payloads[1])


def test_garbage_prefix_resyncs():
    p = blocks(1)[0]
    stream = b"\x00noise\xffVIB" + build_frame(7, p)  # incl. a fake partial magic
    frames, rest = parse_frames(stream)
    assert len(frames) == 1 and frames[0][0] == 7 and rest == b""


def test_corrupt_checksum_skipped():
    good, bad = blocks(2)
    frame_bad = bytearray(build_frame(0, bad))
    frame_bad[20] ^= 0xFF  # flip a payload byte -> checksum mismatch
    frames, _ = parse_frames(bytes(frame_bad) + build_frame(1, good))
    assert [f[0] for f in frames] == [1]  # corrupt frame dropped, next recovered


def test_assemble_reports_gaps_and_drops():
    p = blocks(3)
    stream = (build_frame(0, p[0]) + build_frame(1, p[1])
              + build_frame(5, p[2], dropped=2))  # seqs 2-4 lost host-side
    frames, _ = parse_frames(stream)
    samples, gaps, dropped = assemble(frames)
    assert samples.size == 3 * 256
    assert gaps == 3
    assert dropped == 2


def test_assemble_empty():
    samples, gaps, dropped = assemble([])
    assert samples.size == 0 and gaps == 0 and dropped == 0


def test_end_to_end_wire_to_verdict():
    # A faulted signal digitized the way the firmware would (12-bit counts around
    # mid-supply), framed, parsed back, converted to volts, and scored: the whole
    # host path must still see the BPFO fault.
    from analysis import bearing_freqs, detect, envelope_spectrum
    from test_detect import synthetic_pair

    _, faulted = synthetic_pair()
    counts = np.clip(np.round(faulted / 3.3 * 4095 / 4 + 2048), 0, 4095).astype("<u2")
    stream = b"".join(build_frame(i, counts[i * 2048:(i + 1) * 2048])
                      for i in range(len(counts) // 2048))
    frames, _ = parse_frames(stream)
    samples, gaps, dropped = assemble(frames)
    assert gaps == 0 and dropped == 0
    volts = samples.astype(float) * (3.3 / 4095)
    freqs = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
    det = detect(*envelope_spectrum(volts, 51200, band=(2000, 6000)), freqs)
    assert det["verdict"] == "faulted"
    assert det["element"] == "BPFO"
