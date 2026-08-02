# analysis — detection core

Physics-first rolling-element bearing diagnostics. No training data required; this is
the deterministic, explainable base that ML/RUL is layered on later.

## Modules
- `bearing.py` — `bearing_freqs(rpm, n_balls, ball_dia, pitch_dia, contact_angle_deg)`
  → characteristic defect frequencies (fr, FTF, BPFO, BPFI, BSF);
  `fault_lines(freqs)` → the expected envelope lines per element, encoding the
  modulation physics (BPFI harmonics carry ±fr sidebands; ball faults live at
  **2×BSF ± FTF**, not the rarely-visible 1×BSF comb).
- `envelope.py` — `envelope_spectrum(x, fs, band)` (band-pass → Hilbert envelope →
  spectrum; `band=None` skips filtering), `line_score`/`defect_score` (amplitude at
  expected lines), `classify(...)` (score every element over its physics line set).
- `detect.py` — the decision gate: `comb_snr(...)` (expected-line comb vs local
  envelope noise floor; *robust* — drops the strongest line so a lone machine tone
  coinciding with one expected line cannot fake a comb) and `detect(...)` →
  `healthy` / `suspect` / `faulted` verdict + element + margin. Baseline-free mode
  screens without any per-machine data; pass a healthy capture's `classify` scores
  as `baseline` for the far more sensitive product mode (needed for ball faults).
- `kurtogram.py` — `pick_band(x, fs, freqs)` chooses the demodulation band:
  *matched* criterion (max defect-comb SNR over a band grid) when geometry is
  known, blind spectral-kurtosis otherwise. The biggest accuracy lever on real
  plant signals.
- `trend.py` — the product signal: per-capture score histories → early-life
  baseline (median) → ratio trajectories → `first_sustained_crossing(...)`
  (N consecutive captures over threshold; one noisy snapshot never pages anyone).
- `features.py` — `velocity_rms_iso(...)` (ISO 10816 severity), `kurtosis`,
  `crest_factor`, `rms` (early-warning + trending).

