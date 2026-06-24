# analysis — detection core

Physics-first rolling-element bearing diagnostics. No training data required; this is
the deterministic, explainable base that ML/RUL is layered on later.

## Modules
- `bearing.py` — `bearing_freqs(rpm, n_balls, ball_dia, pitch_dia, contact_angle_deg)`
  → characteristic defect frequencies (fr, FTF, BPFO, BPFI, BSF).
- `envelope.py` — `envelope_spectrum(x, fs, band)` (band-pass → Hilbert envelope →
  spectrum), `defect_score(...)` (amplitude at a defect freq + harmonics),
  `classify(...)` (score every element; max = likely fault).
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
from analysis import bearing_freqs, envelope_spectrum, classify

freqs = bearing_freqs(rpm=1772, n_balls=9, ball_dia=7.94, pitch_dia=39.04)  # CWRU 6205
f, amp = envelope_spectrum(signal, fs=12000, band=(2000, 5000))
scores = classify(f, amp, freqs)
fault = max(scores, key=scores.get)   # e.g. "BPFO"
```

## Notes / roadmap
- **Band selection** is the biggest accuracy lever in noisy plant signals — replace the
  fixed `band` with a kurtogram / spectral-kurtosis sweep (pick the most impulsive band).
- **Order tracking** (resample to shaft angle) for variable-speed machines.
- **Trending + baselines** per asset; **RUL** models once run-to-failure data accrues.
