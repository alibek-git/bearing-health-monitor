"""Bearing-health detection core: defect frequencies, envelope analysis, features."""

from .bearing import bearing_freqs, fault_lines
from .detect import comb_snr, detect, estimate_slip, harmonic_snr
from .envelope import classify, defect_score, envelope_spectrum, line_score
from .features import crest_factor, kurtosis, rms, velocity_rms_iso
from .kurtogram import pick_band
from .trend import baseline_scores, first_sustained_crossing, trend_ratios

__all__ = [
    "bearing_freqs",
    "fault_lines",
    "envelope_spectrum",
    "defect_score",
    "line_score",
    "classify",
    "detect",
    "comb_snr",
    "estimate_slip",
    "harmonic_snr",
    "pick_band",
    "baseline_scores",
    "trend_ratios",
    "first_sustained_crossing",
    "rms",
    "crest_factor",
    "kurtosis",
    "velocity_rms_iso",
]
