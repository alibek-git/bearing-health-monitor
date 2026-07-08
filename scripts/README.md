# scripts

Runnable tools that exercise the `analysis/` core.

## `validate_cwru.py`
Validate the detector on a labeled Case Western Reserve (CWRU) bearing file.

```bash
python scripts/validate_cwru.py data/<file>.mat --fs 12000 --rpm 1772 --plot
# pick the demodulation band automatically (matched kurtogram):
python scripts/validate_cwru.py data/110.mat --fs 48000 --auto-band
# ball faults need the sensitive baseline-relative mode:
python scripts/validate_cwru.py data/119.mat --baseline data/98.mat
```
Prints defect frequencies, per-element scores, comb SNR, and a
`HEALTHY / SUSPECT / FAULTED` verdict with margin; with `--plot`, shows the envelope
spectrum with BPFO/BPFI/BSF marked. `--auto-band` picks the band by matched
spectral kurtosis (`analysis.pick_band`). `--baseline <healthy.mat>` compares
against a healthy capture of the same rig (the product-mode path — required to
catch the smeared combs of ball faults).

## `validate_ims.py`
Trend the detector over a NASA IMS run-to-failure test — the "score rises for
days before failure" demo (and the seed of the RUL model).

```bash
python scripts/validate_ims.py data/ims/2nd_test --channel 0 --plot
```
Scores every ~10-min snapshot (matched band + slip alignment per capture),
trends both comb SNR and score-over-baseline, and prints the first *sustained*
WARN/ALARM crossings with lead time; writes the full per-snapshot trend to CSV.
Validated result on set 2 channel 0 (bearing 1, outer-race death): **sustained
BPFO alarm 2d 12h before failure** (SNR mode), baseline-ratio alarm BPFO 23× at
2d 20h.

## `record_teensy.py`
Capture from the P0 rig (Teensy 4.1 + ADXL1002 running
[`firmware/p0_sampler`](../firmware/p0_sampler/p0_sampler.ino)) and score it
immediately:

```bash
python scripts/record_teensy.py --asset pump7 --seconds 10 --rpm 1480 \
    --bearing 9 7.94 39.04 0     # n_balls ball_dia pitch_dia contact_angle
```
Auto-detects the serial port, verifies frame checksums + sequence continuity
(warns on any host gaps / device drops), saves `data/field/<asset>/<stamp>.npy`
+ sidecar JSON per the field convention, and prints the detector verdict
(band, slip, per-element SNR) when RPM + geometry are given.
