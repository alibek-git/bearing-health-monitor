"""Validate the bearing detector against a Case Western Reserve (CWRU) .mat file.

Proves the algorithm on labeled public data before any hardware. Download a
drive-end .mat from the CWRU Bearing Data Center, then:

    python scripts/validate_cwru.py data/<file>.mat --fs 12000 --rpm 1772

The CWRU drive-end test bearing (SKF 6205-2RS JEM) geometry is the default. A faulted
file should score highest on the element that matches its label (e.g. an outer-race
file → BPFO).
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from scipy.io import loadmat

# allow `python scripts/validate_cwru.py` from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import bearing_freqs, classify, envelope_spectrum  # noqa: E402


def load_de_signal(path):
    """Return the drive-end accelerometer channel from a CWRU .mat."""
    mat = loadmat(path)
    key = next((k for k in mat if k.endswith("_DE_time")), None)
    if key is None:
        raise SystemExit(f"No '*_DE_time' channel in {path}; keys: {list(mat)}")
    return np.asarray(mat[key]).ravel()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("matfile", help="path to a CWRU .mat file (in data/)")
    ap.add_argument("--fs", type=float, default=12000, help="sample rate (12000 or 48000)")
    ap.add_argument("--rpm", type=float, default=1772, help="shaft speed")
    ap.add_argument("--band", type=float, nargs=2, default=(2000.0, 5000.0),
                    help="envelope band-pass (Hz); upper edge must be < fs/2")
    ap.add_argument("--plot", action="store_true", help="plot the envelope spectrum")
    args = ap.parse_args()

    x = load_de_signal(args.matfile)
    # CWRU drive-end bearing: SKF 6205-2RS JEM — 9 balls, ball 7.94 mm, pitch 39.04 mm
    freqs = bearing_freqs(args.rpm, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
    f, amp = envelope_spectrum(x, args.fs, band=tuple(args.band))
    scores = classify(f, amp, freqs)

    print(f"file: {args.matfile}  samples={x.size}  fs={args.fs}  rpm={args.rpm}")
    print("defect freqs (Hz):", {k: round(v, 1) for k, v in freqs.items()})
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    print("scores:", {k: round(v, 5) for k, v in ranked})
    print("LIKELY FAULT:", ranked[0][0])

    if args.plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 4))
        plt.plot(f, amp, lw=0.8)
        for name in ("BPFO", "BPFI", "BSF"):
            plt.axvline(freqs[name], ls="--", alpha=0.6, label=name)
        plt.xlim(0, max(freqs["BPFI"] * 4, 500))
        plt.xlabel("Hz"); plt.ylabel("envelope amplitude"); plt.legend()
        plt.title(f"Envelope spectrum — likely {ranked[0][0]}")
        plt.tight_layout(); plt.show()


if __name__ == "__main__":
    main()
