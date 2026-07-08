"""Healthy / faulted decision gate.

:func:`analysis.envelope.classify` names the most likely failing element but always
returns *something* — on a healthy machine it just ranks noise. This module adds the
missing decision: is there a defect at all, and with what margin?

Two modes:

- **Baseline-free (screening).** Each element's defect comb is compared against the
  local noise floor of the envelope spectrum itself (harmonic SNR). Self-normalizing,
  so it transfers across machines/sensors/units without tuning. Cleanly catches race
  faults (CWRU: outer 167x, inner 56x vs a healthy ceiling of ~3).
- **Baseline-relative (product mode).** Defect scores are compared against a stored
  healthy capture of the *same* machine. Far more sensitive — it catches the weak,
  smeared comb of a ball fault (CWRU: ~50x over baseline) that baseline-free mode
  cannot. This is the mode the P0 field protocol and product trending use.

Verdicts are three-zone (``healthy`` / ``suspect`` / ``faulted``), mirroring the
alert/alarm levels of condition-monitoring practice.
"""

from __future__ import annotations

import numpy as np

from .bearing import fault_lines
from .envelope import classify

_RANK = {"healthy": 0, "suspect": 1, "faulted": 2}


def comb_snr(f, amp, lines, tol=0.01, floor_span=0.12, robust=True):
    """Energy at a set of expected spectral lines relative to the local noise floor.

    For each line: the peak amplitude within ``+-tol`` (fractional) of it, and the
    median amplitude of a surrounding window (``+-floor_span`` of the line) as the
    local floor. Returns ``sum(peaks) / sum(floors)`` — roughly 1-3 for noise,
    order 10-100 for a real defect comb. Lines beyond the spectrum are skipped.

    ``robust`` drops the single strongest line (when >=2 are evaluable) before
    aggregating: a real fault shows a *distributed* comb and keeps its value (a
    uniform comb is exactly unchanged), while a lone machine tone or noise spike
    coinciding with one expected line collapses toward 1. This is what keeps the
    band-search (:func:`analysis.kurtogram.pick_band`) from manufacturing false
    alarms out of stationary interference.
    """
    f = np.asarray(f, dtype=float)
    amp = np.asarray(amp, dtype=float)
    df = (f[1] - f[0]) if len(f) > 1 else 1.0
    peaks, floors = [], []
    for ft in lines:
        if ft <= 0 or ft >= f[-1]:
            continue
        half = max(tol * ft, df)
        span = max(floor_span * ft, 25 * df)  # guarantee enough floor bins near DC
        pk = np.abs(f - ft) <= half
        fl = (np.abs(f - ft) <= span) & (f > 0)
        if not pk.any() or not fl.any():
            continue
        peaks.append(float(amp[pk].max()))
        floors.append(float(np.median(amp[fl])))
    if not peaks:
        return 0.0
    if robust and len(peaks) >= 2:
        i = int(np.argmax(peaks))
        peaks.pop(i)
        floors.pop(i)
    return float(sum(peaks) / max(sum(floors), 1e-30))


def harmonic_snr(f, amp, target, n_harmonics=4, tol=0.01, floor_span=0.12):
    """:func:`comb_snr` over a plain harmonic series of ``target``."""
    return comb_snr(f, amp, [target * h for h in range(1, n_harmonics + 1)],
                    tol, floor_span)


def estimate_slip(f, amp, freqs, n_harmonics=4, span=(0.96, 1.005), step=0.0025):
    """Global slip factor that best aligns the expected combs with the spectrum.

    Rolling elements slip: under heavy load the cage runs a few percent below its
    kinematic speed, dragging every defect frequency down with it (IMS set 2:
    BPFO sits 2.5% under nominal). A fixed ±1% line window then misses the real
    comb entirely. This scans one *shared* scale factor over all elements and
    returns the value maximizing the strongest element's robust comb SNR — one
    global parameter, so it cannot invent an element that isn't there.
    """
    best_s, best = 1.0, -np.inf
    s = span[0]
    while s <= span[1] + 1e-9:
        scaled = {k: v * s for k, v in freqs.items()}
        score = max(comb_snr(f, amp, lines)
                    for lines in fault_lines(scaled, n_harmonics).values())
        if score > best:
            best_s, best = s, score
        s += step
    return best_s


