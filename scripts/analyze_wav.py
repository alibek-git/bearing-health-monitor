"""Analyze a WAV recording of a running bearing (e.g. a phone microphone).

Zero-hardware smoke test: hold a phone near a running bearing and record.
Phones capture 44.1 kHz audio — plenty of bandwidth, and the pipeline is
sample-rate-agnostic. Gross seeded defects are audible as an envelope comb.
Phones save .m4a by default; convert first:

    ffmpeg -i rec.m4a rec.wav

then:

    python scripts/analyze_wav.py rec.wav --rpm 1480 --bearing 9 7.94 39.04 0

A microphone is an *acoustic proxy* for the accelerometer: it hears the airborne
sound of the same impact train, which is fine for detecting gross seeded
defects, but not for calibrated severity (no mounting, unknown transfer path,
room acoustics).
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from scipy.io import wavfile

# allow `python scripts/analyze_wav.py` from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import (bearing_freqs, classify, detect, envelope_spectrum,  # noqa: E402
                      pick_band)


def to_float(data):
    """Convert PCM samples to float in [-1, 1]; float data passes through.

    Handles the WAV integer formats scipy returns: uint8 (offset-binary),
    int16, and int32 (incl. 24-bit files, which scipy widens to int32).
    """
    data = np.asarray(data)
    if data.dtype == np.uint8:
        return (data.astype(np.float64) - 128.0) / 128.0
    if data.dtype.kind == "i":
        return data.astype(np.float64) / float(2 ** (8 * data.dtype.itemsize - 1))
    return data.astype(np.float64)


def load_wav(path, channel=None, trim=0.0):
    """Load a WAV as float mono in [-1, 1]. Returns ``(fs, samples)``.

    ``channel`` selects one channel of a multi-channel file (default: mix all
    to mono). ``trim`` cuts that many seconds from the start (phones fumble at
    record start: handling noise, auto-gain settling).
    """
    fs, data = wavfile.read(path)
    x = to_float(data)
    if x.ndim > 1:
        if channel is None:
            x = x.mean(axis=1)
        elif channel < x.shape[1]:
            x = x[:, channel]
        else:
            raise SystemExit(f"{path}: no channel {channel} (file has {x.shape[1]})")
    elif channel not in (None, 0):
        raise SystemExit(f"{path}: mono file has no channel {channel}")
    x = x[int(trim * fs):]
    if x.size == 0:
        raise SystemExit(f"{path}: nothing left after trimming {trim:g}s")
    return fs, x


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("wavfile", help="path to a .wav recording (convert .m4a with ffmpeg)")
    ap.add_argument("--rpm", type=float, required=True, help="shaft speed")
    ap.add_argument("--bearing", type=float, nargs=4, default=(9, 7.94, 39.04, 0),
                    metavar=("N_BALLS", "BALL_DIA", "PITCH_DIA", "ANGLE"),
                    help="bearing geometry (default: 9 7.94 39.04 0 — the 6205 "
                    "class used on the CWRU rig and the P0 bench)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--band", type=float, nargs=2, metavar=("LO", "HI"),
                   help="fixed envelope band-pass (Hz); upper edge must be < fs/2")
    g.add_argument("--auto-band", action="store_true",
                   help="pick the band by matched kurtogram (analysis.pick_band) — "
                   "this is already the default when --band is not given")
    ap.add_argument("--baseline", help="healthy .wav of the same rig; enables the far "
                    "more sensitive baseline-relative mode")
    ap.add_argument("--channel", type=int, default=None,
                    help="channel index to analyze (default: mix all channels to mono)")
    ap.add_argument("--trim", type=float, default=0.5,
                    help="seconds cut from the start (default 0.5 — phones fumble "
                    "at record start)")
    ap.add_argument("--plot", action="store_true", help="plot the envelope spectrum")
    args = ap.parse_args()

    fs, x = load_wav(args.wavfile, args.channel, args.trim)
    n, bd, pd, ang = args.bearing
    freqs = bearing_freqs(args.rpm, int(n), bd, pd, ang)
    auto = args.band is None
    band = pick_band(x, fs, freqs) if auto else tuple(args.band)
    f, amp = envelope_spectrum(x, fs, band=band)

    baseline = None
    if args.baseline:
        fsb, xb = load_wav(args.baseline, args.channel, args.trim)
        fb, ab = envelope_spectrum(xb, fsb, band=band)
        baseline = classify(fb, ab, freqs)

    det = detect(f, amp, freqs, baseline=baseline)

    print(f"file: {args.wavfile}  samples={x.size}  fs={fs} Hz  "
          f"duration={x.size / fs:.2f}s (after {args.trim:g}s trim)  rpm={args.rpm}")
    print("defect freqs (Hz):", {k: round(v, 1) for k, v in freqs.items()})
    print(f"band: {band[0]:.0f}-{band[1]:.0f} Hz"
          f"{' (auto kurtogram)' if auto else ''}, slip {det['slip']:.3f}")
    print("scores:", {k: round(v, 5) for k, v in
                      sorted(det["scores"].items(), key=lambda kv: -kv[1])})
    print("harmonic SNR:", {k: round(v, 1) for k, v in
                            sorted(det["snr"].items(), key=lambda kv: -kv[1])})
    if det["ratios"] is not None:
        print("vs baseline:", {k: round(v, 1) for k, v in
                               sorted(det["ratios"].items(), key=lambda kv: -kv[1])})
    who = f" — likely {det['element']}" if det["element"] else ""
    print(f"VERDICT: {det['verdict'].upper()}{who}  (margin {det['margin']:.2f}x alarm)")

    if args.plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 4))
        plt.plot(f, amp, lw=0.8)
        for name in ("BPFO", "BPFI", "BSF"):
            plt.axvline(freqs[name], ls="--", alpha=0.6, label=name)
        plt.xlim(0, max(freqs["BPFI"] * 4, 500))
        plt.xlabel("Hz"); plt.ylabel("envelope amplitude"); plt.legend()
        plt.title(f"Envelope spectrum — {det['verdict']}{who}")
        plt.tight_layout(); plt.show()


if __name__ == "__main__":
    main()
