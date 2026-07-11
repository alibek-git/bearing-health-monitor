/**
 * Bearing fault-detection engine — JavaScript port of the Python reference
 * implementation in analysis/ (bearing.py, envelope.py, detect.py,
 * kurtogram.py, trend.py).
 *
 * ES module, zero dependencies, runnable in browser and node.
 *
 * The one deliberate departure from the Python code: instead of
 * butter+sosfiltfilt+hilbert+welch, the envelope spectrum is computed with an
 * FFT method — band-limited analytic signal by spectral masking, magnitude
 * envelope, Hann window, second FFT. This keeps the module dependency-free
 * while preserving the detector semantics (comb SNR against a local floor).
 */

// ---------------------------------------------------------------------------
// FFT: iterative radix-2 complex, in-place. Power-of-2 lengths only.
// ---------------------------------------------------------------------------

function assertPow2(n) {
  if (n < 2 || (n & (n - 1)) !== 0) {
    throw new Error(`FFT length must be a power of 2, got ${n}`);
  }
}

/** In-place forward FFT of the complex signal (re, im). */
export function fft(re, im) {
  const n = re.length;
  assertPow2(n);
  // bit-reversal permutation
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      let t = re[i]; re[i] = re[j]; re[j] = t;
      t = im[i]; im[i] = im[j]; im[j] = t;
    }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const half = len >> 1;
    const ang = -2 * Math.PI / len;
    const wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1.0, ci = 0.0;
      for (let j = 0; j < half; j++) {
        const a = i + j, b = a + half;
        const vr = re[b] * cr - im[b] * ci;
        const vi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - vr; im[b] = im[a] - vi;
        re[a] += vr; im[a] += vi;
        const nr = cr * wr - ci * wi;
        ci = cr * wi + ci * wr;
        cr = nr;
      }
    }
  }
}

/** In-place inverse FFT (conjugate trick, 1/n normalized). */
export function ifft(re, im) {
  const n = re.length;
  for (let i = 0; i < n; i++) im[i] = -im[i];
  fft(re, im);
  for (let i = 0; i < n; i++) {
    re[i] /= n;
    im[i] = -im[i] / n;
  }
}

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

function median(values) {
  const a = Array.from(values).sort((p, q) => p - q);
  const n = a.length;
  if (n === 0) return NaN;
  const m = n >> 1;
  return n % 2 ? a[m] : 0.5 * (a[m - 1] + a[m]);
}

function scaleFreqs(freqs, s) {
  const out = {};
  for (const k of Object.keys(freqs)) out[k] = freqs[k] * s;
  return out;
}

// ---------------------------------------------------------------------------
// Bearing characteristic frequencies (port of analysis/bearing.py)
// ---------------------------------------------------------------------------

/**
 * Characteristic defect frequencies (Hz) for a rolling-element bearing.
 * ballDia and pitchDia must share units (mm or in).
 * Returns {fr, FTF, BPFO, BPFI, BSF}.
 */
export function bearingFreqs(rpm, nBalls, ballDia, pitchDia, contactAngleDeg = 0) {
  const fr = rpm / 60.0;
  const r = (ballDia / pitchDia) * Math.cos(contactAngleDeg * Math.PI / 180.0);
  return {
    fr,
    FTF: 0.5 * fr * (1 - r),
    BPFO: (nBalls / 2.0) * fr * (1 - r),
    BPFI: (nBalls / 2.0) * fr * (1 + r),
    BSF: (pitchDia / (2.0 * ballDia)) * fr * (1 - r * r),
  };
}

/**
 * Expected envelope-spectrum lines per element, encoding the modulation
 * physics: BPFO plain harmonics; BPFI harmonics with +-fr sidebands;
 * BSF harmonics of 2xBSF with +-FTF sidebands; FTF plain harmonics.
 * Returns {BPFO:[...], BPFI:[...], BSF:[...], FTF:[...]}.
 */
export function faultLines(freqs, nHarmonics = 4, nSidebands = 1) {
  const fr = freqs.fr, ftf = freqs.FTF;

  const comb = (center, spacing) => {
    const lines = [];
    for (let h = 1; h <= nHarmonics; h++) {
      const c = h * center;
      lines.push(c);
      for (let k = 1; k <= nSidebands; k++) {
        lines.push(c - k * spacing, c + k * spacing);
      }
    }
    return lines.filter((x) => x > 0);
  };

  const bpfo = [];
  const ftfLines = [];
  for (let h = 1; h <= nHarmonics; h++) {
    bpfo.push(h * freqs.BPFO);
    ftfLines.push(h * ftf);
  }
  return {
    BPFO: bpfo,
    BPFI: comb(freqs.BPFI, fr),
    BSF: comb(2.0 * freqs.BSF, ftf),
    FTF: ftfLines,
  };
}

