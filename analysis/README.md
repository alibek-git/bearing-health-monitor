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
- `features.py` — `velocity_rms_iso(...)` (ISO 10816 severity), `kurtosis`,
  `crest_factor`, `rms` (early-warning + trending).

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
| 98 @12k | normal | healthy (also healthy under the 40-band search — no selection-bias false alarm) | max 3.5 |
| 106 @12k | inner race | **faulted — BPFI** | 35 |
| 131 @12k | outer race | **faulted — BPFO** | 141 |
| 110 @48k | inner race | **faulted — BPFI** | 15–20 |
| 136 @48k | outer race | **faulted — BPFO** | 39 |
| 119 @12k | ball | suspect (auto-band); **faulted** with `baseline=` (26× min over healthy) | 6.1 |
| 123 @48k | ball | **known miss** baseline-free — needs a baseline capture | 2.2 |

The 0.007″ ball fault is the literature-hard case: the Smith & Randall CWRU
benchmark classes B007 as non-diagnosable by conventional envelope analysis.
Our honest posture: baseline-free screening reaches *suspect* at best on ball
faults; the baseline-relative mode — the product path, where every monitored
asset records a healthy baseline at install — flags them cleanly.

## Notes / roadmap
- ~~Band selection (kurtogram)~~ — done: `pick_band`, matched + blind criteria.
- ~~Ball-fault sideband scoring~~ — done: `fault_lines` (2×BSF ± FTF, BPFI ± fr).
- **Order tracking** (resample to shaft angle) for variable-speed machines.
- **Trending + baselines** per asset (`validate_ims.py` next); **RUL** models once
  run-to-failure data accrues.
