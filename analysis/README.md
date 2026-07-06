# analysis — detection core

Physics-first rolling-element bearing diagnostics. No training data required; this is
the deterministic, explainable base that ML/RUL is layered on later.

## Modules
- `bearing.py` — `bearing_freqs(rpm, n_balls, ball_dia, pitch_dia, contact_angle_deg)`
  → characteristic defect frequencies (fr, FTF, BPFO, BPFI, BSF).
- `envelope.py` — `envelope_spectrum(x, fs, band)` (band-pass → Hilbert envelope →
  spectrum), `defect_score(...)` (amplitude at a defect freq + harmonics),
  `classify(...)` (score every element; max = likely fault).
- `detect.py` — the decision gate: `harmonic_snr(...)` (defect comb vs local
  envelope noise floor) and `detect(...)` → `healthy` / `suspect` / `faulted`
  verdict + element + margin. Baseline-free mode screens without any per-machine
  data; pass a healthy capture's `classify` scores as `baseline` for the far more
  sensitive product mode (needed for ball faults).
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

## Validated (CWRU, 1772 rpm drive-end set)
| file | truth | baseline-free verdict | harmonic SNR |
|---|---|---|---|
| 98 | normal | healthy | max 3.3 (under warn=4) |
| 106 | inner race | **faulted — BPFI** | 56 |
| 131 | outer race | **faulted — BPFO** | 167 |
| 119 | ball | suspect; **faulted** with `baseline=` (50× over healthy) | 4.1 |

The 0.007″ ball fault is the textbook-hard case (energy smears across 2×BSF + cage
sidebands); baseline-relative mode — the product path — catches it cleanly.

## Notes / roadmap
- **Band selection** is the biggest accuracy lever in noisy plant signals — replace the
  fixed `band` with a kurtogram / spectral-kurtosis sweep (pick the most impulsive band).
- **Ball faults**: add 2×BSF + FTF-sideband-aware scoring, and prefer 48 kHz data.
- **Order tracking** (resample to shaft angle) for variable-speed machines.
- **Trending + baselines** per asset; **RUL** models once run-to-failure data accrues.
