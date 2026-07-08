"""Record vibration blocks from the P0 Teensy sampler and score them.

Counterpart of ``firmware/p0_sampler/p0_sampler.ino``: reads the framed uint16
stream from USB serial, verifies checksums and sequence continuity, converts to
volts, saves the capture per the data/README.md field convention (.npy +
sidecar .json), and — when RPM and bearing geometry are given — runs the full
detector on the capture and prints the verdict.

    python scripts/record_teensy.py --asset pump7 --seconds 10 --rpm 1480 \
        --bearing 9 7.94 39.04 0        # n_balls ball_dia pitch_dia angle

Requires pyserial (pip install pyserial). The port is auto-detected on macOS
(/dev/cu.usbmodem*) and Linux (/dev/ttyACM*); pass --port to override.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import struct
import sys
import time
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import bearing_freqs, detect, envelope_spectrum, pick_band  # noqa: E402

MAGIC = b"VIB1"
HDR = struct.Struct("<IHI")  # seq uint32, n uint16, dropped uint32
CSUM = struct.Struct("<H")
VREF, ADC_MAX = 3.3, 4095


def build_frame(seq, samples, dropped=0):
    """Encode one frame exactly as the firmware does (used by tests/simulators)."""
    samples = np.asarray(samples, dtype="<u2")
    csum = int(samples.sum(dtype=np.uint64) & 0xFFFF)
    return (MAGIC + HDR.pack(seq, len(samples), dropped)
            + samples.tobytes() + CSUM.pack(csum))


def parse_frames(buf):
    """Extract complete, checksum-valid frames from ``buf`` (bytes-like).

    Returns ``(frames, remainder)`` where ``frames`` is a list of
    ``(seq, dropped, samples ndarray)`` and ``remainder`` is the unconsumed
    tail (a partial frame, or garbage awaiting more data). Corrupt frames are
    skipped by resyncing on the next magic.
    """
    data = bytes(buf)
    frames = []
    pos = 0
    while True:
        i = data.find(MAGIC, pos)
        if i < 0:
            # keep a tail in case a magic straddles the read boundary
            return frames, data[max(pos, len(data) - (len(MAGIC) - 1)):]
        if len(data) - i < len(MAGIC) + HDR.size:
            return frames, data[i:]
        seq, n, dropped = HDR.unpack_from(data, i + len(MAGIC))
        end = i + len(MAGIC) + HDR.size + 2 * n + CSUM.size
        if len(data) < end:
            return frames, data[i:]
        payload = np.frombuffer(data, dtype="<u2", count=n,
                                offset=i + len(MAGIC) + HDR.size)
        (csum,) = CSUM.unpack_from(data, end - CSUM.size)
        if int(payload.sum(dtype=np.uint64) & 0xFFFF) == csum:
            frames.append((seq, dropped, payload))
            pos = end
        else:
            pos = i + 1  # corrupt frame: resync on the next magic


def assemble(frames):
    """Concatenate frame payloads; return ``(samples, gaps, dropped)``.

    ``gaps`` counts missing sequence numbers between consecutive frames (host
    lost data); ``dropped`` is the firmware's own overflow counter from the
    last frame (device lost data because the host read too slowly).
    """
    if not frames:
        return np.array([], dtype=np.uint16), 0, 0
    gaps = sum(max(0, b[0] - a[0] - 1) for a, b in zip(frames, frames[1:]))
    return np.concatenate([f[2] for f in frames]), gaps, frames[-1][1]


def autodetect_port():
    for pat in ("/dev/cu.usbmodem*", "/dev/ttyACM*"):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    raise SystemExit("no Teensy serial port found — pass --port")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", default=None, help="serial port (default: auto-detect)")
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--fs", type=float, default=51200.0, help="must match the firmware FS")
    ap.add_argument("--asset", default="bench", help="asset name for the output path")
    ap.add_argument("--rpm", type=float, default=None, help="shaft speed (enables analysis)")
    ap.add_argument("--bearing", type=float, nargs=4, default=None,
                    metavar=("N_BALLS", "BALL_DIA", "PITCH_DIA", "ANGLE"),
                    help="bearing geometry (enables analysis)")
    ap.add_argument("--out", default=None, help="output .npy (default: data/field/<asset>/...)")
    args = ap.parse_args()

    try:
        import serial
    except ImportError:
        raise SystemExit("pyserial not installed: pip install pyserial")

    port = args.port or autodetect_port()
    n_target = int(args.seconds * args.fs)
    print(f"recording ~{args.seconds:.0f}s ({n_target} samples) from {port} ...")

    frames, buf = [], b""
    with serial.Serial(port, timeout=1) as ser:
        ser.reset_input_buffer()
        deadline = time.monotonic() + args.seconds + 10.0
        got = 0
        while got < n_target and time.monotonic() < deadline:
            chunk = ser.read(65536)
            if not chunk:
                continue
            new, buf = parse_frames(buf + chunk)
            frames.extend(new)
            got = sum(len(f[2]) for f in frames)

    samples, gaps, dropped = assemble(frames)
    if samples.size == 0:
        raise SystemExit("no valid frames received — is p0_sampler flashed and wired?")
    if gaps or dropped:
        print(f"WARNING: {gaps} host-side gaps, {dropped} device-side dropped blocks "
              "— treat this capture as suspect")

    volts = samples[:n_target].astype(float) * (VREF / ADC_MAX)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    rpm_tag = f"_{args.rpm:.0f}rpm" if args.rpm else ""
    out = args.out or f"data/field/{args.asset}/{stamp}{rpm_tag}.npy"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    np.save(out, volts)
    meta = {"fs": args.fs, "rpm": args.rpm, "asset": args.asset, "port": port,
            "vref": VREF, "adc_bits": 12, "n_samples": int(volts.size),
            "host_gaps": int(gaps), "device_dropped": int(dropped),
            "bearing": dict(zip(("n_balls", "ball_dia", "pitch_dia",
                                 "contact_angle_deg"), args.bearing)) if args.bearing else None}
    with open(out.replace(".npy", ".json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"saved {volts.size} samples -> {out} (+ sidecar .json)")

    if args.rpm and args.bearing:
        n, bd, pd, ang = args.bearing
        freqs = bearing_freqs(args.rpm, int(n), bd, pd, ang)
        band = pick_band(volts, args.fs, freqs)
        det = detect(*envelope_spectrum(volts, args.fs, band=band), freqs)
        who = f" — likely {det['element']}" if det["element"] else ""
        print(f"band {band[0]:.0f}-{band[1]:.0f} Hz, slip {det['slip']:.3f}")
        print("SNR:", {k: round(v, 1) for k, v in
                       sorted(det["snr"].items(), key=lambda kv: -kv[1])})
        print(f"VERDICT: {det['verdict'].upper()}{who}  (margin {det['margin']:.2f}x alarm)")
    else:
        print("pass --rpm and --bearing to score the capture immediately")


if __name__ == "__main__":
    main()
