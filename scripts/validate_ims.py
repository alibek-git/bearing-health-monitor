"""Trend the detector over a NASA IMS run-to-failure test (the RUL story).

The IMS rig (Univ. of Cincinnati / NSF IMS Center): 4 Rexnord ZA-2115 double-row
bearings on one shaft, 2000 rpm, 6000 lbf radial load, one ~1 s vibration
snapshot (20,480 points) every ~10 min until failure. Test set 2 (984 snapshots
over ~7 days) ends with an outer-race failure of bearing 1 — channel 0.

Download & extract (see data/README.md), then:

    python scripts/validate_ims.py data/ims/2nd_test --channel 0 --plot

Walks the snapshots chronologically, scores each with the envelope detector,
builds the early-life baseline, and reports the first *sustained* warn/alarm
crossings with their lead time before the end of the test. Writes the full
trend to a CSV next to the data.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import (bearing_freqs, detect, envelope_spectrum,  # noqa: E402
                      first_sustained_crossing, kurtosis, pick_band, trend_ratios,
                      velocity_rms_iso)

# Rexnord ZA-2115: 16 rollers/row, roller 0.331 in, pitch 2.815 in, angle 15.17 deg
ZA2115 = dict(n_balls=16, ball_dia=8.407, pitch_dia=71.501, contact_angle_deg=15.17)


def snapshot_time(name):
    """IMS filenames are timestamps like 2004.02.12.10.32.39."""
    return datetime.strptime(name, "%Y.%m.%d.%H.%M.%S")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", help="IMS test dir of snapshot files (e.g. data/ims/2nd_test)")
    ap.add_argument("--channel", type=int, default=0, help="column = bearing channel (set 2: 0-3)")
    ap.add_argument("--fs", type=float, default=20000.0, help="sample rate (IMS readme: 20 kHz)")
    ap.add_argument("--rpm", type=float, default=2000.0)
    ap.add_argument("--band", type=float, nargs=2, default=None,
                    help="fixed envelope band; default: kurtogram-matched pick per snapshot")
    ap.add_argument("--baseline-files", type=int, default=100,
                    help="early snapshots forming the healthy baseline")
    ap.add_argument("--warn", type=float, default=4.0, help="warn ratio over baseline")
    ap.add_argument("--alarm", type=float, default=10.0, help="alarm ratio over baseline")
    ap.add_argument("--sustain", type=int, default=3,
                    help="consecutive snapshots required to call a crossing")
    ap.add_argument("--every", type=int, default=1, help="use every Nth snapshot (speed)")
    ap.add_argument("--csv", default=None, help="trend CSV path (default: <dir>_ch<N>_trend.csv)")
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    d = Path(args.directory)
    files = sorted(p for p in d.iterdir() if not p.name.startswith("."))[:: args.every]
    if len(files) < args.baseline_files + 10:
        raise SystemExit(f"only {len(files)} snapshots in {d} — not a run-to-failure sequence")

    freqs = bearing_freqs(args.rpm, **ZA2115)
    print(f"{len(files)} snapshots, channel {args.channel}, defect freqs (Hz):",
          {k: round(v, 1) for k, v in freqs.items()})
    band = tuple(args.band) if args.band else None
    print("envelope band:", f"{band[0]:.0f}-{band[1]:.0f} Hz" if band
          else "kurtogram-matched per snapshot")

    # Per snapshot: matched band -> slip-aligned comb SNR (self-normalized, the
    # primary trend) + absolute scores (for the baseline-ratio trend).
    snrs, scores, extras = [], [], []
    for i, p in enumerate(files):
        x = np.loadtxt(p, usecols=args.channel)
        b = band or pick_band(x, args.fs, freqs)
        det = detect(*envelope_spectrum(x, args.fs, band=b), freqs)
        snrs.append(det["snr"])
        scores.append(det["scores"])
        extras.append((det["slip"], kurtosis(x), velocity_rms_iso(x, args.fs)))
        if (i + 1) % 100 == 0:
            print(f"  scored {i + 1}/{len(files)}")

    base, ratios = trend_ratios(scores, args.baseline_files)
    t0, t_end = snapshot_time(files[0].name), snapshot_time(files[-1].name)
    print(f"run: {t0} -> {t_end}  ({(t_end - t0).days}d {(t_end - t0).seconds // 3600}h)")

    def report(label, history, warn, alarm, unit):
        for name, thr in (("WARN", warn), ("ALARM", alarm)):
            idx, el = first_sustained_crossing(history, thr, args.sustain)
            if idx is None:
                print(f"{label} {name} (>={thr}{unit}, {args.sustain} sustained): never")
            else:
                t = snapshot_time(files[idx].name)
                lead = t_end - t
                print(f"{label} {name} (>={thr}{unit}): {t}  element={el}"
                      f"  value={history[idx][el]:.1f}"
                      f"  -> {lead.days}d {lead.seconds // 3600}h before end of test")

    report("comb-SNR", snrs, args.warn, args.alarm, "")
    report("baseline-ratio", ratios, args.warn, args.alarm, "x")

    out = args.csv or f"{d}_ch{args.channel}_trend.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        els = list(base.keys())
        w.writerow(["snapshot"] + [f"snr_{k}" for k in els] + [f"score_{k}" for k in els]
                   + [f"ratio_{k}" for k in els] + ["slip", "kurtosis", "vrms_mm_s"])
        for p, s, h, r, (sl, ku, vr) in zip(files, snrs, scores, ratios, extras):
            w.writerow([p.name] + [f"{s[k]:.2f}" for k in els]
                       + [f"{h[k]:.6g}" for k in els] + [f"{r[k]:.3f}" for k in els]
                       + [f"{sl:.4f}", f"{ku:.3f}", f"{vr:.3f}"])
    print("trend written:", out)

    if args.plot:
        import matplotlib.pyplot as plt
        ts = [snapshot_time(p.name) for p in files]
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        for k in base:
            ax1.semilogy(ts, [s[k] for s in snrs], lw=1, label=k)
            ax2.semilogy(ts, [r[k] for r in ratios], lw=1, label=k)
        for ax, ylabel in ((ax1, "comb SNR"), (ax2, "score / baseline")):
            ax.axhline(args.warn, ls="--", c="orange", alpha=0.7)
            ax.axhline(args.alarm, ls="--", c="red", alpha=0.7)
            ax.set_ylabel(ylabel)
            ax.legend(ncol=5, fontsize=8)
        ax1.set_title(f"IMS {d.name} ch{args.channel} — defect trend")
        plt.tight_layout(); plt.show()


if __name__ == "__main__":
    main()
