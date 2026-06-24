# scripts

Runnable tools that exercise the `analysis/` core.

## `validate_cwru.py`
Validate the detector on a labeled Case Western Reserve (CWRU) bearing file.

```bash
python scripts/validate_cwru.py data/<file>.mat --fs 12000 --rpm 1772 --plot
```
Prints the bearing defect frequencies, per-element scores, and the likely fault; with
`--plot`, shows the envelope spectrum with BPFO/BPFI/BSF marked. A correctly-labeled
faulted file should rank its matching element first.

## Planned
- `validate_ims.py` — NASA IMS run-to-failure (trend the score over the run to the failure).
- `record_teensy.py` — pull live blocks from the P0 sensor (see `firmware/`) and score them.
- `kurtogram.py` — pick the optimal envelope band by spectral kurtosis.