// ---------------------------------------------------------------------------
// Envelope spectrum (FFT method — see module docstring)
// ---------------------------------------------------------------------------

/**
 * Envelope spectrum from an already-computed forward FFT (Xre, Xim) of the
 * mean-removed signal. Builds the band-limited analytic signal by spectral
 * masking, takes the magnitude envelope, mean-removes, Hann-windows, and
 * FFTs again. Returns {f, amp} over the first n/2 bins.
 * Does not modify Xre/Xim.
 */
function envelopeSpectrumFromFFT(Xre, Xim, fs, band) {
  const n = Xre.length;
  const df = fs / n;
  const lo = band ? band[0] : -Infinity;
  const hi = band ? band[1] : Infinity;
  const Yre = new Float64Array(n);
  const Yim = new Float64Array(n);

  // Analytic signal: zero negative-frequency bins and out-of-band positive
  // bins; double the kept positive bins; DC and Nyquist kept unscaled.
  if (!band) { Yre[0] = Xre[0]; Yim[0] = Xim[0]; }
  const nHalf = n >> 1;
  for (let k = 1; k < nHalf; k++) {
    const fk = k * df;
    if (fk >= lo && fk <= hi) {
      Yre[k] = 2 * Xre[k];
      Yim[k] = 2 * Xim[k];
    }
  }
  const fNyq = nHalf * df;
  if (fNyq >= lo && fNyq <= hi) { Yre[nHalf] = Xre[nHalf]; Yim[nHalf] = Xim[nHalf]; }

  ifft(Yre, Yim);

  // envelope = |analytic|, mean-removed, Hann-windowed
  const env = new Float64Array(n);
  let mean = 0.0;
  for (let i = 0; i < n; i++) {
    env[i] = Math.sqrt(Yre[i] * Yre[i] + Yim[i] * Yim[i]);
    mean += env[i];
  }
  mean /= n;
  const twoPiOverN = 2 * Math.PI / n;
  for (let i = 0; i < n; i++) {
    Yre[i] = (env[i] - mean) * 0.5 * (1 - Math.cos(twoPiOverN * i));
    Yim[i] = 0.0;
  }

  fft(Yre, Yim);

  const f = new Float64Array(nHalf);
  const amp = new Float64Array(nHalf);
  for (let k = 0; k < nHalf; k++) {
    f[k] = k * df;
    amp[k] = Math.sqrt(Yre[k] * Yre[k] + Yim[k] * Yim[k]) / n;
  }
  return { f, amp };
}

/**
 * Band-limit the resonance band, demodulate (analytic-signal envelope),
 * return the envelope spectrum. band is [lo, hi] Hz or null to keep all
 * positive frequencies. Returns {f, amp} (Float64Arrays, first n/2 bins).
 */
export function envelopeSpectrum(x, fs, band) {
  const n = x.length;
  assertPow2(n);
  let mean = 0.0;
  for (let i = 0; i < n; i++) mean += x[i];
  mean /= n;
  const Xre = new Float64Array(n);
  const Xim = new Float64Array(n);
  for (let i = 0; i < n; i++) Xre[i] = x[i] - mean;
  fft(Xre, Xim);
  return envelopeSpectrumFromFFT(Xre, Xim, fs, band);
}

// ---------------------------------------------------------------------------
// Comb SNR + line scores (port of analysis/detect.py comb_snr,
// analysis/envelope.py line_score / classify)
// ---------------------------------------------------------------------------

/**
 * Energy at a set of expected spectral lines relative to the local noise
 * floor. Per line: peak amplitude within +-max(tol*ft, df); floor = median
 * amplitude within +-max(floorSpan*ft, 25*df) (f > 0 only). Lines beyond
 * the spectrum are skipped. robust drops the single strongest line (when
 * >= 2 are evaluable). Returns sum(peaks)/max(sum(floors), 1e-30), 0 if no
 * lines are evaluable.
 */
