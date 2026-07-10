# P0 seeded-defect bench — shopping list, build, seeding protocol

Goal: a machine we control where known bearing defects can be swapped in within
minutes — the thing P0 Step 2's success criterion is measured on. Everything
below is Karaganda-local (satu.kz / kaspi.kz / OLX / hardware stores), no
imports, buildable **before** the sensor/Teensy arrive so the electronics land
on a ready rig.

## Design: belt-driven shaft in pillow blocks (not grinder surgery)

```
[grinder or motor] --belt--> [pulley]==25mm shaft==[UCP205]======[UCP205]
                                          (drive end)     (TEST bearing)
```

Two UCP205 pillow-block housings carry a 25 mm shaft; the far housing holds the
**test bearing** (UC205 insert). Swapping a seeded bearing = 2 set screws +
2 base bolts, ~5 minutes, no press. Belt tension gives a controllable **radial
load** — critical, because an unloaded bearing whispers; defect impacts need a
loaded zone. The bench grinder drives the belt from a small pulley on its
arbor (wheels removed!) — and doubles as a second, real machine for healthy-
baseline practice; a used washing-machine motor from OLX is the cheaper/
speed-flexible driver alternative.

Why not swap bearings inside the grinder itself: spindle bearing size is
unknown until opened (often 6202–6204, not our 6205), disassembly may need a
puller, and every swap is surgery. Keep that as an opportunistic extra once the
grinder is open for the pulley fitting.

## Shopping list (verified prices, 2026-07-06/10)

| # | Item | Qty | Where | Price est. |
|---|---|---|---|---|
| 1 | **UCP205** pillow block (housing + UC205 insert) | 2 (+1 spare) | [satu.kz](https://satu.kz/Podshipniki-ucp.html) — generic 2 862 ₸, SKF 5 000 ₸ | ~9 000 ₸ |
| 2 | **UC205** insert bearings — the seed stock | 6 | same sellers | ~10–15 000 ₸ |
| 3 | Shaft: 25 mm steel rod, ~400 mm | 1 | any metal supplier («круг 25 мм») | ~3 000 ₸ |
| 4 | Pulleys (small for driver, ~70–100 mm for shaft) + A-profile V-belt | 1 set | hardware / satu.kz | ~5 000 ₸ |
| 5 | **Bench grinder** 150 mm ~2 950 rpm (driver + baseline machine) | 1 | [satu.kz](https://satu.kz/Tochila-nastolnye.html) RODEX from 19 350 ₸ / [OLX used](https://olx.kz/dom-i-sad/instrumenty/q-%D1%82%D0%BE%D1%87%D0%B8%D0%BB%D0%BE) 5–15 000 ₸ | 5–20 000 ₸ |
| 6 | Rotary engraver (Dremel-class) + **diamond burr bits** | 1 | kaspi.kz / market | ~10–20 000 ₸ (skip if owned) |
| 7 | **Loctite 401** 20 g (sensor pads) | 1 | [satu.kz](https://satu.kz/p95562711-loctite-401-20g.html) | ~7 500 ₸ |
| 8 | Laser tachometer DT-2234C+ + reflective tape | 1 | [tomas.kz](https://tomas.kz/k/f-lazernyy-tahometr/) ~14 500 ₸ (AliExpress ~$8 if you can wait) | ~14 500 ₸ |
| 9 | Base plate (thick plywood/steel), M8–M10 bolts, washers | — | hardware store | ~5 000 ₸ |

**Total ≈ 70–95 000 ₸ (~$130–175)** new-everything; **≈ 50–65 000 ₸** with a
used grinder and an owned rotary tool.

## Defect-seeding protocol (per CWRU convention, Dremel version)

Label bearings first: `H1 H2` (healthy, never touched), `OR1 OR2` (outer race),
`IR1` (inner race), `B1` (ball).

1. **Pry the seals** off an insert with a thin screwdriver — they're rubber,
   re-seatable. Degrease is unnecessary at P0.
2. **Outer race (start here — easiest, and the most common real fault):** angle
   a fine diamond burr between two balls onto the outer raceway groove; one
   transverse scratch, ~0.5–1 mm wide, a few tenths deep. That approximates
   CWRU's 0.007″ class.
3. **Inner race:** rotate the inner ring to expose its groove between balls;
   same transverse scratch.
4. **Ball:** hardest to do meaningfully (the spall must be ON the rolling
   surface); grind a small flat/pit on one ball through the gap. Expect — as on
   CWRU data — the weakest signature. That's realism, not failure.
5. Wipe swarf, one drop of fresh grease, seals back on, label the OD with a
   marker.

Keep `H1`/`H2` sacred — they are the baseline and the false-alarm check.

## Safety (2 950 rpm of hardened steel deserves it)

- Grinder as driver: **both wheels off**, guards left on, pulley properly
  keyed/clamped to the arbor, never stand in the belt plane.
- Bolt the base plate down; check set screws after every swap.
- Eye protection when dremeling races (hardened-steel chips) and when prying
  seals.
- First spin-up of any seeded bearing: short bursts, listen before you trust it.

## Measurement plan (the day the electronics arrive)

1. Sensor stud/glued on the **test-bearing housing, load zone, radial**;
   `record_teensy.py --asset bench --rpm <tach>` with UC205 geometry (count
   balls + caliper the races after first seal removal; until then the
   `BPFO≈0.4·n·fr` approximation in `bearing_freqs`' docstring holds).
2. 10+ healthy captures (H1) across a day → baseline; verify `detect()` reads
   healthy and the trend is flat.
3. Swap OR1 → expect **faulted/BPFO**; IR1 → BPFI; B1 → suspect-or-better
   (baseline mode should flag it).
4. Mini run-to-failure: re-dremel OR2 progressively deeper between capture
   sessions → the trend chart from `analysis/trend.py`, on your own hardware.
5. Optional while waiting for electronics: a phone **microphone** WAV
   (44.1 kHz) held near the housing — the pipeline is sample-rate-agnostic and
   gross seeded defects are often audible as an envelope comb. A tiny WAV
   loader script is a 20-minute add if wanted.

Bearing counts after this list: 2 healthy + 4 seeded + 2 fresh inserts in the
working pillow blocks + 1 spare housing — enough for the full P0 matrix.
