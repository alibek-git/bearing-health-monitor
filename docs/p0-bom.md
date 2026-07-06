# P0 Test-Rig BOM — components, suppliers, prices, shipping to Kazakhstan

Shopping list for the P0 rig ([business-plan.md](business-plan.md) Step 2 +
[firmware/README.md](../firmware/README.md)) and the seeded-defect test bench.
Delivery target: **Karaganda, KZ**.

Prices spot-checked **2026-07-06** (web research). **✓** = seen on a live
page/snippet that day; **~** = estimate, verify before ordering. Customs note:
single orders above the EAEU personal-import threshold (~€200) may incur
duty/VAT on top of the prices below.

## Ordering strategy (TL;DR)

| Batch | Contents | Lead time |
|---|---|---|
| **1 — Digi-Key order** (one consolidated cart) | sensor eval board, Teensy 4.1, headers | ~3–7 business days (DHL/FedEx) + customs |
| **2 — Local Karaganda / KZ marketplaces** (satu.kz, kaspi.kz, tomas.kz, OLX) | test bearings, bench grinder, Loctite, tachometer, USB cable | same day – 5 days |
| **3 — AliExpress batch** (cheap, slow — order day 1) | magnet base, coax + BNC, spare reflective tape | ~10–25 days |

Batches 1+2 alone are enough to start; batch 3 items have local or bundled
substitutes.

## 1. Core rig (required)