export function combSnr(f, amp, lines, tol = 0.01, floorSpan = 0.12, robust = true) {
  const n = f.length;
  const df = n > 1 ? f[1] - f[0] : 1.0;
  const fLast = f[n - 1];
  const peaks = [];
  const floors = [];
  for (const ft of lines) {
    if (ft <= 0 || ft >= fLast) continue;
    const half = Math.max(tol * ft, df);
    const span = Math.max(floorSpan * ft, 25 * df);
    const iLo = Math.max(0, Math.floor((ft - span) / df) - 1);
    const iHi = Math.min(n - 1, Math.ceil((ft + span) / df) + 1);
    let pk = -Infinity;
    const fl = [];
    for (let i = iLo; i <= iHi; i++) {
      const d = Math.abs(f[i] - ft);
      if (d <= span && f[i] > 0) fl.push(amp[i]);
      if (d <= half && amp[i] > pk) pk = amp[i];
    }
    if (pk === -Infinity || fl.length === 0) continue;
    peaks.push(pk);
    floors.push(median(fl));
  }
  if (peaks.length === 0) return 0.0;
  if (robust && peaks.length >= 2) {
    let iMax = 0;
    for (let i = 1; i < peaks.length; i++) if (peaks[i] > peaks[iMax]) iMax = i;
    peaks.splice(iMax, 1);
    floors.splice(iMax, 1);
  }
  let sp = 0.0, sf = 0.0;
  for (const p of peaks) sp += p;
  for (const q of floors) sf += q;
  return sp / Math.max(sf, 1e-30);
}

/** Summed envelope amplitude at a list of expected spectral lines (Hz). */
export function lineScore(f, amp, lines, tol = 0.01) {
  const n = f.length;
  const df = n > 1 ? f[1] - f[0] : 1.0;
  let s = 0.0;
  for (const ft of lines) {
    const half = Math.max(tol * ft, df);
    const iLo = Math.max(0, Math.floor((ft - half) / df) - 1);
    const iHi = Math.min(n - 1, Math.ceil((ft + half) / df) + 1);
    let pk = -Infinity;
    for (let i = iLo; i <= iHi; i++) {
      if (Math.abs(f[i] - ft) <= half && amp[i] > pk) pk = amp[i];
    }
    if (pk !== -Infinity) s += pk;
  }
  return s;
}

/**
 * Per-element defect scores (port of analysis/envelope.py classify):
 * lineScore summed over each element's physics-informed line set.
 */
export function classify(f, amp, freqs, nHarmonics = 4) {
  const lines = faultLines(freqs, nHarmonics);
  const out = {};
  for (const k of Object.keys(lines)) out[k] = lineScore(f, amp, lines[k]);
  return out;
}

// ---------------------------------------------------------------------------
// Slip estimation + detection gate (port of analysis/detect.py)
// ---------------------------------------------------------------------------

/**
 * Global slip factor that best aligns the expected combs with the spectrum.
 * Scans one shared scale factor over all elements (span 0.96..1.005,
 * step 0.0025) and returns the value maximizing the strongest element's
 * robust comb SNR.
 */
export function estimateSlip(f, amp, freqs, nHarmonics = 4,
                             span = [0.96, 1.005], step = 0.0025) {
  let bestS = 1.0;
  let best = -Infinity;
  let s = span[0];
  while (s <= span[1] + 1e-9) {
    const lines = faultLines(scaleFreqs(freqs, s), nHarmonics);
    let score = -Infinity;
    for (const k of Object.keys(lines)) {
      const v = combSnr(f, amp, lines[k]);
      if (v > score) score = v;
    }
    if (score > best) { bestS = s; best = score; }
    s += step;
  }
  return bestS;
}

const RANK = { healthy: 0, suspect: 1, faulted: 2 };

function zone(value, warn, alarm) {
  return value > alarm ? 'faulted' : value > warn ? 'suspect' : 'healthy';
}

/**
 * Decide healthy / suspect / faulted; name the element when not healthy.
 * freqs is the dict from bearingFreqs(). Slip is auto-estimated. Thresholds:
 * warn=4, alarm=10 on comb SNR (strict > comparisons). Throws on a
 * non-finite spectrum or when no defect frequency falls inside the spectrum.
 * Returns {verdict, element, margin, snr, scores, slip}.
 */
export function detect(f, amp, freqs, nHarmonics = 4, warn = 4.0, alarm = 10.0) {
  for (let i = 0; i < amp.length; i++) {
    if (!Number.isFinite(amp[i])) {
      throw new Error('envelope spectrum contains non-finite values — reject the capture');
    }
  }

  const slip = estimateSlip(f, amp, freqs, nHarmonics);
  const scaled = scaleFreqs(freqs, slip);

  const lines = faultLines(scaled, nHarmonics);
  const snr = {};
  for (const k of Object.keys(lines)) snr[k] = combSnr(f, amp, lines[k]);
  if (Object.values(snr).every((v) => v === 0.0)) {
    throw new Error('no defect frequency falls inside the spectrum — check fs/rpm/geometry');
  }
  const scores = classify(f, amp, scaled, nHarmonics);

  let element = null;
  for (const k of Object.keys(snr)) {
    if (element === null || snr[k] > snr[element]) element = k;
  }
  const verdict = zone(snr[element], warn, alarm);
  const margin = snr[element] / alarm;

  if (verdict === 'healthy') element = null;
  return { verdict, element, margin, snr, scores, slip };
}

