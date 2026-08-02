# Bearing-Health Monitor  *(working name — rename freely)*

Retrofittable wireless vibration sensing + edge analytics that predicts rolling-element
**bearing failure weeks ahead**, for heavy industry — assembled and supported locally in
Kazakhstan, starting with the Karaganda industrial basin (Qarmet and peers).

This repo is the product. The thesis, market, build plan (import / assemble / code),
go-to-market, unit economics, risks, and the **P0 technical spec** live in
[`docs/business-plan.md`](docs/business-plan.md).

## Status

**P0 Step 1 (public-data validation): done.** On the CWRU 1772-rpm drive-end sets
(12 kHz *and* 48 kHz) the detector reads the normal file *healthy* — including
under the automatic band search — and identifies every **race** fault baseline-free
with the correct element (comb SNR 15–141). **Ball faults are not solved:** they read
*suspect* at best baseline-free, and while the baseline-relative mode does flag CWRU
119 as changed (26–50×), it ranks the wrong element (BPFO, truth = ball). Physics-line
scoring (2×BSF ± FTF, BPFI ± fr) and a matched kurtogram band picker included. Details
in [`analysis/README.md`](analysis/README.md); regression-guarded by `pytest tests/`.

**Run-to-failure trending validated (NASA IMS set 2):** with no training data, and
including automatic band selection and bearing-slip alignment (the rig runs 2.5%
under kinematic frequencies), the detector names the failing element (outer race)
and raises a **sustained alarm ~2.5 days before the bearing dies** — and, on the
same shaft, **about 2 days before its three neighbours**. Those neighbours do also
reach sustained alarm late in the run (all four bearings are identical ZA-2115s, so
they share a BPFO; presumed casing crosstalk). The discrimination claim is therefore
*lead time over the neighbours*, not silence from them. This is the trend/alert
mechanic the product ships with.

> **Evidence scope, stated plainly.** One healthy CWRU record, three fault
> conditions, and one run-to-failure event. The healthy record sits 1.2% under the
> warn threshold, and n=1 supports no lower bound on lead time. Enough to say the
> physics works; not yet enough to quote a false-alarm rate or a lead-time
> distribution to a buyer. See [`analysis/README.md`](analysis/README.md#what-this-evidence-does-not-support).

**Next:** P0 Step 2 — the field rig on one real machine
(see [`docs/p0-bom.md`](docs/p0-bom.md); Teensy on back-order), and
`record_teensy.py` so the rig streams straight into this pipeline.

## Layout

| Path | What |
|---|---|
| [`analysis/`](analysis/) | Detection core — bearing defect frequencies, envelope demodulation, condition features (the IP) |
| [`scripts/`](scripts/) | Runnable validation (e.g. against the CWRU bearing dataset) |
| [`firmware/`](firmware/) | Edge sensor sampling (Teensy + ADXL1002) — P0 notes |
| [`demo/`](demo/) | Live demo dashboard — synthetic machine through the real pipeline (Docker-ready) |
| [`data/`](data/) | Local datasets (gitignored) — CWRU / IMS / NASA + field recordings |
| [`docs/`](docs/) | Business plan + P0 technical spec, BOM, and [patent provenance](docs/patent-provenance.md) |

## Quickstart (P0 analysis)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/                       # synthetic regression tests (no data needed)
# download CWRU drive-end .mat files into data/
# (https://engineering.case.edu/sites/default/files/<n>.mat — 98, 106, 119, 131), then:
python scripts/validate_cwru.py data/131.mat --fs 12000 --rpm 1772
pytest tests/                       # now also runs the CWRU validation tests
```

It prints the bearing defect frequencies, per-element scores/SNR, and a
`HEALTHY / SUSPECT / FAULTED` verdict with margin; `--plot` shows the envelope
spectrum with the defect peaks marked.

## How it works (the core IP)

Vibration → band-pass the impact-resonance band → **Hilbert envelope** (amplitude
demodulation) → envelope spectrum → peak-pick at the bearing **defect frequencies**
(BPFO / BPFI / BSF / FTF) and harmonics. The largest score names the failing element.
Physics-first, so it works with **no training data**; anomaly/RUL ML is layered on as
field data accumulates. Details in [`analysis/README.md`](analysis/README.md).
