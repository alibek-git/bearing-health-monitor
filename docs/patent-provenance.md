# Patent Provenance — where this idea came from

The idea behind this repo was surfaced by the [`cortex_agents`](https://github.com/alibek-git/cortex_agents)
pipeline, which scans **expiring or recently expired** US patents in selected CPC classes
and scores each for commercial promise and build difficulty.

This document records the actual source patent, its ownership, and its legal status —
because the first version of [`business-plan.md`](business-plan.md) cited the wrong
patent number, and because the ownership is commonly misattributed.

**Verified 2026-07-26** against the USPTO grant facsimile, USPTO Assignment Center,
DPMAregister, the EPO Register/Espacenet, Google Patents, Justia and FreePatentsOnline.

---

## 1. The source patent

| Field | Value |
|---|---|
| **Number** | **US 7,599,804 B2** |
| Title (54) | METHOD FOR DETECTING STRUCTURE-BORNE NOISE EVENTS IN A ROLLER BEARING |
| German original | DE 103 03 877.9 — *"Verfahren zur Feststellung von Körperschallereignissen in einem Wälzlager"* |
| Inventor (75) | **Alfred Pecher**, Stadtlauringen (DE) — sole inventor |
| Assignee (73) | **FAG Kugelfischer AG** (DE), Schweinfurt |
| Application | 10/543,844 · PCT/DE2004/000095 · WO 2004/068100 A1 |
| PCT filed (22) | 2004-01-23 · §371(c) date (86) 2005-08-29 |
| Priority (30) | **2003-01-31** (DE 103 03 877) |
| Granted (45) | **2009-10-06** (pre-grant pub. US 2006/0150737 A1) |
| Classification | Int. Cl. G01M 13/04 · CPC **G01M13/045** + F16C19/52 · U.S. Cl. 702/39 |
| Family | DE10303877A1 · WO2004/068100A1 · EP1616163A1/B1 · DE502004002624D1 · ES2277234T3 · JP2006518455A / JP4424515B2 · CN1756944A / CN100510678C · US2006/0150737A1 |

### How it was selected

`cortex_agents` ran the industrial pool with `CPC_PREFIXES="G01,G05B"` and selected
patents whose estimated term expires within ±3 years of the run date
(`EXPIRY_BACK_YEARS` / `EXPIRY_FWD_YEARS` in `src/config.py`) — i.e. freedom-to-operate
was the selection filter by design. From `logs/patents_industrial_resume.log:86`:

```
2026-06-24T05:27:12Z INFO cortex [25/40] Analyzing US-7599804-B2 — Method for detecting structure-borne noise events in a roller bearing
2026-06-24T05:27:22Z INFO cortex [25/40] Wrote US-7599804-B2 (promise=7/10, difficulty=6/10)
```

Note that the pipeline's BigQuery projection is
`patent_id, title, abstract, cpc_class, grant_date, estimated_expiration` — it never
fetches the assignee or the claims. So the idea came from the patent's **topic**, not
from its teaching. See §5.

---

## 2. Ownership — FAG Kugelfischer → Schaeffler

From DPMAregister's *Früherer Anmelder/Inhaber* fields on DE 103 03 877.9, corroborated
by the EPO Register:

```
FAG Kugelfischer Georg Schäfer AG, Schweinfurt   (at filing, 2003-01-31)
  → FAG Kugelfischer AG & Co. KG                 (2003-04-30)
  → FAG Kugelfischer AG                          (2003-12-12)  ← string on the US patent face
  → FAG Kugelfischer AG & Co. oHG                (2005-08-24)
  → Schaeffler KG, Herzogenaurach                (2006-04-10)
  → Schaeffler Technologies GmbH & Co. KG        (2010-04-23)
  → Schaeffler Technologies AG & Co. KG          (2012-08-27)
```

These are renames and internal restructurings inside one group following
INA-Holding Schaeffler's 2001 takeover of FAG Kugelfischer — never a third-party sale.
FAG Kugelfischer AG & Co. oHG was dissolved 2006-01-01 into Schaeffler KG, so title
passed by universal succession.

**No assignment was ever recorded at the USPTO** (Assignment Center returns
`noOfAssignments: 0` for patent 7599804 / application 10543844). That is normal —
recording under 35 U.S.C. § 261 is permissive, not a condition of title — but it means
the *US* assignee of record is still "FAG Kugelfischer AG".

> **Uncertain:** the exact current-owner label. DPMAregister (primary) says
> *Schaeffler Technologies AG & Co. KG*; Google Patents normalises "Current Assignee" to
> *IHO Holding GmbH & Co. KG* (the Schaeffler family holding vehicle); the USPTO still
> shows *FAG Kugelfischer AG*. All are Schaeffler-side. The group identity is certain;
> the legal-entity label is not.

### It was **not** General Electric

A common misattribution, worth stating plainly:

- "General Electric" appears **zero times** in the Google Patents record and zero times
  in the full DPMAregister file for DE 103 03 877.9.
- No GE entity appears as applicant, assignee, proprietor, or recorded assignor/assignee
  at any link in the chain.
- The English title is a near-verbatim translation of the **German FAG title**.

Why the confusion is understandable: **G01M13/045 is a class where GE does hold patents**
(~24 families, notably **US 3,677,072 A**, Bjorn Weichbrodt, priority 1970 — which claims
a peak-to-mean *crest-factor* discriminator, not event detection or envelope demodulation),
and GE acquired **Bently Nevada** in January 2002. But Bently Nevada's portfolio is
eddy-current proximity probes and machinery protection, not envelope demodulation — and
GE has since fully exited (Bently Nevada is a Baker Hughes brand today).

Approximate G01M13/045 family counts by holder: SKF ~118 · Siemens ~63 ·
Schaeffler/FAG ~49 · GE 24 · SPM ~14 · Emerson/CSI ~12 · Rockwell ~7.

---

## 3. Legal status — expired everywhere

| Right | Status |
|---|---|
| **US 7,599,804 B2** | **EXPIRED.** 3.5-year maintenance fee never paid. REMI 2013-05-17 → **LAPS 2013-10-06** → STCH "PATENT EXPIRED DUE TO NONPAYMENT OF MAINTENANCE FEES UNDER 37 CFR 1.362". Nominal adjusted expiry would have been 2025-11-08 (655 days PTA); it died ~12 years early. No terminal disclaimer. |
| **DE 103 03 877.9** | Never granted — deemed withdrawn for non-payment, *"Nicht anhängig/erloschen"*. |
| **EP 1 616 163 B1** | Granted 2007-01-10, no opposition filed, then abandoned state-by-state for unpaid renewals. Dead everywhere. |
| JP / CN / ES members | Same abandoned family. |

> **Uncertain:** the per-state EP lapse dates. Two independent reads of the register
> disagreed (one placing most lapses in 2007–2008 with a few states running to early 2013;
> the other placing all lapses 2007–2009). Both agree no renewal was paid past early 2013.
> The disagreement is entirely in the past and has no practical consequence.

**Consequence:** the method is unencumbered prior art, freely implementable, with **no
licence requirement**. It equally confers **no exclusivity** — it is prior art against
everyone. This is consistent with the plan's own position that the moat is local, not
technological. Live patent risk in this space sits in narrow modern implementation claims
held by SKF, Siemens, Schaeffler, Emerson/CSI and SPM — not in the general technique.

---

## 4. People

**Alfred Pecher** — sole inventor, FAG Kugelfischer employee at filing (Stadtlauringen is
~20 km from FAG's Schweinfurt HQ). Continues into Schaeffler: US 7,591,194 (filed 2004)
lists him with assignee Schaeffler KG. By December 2013 a Schaeffler press release on the
new Herzogenaurach acoustics test field quotes **"Dr. Alfred Pecher, Leiter Akustik"**
(Head of Acoustics) — air- and structure-borne sound, i.e. a direct ten-year line from
this patent. Listed as **"Prof. Dr. Alfred Pecher"** among adjunct lecturers at the
Faculty of Mechanical Engineering, TH Würzburg-Schweinfurt. 61 patent publications
(~20 families); seven US grants name him: 7,263,901 · 7,568,842 · 7,591,194 · 7,599,804 ·
7,650,254 · 7,716,018 · 7,860,689.

> **Not asserted** (no source found): his university, degree, or dissertation.
> **Namesake warning:** an ABB powerline-DSSS patent and a TU Ilmenau biosignal patent
> under the same name are almost certainly a different person.

**FAG's condition-monitoring organisation at the time** — FAG Industrial Services GmbH
(Herzogenrath, registered 2002-06-21, renamed Schaeffler Monitoring Services 2019), run by
Hans-Willi Keßler. Group level: Jürgen Geißinger (Schaeffler CEO 1998–2013, FAG chairman
2001–04), Robert Schullan (head of FAG from 2004-03-01).

---

## 5. What this repo actually implements — and it is *not* this patent's method

Worth being precise about, since the provenance line invites the assumption.

**The patent claims:** filter the signal from a pressure- or strain-sensitive sensor on the
bearing, compute a first and at least one further variance value from the digital filter
output, take their **weighted arithmetic mean by recursive calculation**, and declare a
structure-borne-noise event when it exceeds a threshold. The stated point is to run the
damage decision on an evaluation device with very little memory and compute — explicitly
**without an FFT** — e.g. electronics inside a circumferential groove of the bearing ring.

**This repo implements:** band-pass → **Hilbert envelope** → envelope spectrum →
peak-picking at the kinematic defect frequencies and their harmonics, with a matched
kurtogram band picker, slip estimation and baseline trending. That is the
**HFRT / envelope-analysis lineage** — Balderston (Boeing, 1969), Darlow/Badgley/Hogg
(1974), McFadden & Smith (1984), Antoni & Randall spectral kurtosis (2006–07),
SKF gE/SEE, Emerson PeakVue — all long-published, public-domain literature.

So US 7,599,804 B2 was the **idea trigger** (its title and abstract are all the pipeline
fed its analyzer), not a technical source. Nothing here is derived from its claims.

Historical credit for the underlying technique, none of it GE:

1. **Shock Pulse Method** — Eivind Olav Sohoel, US 3,554,012 (filed 1968), later SPM Instrument
2. **H. Balderston**, Boeing (1969) — fault energy lives in HF resonances excited by impacts
3. **Darlow, Badgley & Hogg** (1974) — named and demonstrated HFRT
4. **McFadden & Smith** (1984), *Tribology International* — the canonical review
5. **SKF** enveloped acceleration / SEE (early 1990s); **Emerson/CSI PeakVue** — J. C. Robinson, US 5,895,857 (1997)
6. **Spectral kurtosis / kurtogram** — Dwyer (1983) → Antoni & Randall (2006), Antoni (2007)
7. Oldest in class: US 2,793,525 A, Bruce I. Mims, **Barden Corp.** (1953 — Barden is now Schaeffler); Tibor Tallian, **SKF**, US 3,208,268 A (1961)

---

## 6. Correction log

The original [`business-plan.md`](business-plan.md) source line cited **`US-7708998-B2`**.
That number is **"Methods of inhibiting unwanted cell proliferation using hedgehog
antagonists"** — a Curis, Inc. oncology patent (inventors Dudek, Karavanov, Pepicelli,
Kotkow, Rubin; priority 2000-10-13; granted 2010-05-04; expired 2022-04-14). It contains
no G01M classification and has no DE/EP/WO family.

It appears in the same `cortex_agents` sheet, scored **promise 6 / difficulty 9**, whereas
the business plan records **promise 7 / difficulty 6** — which is US-7599804-B2's score.
So the scores came from the right row and only the identifier was wrong: a row
misalignment when the pool was transcribed, not a typo (the digits don't map).

**Worth checking whether other entries transcribed from that sheet carry the same offset.**
