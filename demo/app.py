"""Demo dashboard: synthetic machine -> the real detection pipeline -> live UI.

Run locally:   uvicorn demo.app:app --reload      (then open http://127.0.0.1:8000)
Run in Docker: docker build -f demo/Dockerfile -t bearing-demo . \
               && docker run --rm -p 8000:8000 bearing-demo

Every "capture" is one simulated measurement (compressed machine-time: one
capture = one simulated hour). The signal goes through exactly the code that
validated on CWRU and NASA IMS: matched band pick -> envelope spectrum -> slip
alignment -> comb SNR -> healthy/suspect/faulted verdict, plus the early-life
baseline ratio trend with sustained-crossing events.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

import numpy as np
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import detect, envelope_spectrum, pick_band, trend_ratios  # noqa: E402
from analysis.trend import first_sustained_crossing  # noqa: E402
from demo.simulator import FREQS, FS, SLIP, capture  # noqa: E402

N_BASELINE = 12
WARN, ALARM, SUSTAIN = 4.0, 10.0, 3
HOURS_PER_CAPTURE = 1.0

app = FastAPI(title="bearing-health demo")


class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rng = np.random.default_rng(7)
        self.fault = "outer"
        self.mode = "auto"          # auto: severity grows; manual: slider
        self.severity = 0.0
        self.growth = 0.012         # per capture, auto mode
        self.running = False
        self.t0 = datetime(2026, 7, 9, 8, 0, 0)
        self.hours = 0.0
        self.scores = []            # classify() dicts per capture
        self.events = []
        self.crossed = {"warn": None, "alarm": None}


S = State()


class Config(BaseModel):
    fault: str | None = None
    mode: str | None = None
    severity: float | None = None
    growth: float | None = None
    running: bool | None = None


@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.post("/api/reset")
def reset():
    S.reset()
    return {"ok": True}


@app.post("/api/config")
def config(cfg: Config):
    for k, v in cfg.model_dump(exclude_none=True).items():
        setattr(S, k, v)
    return {"ok": True}


def _decimate(x, n):
    step = max(1, len(x) // n)
    return np.asarray(x)[::step]


@app.post("/api/step")
def step():
    if S.running and S.mode == "auto":
        S.severity = min(1.0, S.severity + S.growth * (0.7 + 0.6 * S.rng.random()))

    x = capture(S.fault if S.severity > 0 else "none", S.severity, S.rng)
    band = pick_band(x, FS, FREQS)
    f, amp = envelope_spectrum(x, FS, band=band)
    det = detect(f, amp, FREQS)
    S.scores.append(det["scores"])
    S.hours += HOURS_PER_CAPTURE
    now = S.t0 + timedelta(hours=S.hours)

    ratios = None
    if len(S.scores) >= N_BASELINE:
        _, all_ratios = trend_ratios(S.scores, N_BASELINE)
        ratios = all_ratios
        for name, thr in (("warn", WARN), ("alarm", ALARM)):
            if S.crossed[name] is None:
                idx, el = first_sustained_crossing(all_ratios, thr, SUSTAIN)
                if idx is not None:
                    t = S.t0 + timedelta(hours=(idx + 1) * HOURS_PER_CAPTURE)
                    S.crossed[name] = {"capture": idx, "element": el,
                                       "time": t.strftime("%d %b %H:%M")}
                    S.events.append(f"{name.upper()} — {el} sustained ≥{thr}× "
                                    f"at {t.strftime('%d %b %H:%M')}")

    sel = f <= 320
    return {
        "time": now.strftime("%d %b %H:%M"),
        "capture": len(S.scores),
        "severity": round(S.severity, 3),
        "fault": S.fault,
        "running": S.running,
        "mode": S.mode,
        "verdict": det["verdict"],
        "element": det["element"],
        "margin": round(det["margin"], 2),
        "slip": round(det["slip"], 4),
        "true_slip": SLIP,
        "band": [round(band[0]), round(band[1])],
        "snr": {k: round(v, 2) for k, v in det["snr"].items()},
        "freqs": {k: round(v * det["slip"], 1) for k, v in FREQS.items() if k != "fr"},
        "wave": [round(float(v), 4) for v in _decimate(x[:2560], 640)],
        "spec_f": [round(float(v), 1) for v in _decimate(f[sel], 320)],
        "spec_a": [round(float(v), 5) for v in _decimate(amp[sel], 320)],
        "ratios": ({k: [round(r[k], 2) for r in ratios] for k in ratios[0]}
                   if ratios else None),
        "baseline_n": N_BASELINE,
        "warn": WARN, "alarm": ALARM,
        "events": S.events[-8:],
    }
