# scripts

Runnable tools that exercise the `analysis/` core.

## `validate_cwru.py`
Validate the detector on a labeled Case Western Reserve (CWRU) bearing file.

```bash
python scripts/validate_cwru.py data/<file>.mat --fs 12000 --rpm 1772 --plot
# ball faults need the sensitive baseline-relative mode:
python scripts/validate_cwru.py data/119.mat --baseline data/98.mat
```
Prints defect frequencies, per-element scores, harmonic SNR, and a
`HEALTHY / SUSPECT / FAULTED` verdict with margin; with `--plot`, shows the envelope
spectrum with BPFO/BPFI/BSF marked. `--baseline <healthy.mat>` compares against a
healthy capture of the same rig (the product-mode path — required to catch the
smeared combs of ball faults).

## Planned
- `validate_ims.py` — NASA IMS run-to-failure (trend the score over the run to the failure).
- `record_teensy.py` — pull live blocks from the P0 sensor (see `firmware/`) and score them.
- `kurtogram.py` — pick the optimal envelope band by spectral kurtosis.