`detect()` also estimates **bearing slip** (`estimate_slip`): under real load the
cage runs a few % below kinematic speed, dragging every defect line down — IMS
runs at 2.5% slip and a fixed ±1% window misses the true comb entirely. One
global scale factor, searched per capture, re-aligns the whole line grid (and
being global, it cannot invent an element that isn't there).

## Pipeline
```
raw acceleration ─▶ band-pass resonance band ─▶ Hilbert envelope ─▶ envelope spectrum
                                                                          │
   bearing geometry + RPM ─▶ defect frequencies ───────────────▶ peak-pick @ defect freqs
                                                                          │
                                                          {BPFO,BPFI,BSF,FTF} scores → fault
```

## Example
```python
from analysis import bearing_freqs, envelope_spectrum, detect

freqs = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)  # CWRU 6205
f, amp = envelope_spectrum(signal, fs=12000, band=(2000, 5000))
det = detect(f, amp, freqs)           # optionally baseline=<healthy classify() scores>
det["verdict"], det["element"]        # e.g. ("faulted", "BPFO")
```

## Validated (CWRU, 1772 rpm drive-end sets, kurtogram auto-band)
| file | truth | baseline-free verdict | comb SNR |
|---|---|---|---|
| 98 @12k | normal | healthy — but at **3.95 against `warn=4.0`** (see below) | max **3.95** |
| 106 @12k | inner race | **faulted — BPFI** | 35 |
| 131 @12k | outer race | **faulted — BPFO** | 141 |
| 110 @48k | inner race | **faulted — BPFI** | 15–20 |
| 136 @48k | outer race | **faulted — BPFO** | 39 |
| 119 @12k | ball | suspect (auto-band); with `baseline=` flags a change (26–50×) but ranks the **wrong element** (BPFO) | 6.1 |
| 123 @48k | ball | **known miss** baseline-free — needs a baseline capture | 2.2 |

**The healthy ceiling is 3.95, not 3.5.** Earlier revisions of this table quoted 3.5
from a weaker configuration than the detector actually runs. Under the shipped
default path (matched kurtogram band + `slip="auto"`), CWRU 98 reaches **3.95**
against `warn=4.0` — a **1.2% margin**, on the only healthy record in the set.

The 0.007″ ball fault is the literature-hard case: the Smith & Randall CWRU
benchmark classes B007 as non-diagnosable by conventional envelope analysis.
Our honest posture: baseline-free screening reaches *suspect* at best on ball
faults, and **baseline-relative mode does not rescue the element** — on 119 all four
elements rise 26–50× together, BSF is the *lowest* of the four, and the top rank goes
to BPFO. Broadband level has moved; the ratio ranking cannot say which element moved
it. Ball-fault element identification is unsolved here.

## Validated (NASA IMS set 2, run-to-failure, 984 snapshots / 7 days)
Bearing 1 dies of an outer-race failure at the end of the test. Per-snapshot
matched band + slip alignment (the rig runs 2.5% slip), sustained-crossing
trend (3 consecutive):

| trend | WARN (≥4) | ALARM (≥10) |
|---|---|---|
| comb SNR (no baseline) | **BPFO, 2d 20h before failure** | **BPFO, 2d 12h before failure** |
| score / early-life baseline | 3d 20h (element fuzzy at warn level) | **BPFO 23×, 2d 20h before failure** |

### All four bearings alarm — the failing one alarms first

The earlier claim here ("the surviving bearings never sustain an alarm") was wrong.
Running all four channels through the shipped pipeline at the shipped thresholds
(`EVERY=10` → 99 snapshots, ~100 min apart):

| ch | bearing | sustained WARN (≥4) | sustained ALARM (≥10) | peak comb SNR |
|---|---|---|---|---|
| 0 | **1 — dies (outer race)** | idx 54 | **idx 59** | 31.6 |
| 1 | 2 — survives | idx 72 | idx 90 | 33.2 |
| 2 | 3 — survives | idx 84 | idx 91 | 25.2 |
| 3 | 4 — survives | idx 71 | idx 88 | 38.5 |

All four reach sustained alarm, all four attributed to BPFO. All four are identical
ZA-2115s on one shaft, so they share a BPFO — the neighbours' late alarms are
presumed casing crosstalk from the disintegrating bearing, not four simultaneous
faults. Note also that bearing 4 peaks *higher* (38.5) than the bearing that actually
failed (31.6): **magnitude does not rank which bearing is dying.**

The defensible claim is therefore: *correct element named, sustained alarm ~2.5 days
before the bearing dies and **~2 days before the earliest neighbour**, zero training
data.* Per-bearing localisation on a shared shaft needs a cross-channel
disambiguation step that does not exist yet.

### What this evidence does not support

Worth being explicit, because the numbers above are easy to over-read:

- **No false-alarm rate.** One healthy CWRU record, reading 1.2% under the warn
  threshold. A rate needs a healthy population, not a single capture.
- **No lead-time distribution.** n=1 failure event. One observation has no
  dispersion, so "2.5 days" has no lower bound — and nothing here supports the
  word *weeks*.
- **No ball-fault element identification.** See the CWRU section above.
- **No per-bearing localisation** on a multi-bearing shaft.
- **Nothing through the product's sensor chain.** CWRU and IMS are lab piezo
  recordings at constant speed and load. The product is a MEMS part on a magnet
  mount, duty-cycled, on a variable-load machine. That gap is unmeasured.

Closing these is cheap and mostly needs no hardware: IMS sets 1 and 3 are already in
`data/ims_bearings.zip` (+3 failures), and XJTU-SY, PRONOSTIA/FEMTO, Paderborn and
MFPT would take the run-to-failure count from 1 to ~35 and build a real healthy
denominator.

## Notes / roadmap
- ~~Band selection (kurtogram)~~ — done: `pick_band`, matched + blind criteria.
- ~~Ball-fault sideband scoring~~ — done: `fault_lines` (2×BSF ± FTF, BPFI ± fr).
- ~~Trending + baselines~~ — done: `trend.py`, validated on IMS set 2.
- **Order tracking** (resample to shaft angle) for variable-speed machines.
- **RUL** models on the trend trajectories (IMS sets 1+3 in the same archive).
