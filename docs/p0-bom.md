# P0 Test-Rig BOM — components, suppliers, prices, shipping to Kazakhstan

Shopping list for the P0 rig ([business-plan.md](business-plan.md) Step 2 +
[firmware/README.md](../firmware/README.md)) and the seeded-defect test bench.
Delivery target: **Karaganda, KZ**.

Prices spot-checked **2026-07-06** (web research). **✓** = seen on a live
page/snippet that day; **~** = estimate, verify before ordering. Customs note:
single orders above the EAEU personal-import threshold (~€200) may incur
duty/VAT on top of the prices below.

## ⚠ Supplier access from Kazakhstan (checked 2026-07-06)

**Digi-Key geo-blocks Kazakhstan IPs** (confirmed by us: digikey.com returns
"blocked" from KZ, loads via EU VPN). Context: since 2023 US export-control
guidance (BIS/FinCEN transshipment alerts) treats KZ as a diversion-risk
destination, so several US distributors restrict service. **Do not order via
VPN to a KZ address** — compliance screening at checkout/fulfilment will
likely kill the order anyway. Digi-Key prices below are kept as reference only.

**The two key parts now come from different places** (checked 2026-07-06):

**Sensor (EVAL-ADXL1002Z) → ✗ NOT Mouser either.** Checkout tested 2026-07-10:
**Kazakhstan is absent from Mouser's ship-to country list** (cart reached the
address step, $110.21 DDP — no KZ option). Same de-risking as Digi-Key, just
enforced at checkout instead of the firewall. Working routes, in order:
1. **RadioMart order-in** (~3–4 wk, quote requested with the Teensy) — local
   importer handles the channel professionally;
2. **TME Poland export desk** (+48 42 645 54 44; carries Analog Devices — ask
   for the eval board explicitly);
3. **Chip One Stop** (Japan, Arrow group, int@chip1stop.com);
4. **plaza.kz** (Almaty agent, +7 778 006 60 00) — orders US-distributor items
   with KZ delivery.
Self-import via freight forwarder is technically possible but works around the
distributor's compliance terms — prefer the licensed-importer routes above.

**Teensy 4.1 → NOT Mouser.** ⚠ PJRC's store now links **only to SparkFun**
(sole manufacturer since 2025); Mouser/Digi-Key buy-links were dropped, so
`DEV-16771` appears delisted at Mouser. Genuine-board routes, live status:

| Shop | Price | Stock (2026-07-06) | Ships to KZ? | Link |
|---|---|---|---|---|
| **RadioMart** (Karaganda, local) | **84 370 ₸ ≈ $153** (quoted 2026-07-09; site's 59 000 ₸ stale) | **back-order confirmed: ~5–6 weeks from Europe**, 1 pc or batch OK, 3-month own warranty, genuine confirmed, **50/50 payment accepted**, pickup Karaganda or KZ-wide delivery; no Teensy 4.0 in stock; other components order-in ~3–4 wk; parallel import («признак 5» — manufacturer bars export to KZ) | **local ✓** | [radiomart.kz](https://radiomart.kz/teensy/6016-plata-teensy-41-bez-pin.html) |
| **Electrokit** (SE) | 379 SEK ≈ $36 | 54 in stock ✓ | **✗ confirmed by email 2026-07-07: EU-only, no export outside EU** | [electrokit.com](https://www.electrokit.com/en/product/teensy-4-1/) |
| **Opencircuit** (NL) | €44.50 (€36.80 ex-VAT) | in stock, 5–7 d ✓ | not stated — email info@opencircuit.nl (likely EU-only too) | [opencircuit.shop](https://opencircuit.shop/Product/Teensy-4.1) |
| **Pimoroni** (UK) | £23 | out of stock ✗ | worldwide shipping stated — likely moot given manufacturer export bar | [shop.pimoroni.com](https://shop.pimoroni.com/en-us/products/teensy-4-1) |
| SparkFun (source) | $37.20 | backordered ✗ | **✗ — manufacturer bars export to KZ** (per RadioMart) | [sparkfun.com](https://www.sparkfun.com/teensy-4-1.html) |

**Key learning (2026-07-07):** PJRC/SparkFun officially prohibits export of Teensy
to Kazakhstan — which explains the Digi-Key geo-block and Electrokit's refusal in
one stroke. The realistic channel is KZ parallel import (RadioMart-style): EU-
sourced, seller's own warranty (3 mo), ~5–6 week lead. Order early, order spares.

All presented as genuine PJRC/SparkFun (`DEV-16771` / `TEENSY41`); AliExpress
excluded — $2–15 "Teensy" listings are documented counterfeits that fail under
vibration. There's a real Teensy 4.1 supply crunch (SparkFun + Pimoroni + RadioMart
all dry). **Recommended play (updated 2026-07-09 after the price quote):** order
**1× Teensy 4.1 via RadioMart** back-order at the quoted 84 370 ₸ (~4× MSRP but
the only compliant KZ route; 50/50 payment; get the price fixed in the invoice) —
the second unit is deferred, budget permitting later. **Buy the EVAL-ADXL1002Z
from Mouser directly** (~$100–110 + shipping — RadioMart's markup pattern would
put it well above that; still worth letting them quote it as the fallback).
Small items (tachometer, coax, magnets) stay local/AliExpress unless RadioMart's
quote is competitive. Handling discipline while running a single board: sensor
powered from 3V3 only (5 V supply would drive VOUT past the Teensy's ADC limit),
ground yourself before touching the rig, no hot-plugging the analog line. The "no pins"
variant is fine (solder wires directly — more robust under vibration than
headers). Set a Pimoroni back-in-stock alert as the worldwide fallback.

Other routes considered: Welectron DE (official Teensy distributor, worldwide
DHL) is another genuine option if the above stall; plaza.kz (Almaty agent,
sale@plaza.kz) can special-order; Taiwan has no franchised intl-retail route
(Switch Science JP closed its international store in 2022).

## Ordering strategy (TL;DR)

| Batch | Contents | Lead time |
|---|---|---|
| **1a — Mouser** | sensor eval board (EVAL-ADXL1002Z) | ~3–7 business days (FedEx/UPS) + customs |
| **1b — RadioMart (local) or Electrokit** (separate order — Teensy not on Mouser) | Teensy 4.1 | RadioMart back-order if offered (local, no customs) // EU ~1–2 wk pending KZ confirm — pursue in parallel |
| **2 — Local Karaganda / KZ marketplaces** (satu.kz, kaspi.kz, tomas.kz, OLX) | test bearings, bench grinder, Loctite, tachometer, USB cable | same day – 5 days |
| **3 — AliExpress batch** (cheap, slow — order day 1) | magnet base, coax + BNC, spare reflective tape | ~10–25 days |

Batches 1+2 alone are enough to start; batch 3 items have local or bundled
substitutes.

## 1. Core rig (required)

| Component | Pick | Supplier | Price | Ships to KZ | Notes |
|---|---|---|---|---|---|
| Vibration sensor | **EVAL-ADXL1002Z** (±50 g, flat to ~11 kHz, analog out, 25 µg/√Hz) | **RadioMart order-in (quote pending)** / TME export desk / Chip One Stop | US ref $110 ✓; KZ landed price TBD | ~3–4 wk (RadioMart channel) | ⚠ Mouser checkout has **no Kazakhstan** in the country list (tested 2026-07-10); Digi-Key geo-blocked. All US direct routes closed |
| — budget sensor option | EVAL-ADXL1005Z (±100 g, flat to ~23 kHz, 75 µg/√Hz — noisier, fine for seeded defects) | Mouser / TME | ~$50–65 ✓ | same order | Halves the sensor cost if the noise floor is acceptable |
| ADC / MCU | **Teensy 4.1** (600 MHz, samples ≥51.2 kSPS, streams USB) | **[Electrokit](https://www.electrokit.com/en/product/teensy-4-1/) ≈$36 / [Pimoroni](https://shop.pimoroni.com/en-us/products/teensy-4-1) £23** | ~$36–46 | EU ~1–2 wk (confirm KZ) | ⚠ **Not on Mouser/Digi-Key** — PJRC sells via SparkFun only now. See Teensy table above. ⚠ **Never AliExpress** (counterfeits fail under vibration) |
| Pin headers | 2×24-pin 2.54 mm breakaway strips | add to the Teensy order | ~$2 ~ | rides along | Or buy the pins-presoldered Teensy variant |
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

## Ordering status (2026-07-10)

1. **Teensy 4.1:** RadioMart quote in hand — 84 370 ₸/pc, 50/50 payment,
   genuine, 5–6 wk. Ordering **1 pc** (budget call; ask for a same-price option
   on a 2nd). All US/EU direct routes confirmed closed.
2. **Sensor (EVAL-ADXL1002Z):** Mouser checkout confirmed to exclude Kazakhstan
   (tested 2026-07-10) — awaiting RadioMart's quote; probing TME export desk and
   Chip One Stop (int@chip1stop.com) in parallel; plaza.kz as the local-agent
   fallback.
3. **Bench + small items:** buy locally now (satu.kz/kaspi/OLX) — independent of
   import lead times; the bench can be built and defects seeded before any
   electronics arrive.
4. Customs/compliance: rides with the licensed importer on routes 1–2. Avoid
   self-import via forwarders — it works around distributor compliance terms.
5. AliExpress items: check seller ratings; avoid "Teensy" listings entirely.