| Component | Pick | Supplier | Price | Ships to KZ | Notes |
|---|---|---|---|---|---|
| Vibration sensor | **EVAL-ADXL1002Z** (±50 g, flat to ~11 kHz, analog out, 25 µg/√Hz) | [Digi-Key](https://www.digikey.com/en/products/detail/analog-devices-inc/EVAL-ADXL1002Z/7200822) | **$106.50 ✓** | DHL/FedEx ~3–7 bd, ~$25–50 ~ | In stock. Alternates: [Arrow](https://www.arrow.com/en/products/eval-adxl1002z/analog-devices) $88.77 ✓ (KZ checkout unverified), Mouser ~$100–110 ~ |
| — budget sensor option | EVAL-ADXL1005Z (±100 g, flat to ~23 kHz, 75 µg/√Hz — noisier, fine for seeded defects) | [Digi-Key](https://www.digikey.com/en/products/detail/analog-devices-inc/EVAL-ADXL1005Z/9648380) | $57.76 ✓ | same order | Halves the sensor cost if the noise floor is acceptable |
| ADC / MCU | **Teensy 4.1** (600 MHz, samples ≥51.2 kSPS, streams USB) | [Digi-Key](https://www.digikey.com/en/products/detail/sparkfun-electronics/DEV-16771/12180099) | **$37.20 ✓** | same order | ⚠ SparkFun (now sole manufacturer, $31.50) shows **backorder**; Digi-Key had stock. ⚠ **Never AliExpress** — $2–15 "Teensy" listings are documented counterfeits that die under vibration |
| Pin headers | 2×24-pin 2.54 mm breakaway strips | add to Digi-Key cart | ~$2 ~ | rides along | Or buy the pins-presoldered Teensy (~$46) |
| USB data cable | micro-B, short (<1 m) | local phone/electronics shop | ~$3 ~ | same day | Must be a *data* cable, not charge-only |
| RPM measurement | **DT-2234C+ laser tachometer** + reflective tape | [AliExpress](https://www.aliexpress.com/w/wholesale-DT-2234C.html) $5–17 ✓ or [tomas.kz](https://tomas.kz/k/f-lazernyy-tahometr/) ~$27 ✓ | $5–27 | Ali ~10–25 d / local 2–5 d | Local costs ~2× but arrives in days |
| Mounting — rigid | Stud (bundled with sensor board) + **Loctite 401** 20 g for glued pads | [satu.kz](https://satu.kz/p95562711-loctite-401-20g.html) | ~$14–15 ✓ (≈7 500–8 000 ₸) | domestic 2–5 d | Stud/adhesive is the only mounting flat to 10+ kHz |
| Mounting — scanning | Rubber-coated neodymium pot magnet, M6 thread | eBay / [protool.kz](https://protool.kz) | $5–15 ~ | local days / eBay 2–4 wk | Magnet mounts roll off ~2 kHz — demo/scanning only. Pro 2-pole bases ($135–150 ✓, [Motionics](https://store.motionics.com/products/two-pole-rare-earth-accelerometer-magnetic-base)/[STI](https://www.stiweb.com/Magnetic-Bases-s/142.htm)) not needed for P0 |
| Signal cable | RG174 coax (50 Ω) + BNC crimp/solder connectors, few m | [eBay assembled](https://www.ebay.com/itm/165709625074) from $7.98 ✓ / AliExpress bulk $8–15 ~ | ~$10–20 | 2–4 wk | Local fallback: shielded microphone cable ~$1/m from any KZ electronics shop |

**Core subtotal ≈ $185–235** ($135–185 with the ADXL1005Z option), incl. ~$30–50 shipping.

## 2. Seeded-defect test bench (required for Step-2 validation)

Buy locally — cheapest *and* fastest.

| Component | Pick | Supplier | Price | Lead time | Notes |
|---|---|---|---|---|---|
| Test bearings ×8–10 | **6205-2RS** GPZ/SPZ (the CWRU test bearing, 25×52×15 mm) | [satu.kz Karaganda sellers](https://satu.kz/karaganda/Podshipnik-6205-2rs-skf;15.html) | **~$2.20/pc ✓** (≈1 158 ₸) | pickup / 1–3 d | Keep 2 healthy as baseline; seed Dremel/EDM defects (outer race, inner race, ball) in the rest |
| Baseline pair | 6205-2RS **SKF** (brand, known-good) | satu.kz | ~$12.70/pc ✓ | 2–5 d | Beware counterfeits at too-low prices |
| Drive | **Bench grinder** 125–150 mm, ~2 950 rpm (RODEX/ZUBR class) | [satu.kz](https://satu.kz/Tochila-nastolnye.html) / kaspi.kz | **$36–60 ✓** | 2–5 d (kaspi often next-day) | Motor + rigid housing + two accessible spindle bearings in one purchase; 2 950 rpm ≈ CWRU speeds |
| — cheaper drive | Used grinder/motor («точило б/у») | [OLX.kz Karaganda](https://olx.kz/dom-i-sad/instrumenty/q-%D1%82%D0%BE%D1%87%D0%B8%D0%BB%D0%BE) | $10–30 ~ | same day | Or RS775 DC motor ($2–5 ✓ AliExpress) + PSU — fallback, needs shaft adapter |
| Defect seeding | Dremel-type engraver + diamond bit (if not owned) | local / kaspi.kz | ~$15–30 ~ | days | A scratch across the outer race is the classic seeded fault |

**Bench subtotal ≈ $85–150.**

## 3. Optional — IEPE/ICP higher-fidelity fallback chain

Order **only if** MEMS results are marginal (the spec's escalation path). All
items `required: false`.

| Component | Pick | Supplier | Price | Ships to KZ | Notes |
|---|---|---|---|---|---|
| Industrial accelerometer | **IMI/PCB 603C01** (100 mV/g, 0.5 Hz–10 kHz, 2-pin MIL) | [Radwell](https://www.radwell.com/Buy/IMI/IMI/603C01) | **$152.20 ✓** new ($76 refurb) | courier ~5–10 bd ~, confirm KZ at checkout (or their EU branch) | Alternates: CTC AC102-1A $199.50 ✓ ([Radwell](https://www.radwell.com/en-US/Buy/CTC%20VIBRATION/CTC%20VIBRATION/AC102-1A/)); AliExpress CT1005LC-class $150–300 ✓ (needs back-to-back calibration check) |
| IEPE conditioner | 4 mA constant-current module (24 V, BNC) | [AliExpress](https://www.aliexpress.com/item/1005003266308099.html) | **$60 ✓** (eBay class $30–50 ~) | ~10–25 d | Brand units (Pico TA487 £199 ✓, PCB 480E09 ~$415) are overkill for P0; worst case DIY from LM334 + 24 V boost for a few $ |
| Sensor cable | Generic 2-pin MIL-C-5015 → BNC harness, 3–5 m | eBay/AliExpress China sellers | $20–40 ~ | 2–4 wk | Must match sensor connector (603C01/AC102 = 2-pin MIL; PCB 352-class = 10-32 coax) |

**IEPE subtotal ≈ $230–290** (+ shipping/customs).

## 4. Skip for P0 (researched, rejected)

- **Digilent Analog Discovery 3** — $379 ✓ ([Digi-Key](https://www.digikey.com/en/products/detail/digilent-inc/410-415/19235661)): replaces all Teensy firmware work at ~10× the cost; Digilent direct now requires an End-Use Statement for KZ — if ever needed, buy via Digi-Key. ADALM2000 (~$262 ~) same story, rougher tooling.
- **ST STEVAL-MKI208V1K** (IIS3DWB) — $32.45 ✓: tempting price but flat only to ~6.3 kHz, ±16 g max, fixed 26.7 kHz digital ODR — loses the resonance band the envelope method exploits and reworks the whole sampling design.
- **Pro magnetic bases** ($135–150) and **imported mounting studs** — the bundled stud + local Loctite + a $10 pot magnet cover P0.

## Budget summary

| Scenario | Total |
|---|---|
| Core rig + bench (recommended start) | **≈ $270–385** |
| — with budget sensor (ADXL1005Z) | ≈ $220–335 |
| + IEPE fallback chain (only if needed) | + $230–290 |

> The plan's "~$150" figure covered the sensor + MCU at pre-2026 prices; the
> ADXL1002 eval board alone is now ~$106. The full working setup including the
> seeded-defect bench lands at ~$300 — still firmly in P0 territory.

## Re-verification checklist before ordering

1. Digi-Key cart: confirm KZ address accepted + shipping quote (est. $25–50).
2. Teensy 4.1 stock at Digi-Key (SparkFun upstream is on backorder).
3. Customs: order >€200 → expect duty/VAT; consider splitting batches.
4. AliExpress items: check seller ratings; avoid "Teensy" listings entirely.
