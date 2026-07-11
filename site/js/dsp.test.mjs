/**
 * Tests for the JavaScript port of the bearing detection engine.
 * Run: node --test site/js/dsp.test.mjs
 */

import test from 'node:test';
import assert from 'node:assert/strict';

import {
  bearingFreqs,
  envelopeSpectrum,
  detect,
  pickBand,
  trendRatios,
  firstSustainedCrossing,
} from './dsp.js';
import { MACHINE, makeRng, capture } from './simulator.js';

const FREQS = bearingFreqs(
  MACHINE.rpm,
  MACHINE.geometry.nBalls,
  MACHINE.geometry.ballDia,
  MACHINE.geometry.pitchDia,
);

function relClose(actual, expected, rel) {
  assert.ok(
    Math.abs(actual - expected) <= rel * Math.abs(expected),
    `expected ${actual} within rel ${rel} of ${expected}`,
  );
}

/** Full pipeline: matched band search -> envelope spectrum -> detection. */
function analyze(x) {
  const band = pickBand(x, MACHINE.fs, FREQS);
  const { f, amp } = envelopeSpectrum(x, MACHINE.fs, band);
  return detect(f, amp, FREQS);
}

test('bearingFreqs matches published CWRU 6205 multipliers', () => {
  const fr = MACHINE.rpm / 60.0;
  relClose(FREQS.fr, fr, 1e-12);
  relClose(FREQS.BPFO, 3.5848 * fr, 1e-3);
  relClose(FREQS.BPFI, 5.4152 * fr, 1e-3);
  relClose(FREQS.BSF, 2.3568 * fr, 1e-3);
  relClose(FREQS.FTF, 0.3983 * fr, 1e-3);
});

test('healthy capture -> verdict healthy, max SNR below warn', () => {
  const x = capture('none', 0.0, makeRng(42));
  assert.equal(x.length, MACHINE.n);
  const res = analyze(x);
  assert.equal(res.verdict, 'healthy');
  assert.equal(res.element, null);
  const maxSnr = Math.max(...Object.values(res.snr));
  assert.ok(maxSnr < 4, `healthy max SNR ${maxSnr} should be < 4`);
});

test('outer-race fault -> BPFO named, slip recovered', () => {
  const res = analyze(capture('outer', 0.8, makeRng(7)));
  assert.notEqual(res.verdict, 'healthy');
  assert.equal(res.element, 'BPFO');
  assert.ok(res.snr.BPFO === Math.max(...Object.values(res.snr)));
  assert.ok(
    Math.abs(res.slip - MACHINE.slip) <= 0.012,
    `slip ${res.slip} should be within 0.982 +- 0.012`,
  );
});

test('inner-race fault -> BPFI named', () => {
  const res = analyze(capture('inner', 0.85, makeRng(11)));
  assert.notEqual(res.verdict, 'healthy');
  assert.equal(res.element, 'BPFI');
  assert.ok(res.snr.BPFI === Math.max(...Object.values(res.snr)));
});

test('ball fault -> BSF named', () => {
  const res = analyze(capture('ball', 0.85, makeRng(13)));
  assert.notEqual(res.verdict, 'healthy');
  assert.equal(res.element, 'BSF');
  assert.ok(res.snr.BSF === Math.max(...Object.values(res.snr)));
});

test('trend: sustained ramp in one element is found at run start', () => {
  const flat = () => ({ BPFO: 1.0, BPFI: 1.1, BSF: 0.9, FTF: 1.0 });
  const history = [flat(), flat(), flat(), flat()];
  for (const bpfo of [2.0, 5.0, 8.0, 12.0]) {
    history.push({ ...flat(), BPFO: bpfo });
  }
  const { base, ratios } = trendRatios(history, 4);
  relClose(base.BPFO, 1.0, 1e-12);
  const hit = firstSustainedCrossing(ratios, 4.0, 3);
  assert.equal(hit.element, 'BPFO');
  assert.equal(hit.index, 5); // first capture of the sustained >= 4x run
});

test('trend: a single spike does not page anyone (sustain=3)', () => {
  const flat = () => ({ BPFO: 1.0, BPFI: 1.0, BSF: 1.0, FTF: 1.0 });
  const history = [flat(), flat(), flat(), flat(),
    { ...flat(), BPFO: 10.0 }, flat(), flat(), flat()];
  const { ratios } = trendRatios(history, 4);
  const hit = firstSustainedCrossing(ratios, 4.0, 3);
  assert.equal(hit.index, null);
  assert.equal(hit.element, null);
});