def _zone(value, warn, alarm):
    return "faulted" if value > alarm else "suspect" if value > warn else "healthy"


def detect(f, amp, freqs, n_harmonics=4, warn=4.0, alarm=10.0,
           baseline=None, warn_ratio=4.0, alarm_ratio=10.0, slip="auto"):
    """Decide healthy / suspect / faulted; name the element when not healthy.

    ``freqs`` is the dict from :func:`analysis.bearing.bearing_freqs`. ``baseline``,
    if given, is the ``classify(...)`` score dict from a healthy capture of the same
    machine; the verdict is then the more severe of the two modes. ``slip="auto"``
    (default) first aligns the expected combs to the spectrum with one global
    slip factor (see :func:`estimate_slip`); pass ``slip=None`` or a number to
    disable/pin it.

    Thresholds (``warn``/``alarm`` on harmonic SNR, ``warn_ratio``/``alarm_ratio``
    on score-over-baseline) are calibrated on CWRU: healthy tops out ~3.3, race
    faults reach 56-167. Tune conservatively per fleet; trends beat absolutes.

    Raises ``ValueError`` instead of guessing when the verdict would be built on
    no evidence: a non-finite spectrum (dropped samples / sensor glitch), every
    defect frequency outside the spectrum (wrong fs/rpm/geometry), or a baseline
    with missing or non-positive scores. A loud failure beats a silent
    false-healthy on a safety gate.

    Returns a dict:
      verdict  - "healthy" | "suspect" | "faulted"
      element  - failing element ("BPFO"/"BPFI"/"BSF"/"FTF"), None when healthy
      margin   - top statistic / its alarm threshold (>=1 means alarm-level)
      snr      - per-element comb SNR over its physics-informed line set
                 (baseline-free evidence; see analysis.bearing.fault_lines)
      scores   - per-element defect scores (``classify`` output)
      ratios   - per-element score / baseline score, or None without a baseline
    """
    amp = np.asarray(amp, dtype=float)
    if not np.all(np.isfinite(amp)):
        raise ValueError("envelope spectrum contains non-finite values — reject the capture")

    if slip == "auto":
        slip = estimate_slip(f, amp, freqs, n_harmonics)
    freqs = {k: v * (slip or 1.0) for k, v in freqs.items()}

    snr = {k: comb_snr(f, amp, lines)
           for k, lines in fault_lines(freqs, n_harmonics).items()}
    if all(v == 0.0 for v in snr.values()):
        raise ValueError("no defect frequency falls inside the spectrum — check fs/rpm/geometry")
    scores = classify(f, amp, freqs, n_harmonics)
    ratios = None

    element = max(snr, key=snr.get)
    verdict = _zone(snr[element], warn, alarm)
    margin = snr[element] / alarm

    if baseline is not None:
        bad = [k for k in scores if not baseline.get(k, 0.0) > 0.0]
        if bad:
            raise ValueError(f"baseline is missing or non-positive for {bad} — "
                             "pass the classify() scores of a healthy capture")
        ratios = {k: scores[k] / baseline[k] for k in scores}
        top = max(ratios, key=ratios.get)
        v = _zone(ratios[top], warn_ratio, alarm_ratio)
        if _RANK[v] > _RANK[verdict]:
            verdict, element, margin = v, top, ratios[top] / alarm_ratio

    if verdict == "healthy":
        element = None
    return {"verdict": verdict, "element": element, "margin": margin,
            "snr": snr, "scores": scores, "ratios": ratios, "slip": slip}
