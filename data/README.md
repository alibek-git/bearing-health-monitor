# data

Local datasets and field recordings. **Everything here except this README is
gitignored** (datasets are large and/or customer-confidential).

## Public datasets for P0 validation
- **CWRU Bearing Data Center** — labeled inner/outer/ball faults, drive-end
  accelerometer, 12 kHz & 48 kHz. The fastest way to prove the detector.
  Place `.mat` files here and run `scripts/validate_cwru.py`.
  Direct URLs: `https://engineering.case.edu/sites/default/files/<n>.mat` —
  the validated 1-hp/1772-rpm set is `98` (normal), `106` (inner 0.007″),
  `119` (ball 0.007″), `131` (outer 0.007″). `tests/test_cwru.py` picks these up
  automatically when present.
- **NASA IMS** — run-to-failure (trend scores from healthy to failure).
- **NASA / FEMTO PRONOSTIA** — accelerated run-to-failure for RUL work.

## Field recordings
Store P0 captures as `field/<asset>/<YYYY-MM-DD>_<rpm>rpm.npy` (or `.wav`/`.csv`) plus a
small sidecar JSON with `fs`, `rpm`, bearing part number + geometry, and operating
notes. Keep customer data out of any shared/public remote.
