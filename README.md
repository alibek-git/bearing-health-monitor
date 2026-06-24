# Bearing-Health Monitor  *(working name — rename freely)*

Retrofittable wireless vibration sensing + edge analytics that predicts rolling-element
**bearing failure weeks ahead**, for heavy industry — assembled and supported locally in
Kazakhstan, starting with the Karaganda industrial basin (Qarmet and peers).

This repo is the product. The thesis, market, build plan (import / assemble / code),
go-to-market, unit economics, risks, and the **P0 technical spec** live in
[`docs/business-plan.md`](docs/business-plan.md).

## Status

**P0 — validate the core claim.** Prove that off-the-shelf vibration + envelope
analysis cleanly detects a *known* bearing defect: first on public labeled datasets,
then on one real machine. No product hardware yet. ~$150, ~2–4 weeks.

## Layout

| Path | What |
|---|---|
| [`analysis/`](analysis/) | Detection core — bearing defect frequencies, envelope demodulation, condition features (the IP) |
| [`scripts/`](scripts/) | Runnable validation (e.g. against the CWRU bearing dataset) |
| [`firmware/`](firmware/) | Edge sensor sampling (Teensy + ADXL1002) — P0 notes |
| [`data/`](data/) | Local datasets (gitignored) — CWRU / IMS / NASA + field recordings |
| [`docs/`](docs/) | Business plan + P0 technical spec |

## Quickstart (P0 analysis)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# download a CWRU drive-end .mat into data/, then:
python scripts/validate_cwru.py data/<file>.mat --fs 12000 --rpm 1772
```

It prints the bearing defect frequencies, per-element scores, and the likely fault,
and plots the envelope spectrum with the defect peaks marked.

## How it works (the core IP)

Vibration → band-pass the impact-resonance band → **Hilbert envelope** (amplitude
demodulation) → envelope spectrum → peak-pick at the bearing **defect frequencies**
(BPFO / BPFI / BSF / FTF) and harmonics. The largest score names the failing element.
Physics-first, so it works with **no training data**; anomaly/RUL ML is layered on as
field data accumulates. Details in [`analysis/README.md`](analysis/README.md).
