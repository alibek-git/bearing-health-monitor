/**
 * Synthetic bearing-vibration source for the demo dashboard — JavaScript
 * port of demo/simulator.py at n=16384 / fs=25600 (0.64 s captures).
 *
 * Physics-faithful captures: broadband noise + shaft harmonics, plus a
 * fault-specific impact train ringing a structural resonance:
 * - outer race: impacts at BPFO, constant amplitude
 * - inner race: impacts at BPFI, amplitude-modulated at shaft rate
 * - ball: impacts at 2xBSF, modulated at cage (FTF) rate
 * The train runs at 0.982x kinematic frequency (cage slip), so the demo
 * exercises the detector's slip alignment.
 */

import { bearingFreqs } from './dsp.js';

// Demo machine: a 1480-rpm pump motor with the CWRU-class 6205 bearing.
export const MACHINE = {
  rpm: 1480,
  fs: 25600,
  n: 16384,
  geometry: { nBalls: 9, ballDia: 7.94, pitchDia: 39.04 },
  slip: 0.982, // true cage slip of the simulated machine (detector must find it)
};

const RESONANCE_HZ = 3400.0;
const RING_TAU = 0.0009;

const FREQS = bearingFreqs(
  MACHINE.rpm,
  MACHINE.geometry.nBalls,
  MACHINE.geometry.ballDia,
  MACHINE.geometry.pitchDia,
);

/** Deterministic mulberry32 PRNG; returns () => float in [0, 1). */
export function makeRng(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Standard normal via Box-Muller from a [0,1) uniform source. */
function gauss(rng) {
  const u = 1.0 - rng(); // (0, 1] — avoids log(0)
  const v = rng();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/**
 * Decaying-resonance impacts every 1/rate seconds added into x; per-impact
 * amplitude taken from ampOfT evaluated at the impact instant.
 */
function addImpactTrain(x, fs, rate, ampOfT) {
  const n = x.length;
  const tLast = (n - 1) / fs;
  const nImpacts = Math.floor(tLast * rate) + 1;
  const dur = 12 * RING_TAU;
  for (let k = 0; k < nImpacts; k++) {
    const t0 = k / rate;
    const a = ampOfT(t0);
    for (let i = Math.max(0, Math.ceil(t0 * fs)); i < n; i++) {
      const d = i / fs - t0;
      if (d < 0) continue;
      if (d >= dur) break;
      x[i] += a * Math.exp(-d / RING_TAU) * Math.sin(2 * Math.PI * RESONANCE_HZ * d);
    }
  }
}

/**
 * One capture of MACHINE.n samples at MACHINE.fs (Float64Array, arbitrary
 * g-ish units). fault is 'none' | 'outer' | 'inner' | 'ball'; severity 0..1
 * scales the impact energy (past ~0.7 the broadband floor rises too).
 */
export function capture(fault = 'none', severity = 0.0, rng = makeRng(1)) {
  const { fs, n } = MACHINE;
  const fr = FREQS.fr;

  const x = new Float64Array(n);
  const noiseAmp = 0.30 * (1.0 + 2.0 * Math.max(0.0, severity - 0.7));
  for (let i = 0; i < n; i++) {
    const t = i / fs;
    x[i] = noiseAmp * gauss(rng)
      + 0.25 * Math.sin(2 * Math.PI * fr * t)
      + 0.10 * Math.sin(2 * Math.PI * 2 * fr * t + 1.0);
  }
  if (fault === 'none' || severity <= 0.0) return x;

  const amp = 1.6 * severity;
  const jitter = () => 1.0 + 0.15 * (rng() - 0.5); // +-7.5% impact-to-impact spread

  if (fault === 'outer') {
    const rate = FREQS.BPFO * MACHINE.slip;
    addImpactTrain(x, fs, rate, () => amp * jitter());
  } else if (fault === 'inner') {
    const rate = FREQS.BPFI * MACHINE.slip;
    addImpactTrain(x, fs, rate, (t0) => amp * jitter()
      * (0.4 + 0.6 * 0.5 * (1 + Math.sin(2 * Math.PI * fr * t0))));
  } else if (fault === 'ball') {
    const rate = 2.0 * FREQS.BSF * MACHINE.slip;
    const ftf = FREQS.FTF * MACHINE.slip;
    addImpactTrain(x, fs, rate, (t0) => amp * jitter()
      * (0.3 + 0.7 * Math.abs(Math.cos(2 * Math.PI * ftf * t0))));
  } else {
    throw new Error(`unknown fault '${fault}'`);
  }
  return x;
}