// ---------------------------------------------------------------------------
// Demodulation band selection (port of analysis/kurtogram.py, matched
// criterion only)
// ---------------------------------------------------------------------------

/**
 * Overlapping candidate bands between fLo and ~0.45*fs: quarter-octave
 * spaced centers, relative widths 1/3, 2/3, 1; min width 200 Hz.
 */
export function bandGrid(fs, fLo = 500.0, widths = [1 / 3, 2 / 3, 1.0]) {
  const fHi = 0.45 * fs;
  const bands = [];
  let c = fLo * 1.5;
  while (c < fHi) {
    for (const w of widths) {
      const lo = c - c * w / 2.0;
      const hi = c + c * w / 2.0;
      if (lo >= fLo * 0.5 && hi <= fHi && hi - lo >= 200.0) {
        bands.push([Math.round(lo * 10) / 10, Math.round(hi * 10) / 10]);
      }
    }
    c *= Math.pow(2, 0.25);
  }
  return bands;
}

/**
 * Return [lo, hi] of the best demodulation band (matched criterion: the
 * band whose envelope spectrum shows the strongest defect-line comb, max
 * over slips 1.0/0.99/0.975/0.96 and elements of combSnr). Reuses one
 * forward FFT of x; each candidate band is evaluated by masking bins.
 */
export function pickBand(x, fs, freqs, fLo = 500.0) {
  const n = x.length;
  assertPow2(n);
  let mean = 0.0;
  for (let i = 0; i < n; i++) mean += x[i];
  mean /= n;
  const Xre = new Float64Array(n);
  const Xim = new Float64Array(n);
  for (let i = 0; i < n; i++) Xre[i] = x[i] - mean;
  fft(Xre, Xim);

  const slips = [1.0, 0.99, 0.975, 0.96]; // coarse; detect() refines afterwards
  const lineSets = slips.map((s) => faultLines(scaleFreqs(freqs, s)));

  let best = null;
  let bestScore = -Infinity;
  for (const band of bandGrid(fs, fLo)) {
    const { f, amp } = envelopeSpectrumFromFFT(Xre, Xim, fs, band);
    let score = -Infinity;
    for (const lines of lineSets) {
      for (const k of Object.keys(lines)) {
        const v = combSnr(f, amp, lines[k]);
        if (v > score) score = v;
      }
    }
    if (score > bestScore) { best = band; bestScore = score; }
  }
  return best;
}

// ---------------------------------------------------------------------------
// Trending (port of analysis/trend.py)
// ---------------------------------------------------------------------------

/**
 * Element-wise median of the first nBaseline score dicts.
 */
export function baselineScores(history, nBaseline) {
  if (history.length < nBaseline) {
    throw new Error(`need >= ${nBaseline} captures for a baseline, got ${history.length}`);
  }
  const base = {};
  for (const k of Object.keys(history[0])) {
    base[k] = median(history.slice(0, nBaseline).map((h) => h[k]));
  }
  return base;
}

/**
 * Score-over-baseline ratio per element for every capture in history.
 * Returns {base, ratios} where ratios is a list of dicts aligned with
 * history.
 */
export function trendRatios(history, nBaseline) {
  const base = baselineScores(history, nBaseline);
  const ratios = history.map((h) => {
    const r = {};
    for (const k of Object.keys(base)) r[k] = h[k] / Math.max(base[k], 1e-30);
    return r;
  });
  return { base, ratios };
}

/**
 * Index and element of the first ratio >= threshold held for sustain
 * consecutive captures. Returns {index, element} ({index: null,
 * element: null} when never sustained). The index is the first capture of
 * the sustained run; ties resolve to the earliest crossing.
 */
export function firstSustainedCrossing(ratios, threshold, sustain = 3) {
  const keys = ratios.length ? Object.keys(ratios[0]) : [];
  let bestIndex = null;
  let bestElement = null;
  for (const k of keys) {
    let run = 0;
    for (let i = 0; i < ratios.length; i++) {
      run = ratios[i][k] >= threshold ? run + 1 : 0;
      if (run >= sustain) {
        const start = i - sustain + 1;
        if (bestIndex === null || start < bestIndex) {
          bestIndex = start;
          bestElement = k;
        }
        break;
      }
    }
  }
  return { index: bestIndex, element: bestElement };
}
