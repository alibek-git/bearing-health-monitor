# Retrofit Bearing-Health Monitoring for Heavy Industry

**One-liner:** A retrofittable wireless sensor kit + edge-AI software that bolts onto
existing rotating machinery (motors, pumps, fans, gearboxes, conveyors, mill stands)
and predicts bearing failure weeks before it happens — assembled and supported locally
in Kazakhstan, sold first to Karaganda heavy industry.

- **Source:** `Patents — Industrial Software` pool, `US-7708998-B2`-class (`G01M13` —
  structure-borne noise / rolling-element bearing diagnostics). Promise 7 / Difficulty 6
  (the most buildable idea at the top of that pool).
- **Why it's here:** the demand is proven (Schaeffler OPTIME, SKF, Augury, Waites all
  sell this globally), and the founder has a real edge — **local assembly + on-site
  support + RU/KZ language + local-content procurement + a warm anchor market in the
  Karaganda industrial basin.** The moat is local, not technological.

---

## 1. Problem

Unplanned downtime from bearing failure is one of the largest avoidable costs in heavy
industry. Rolling-element bearings fail progressively (microscopic spalling → defect
frequencies → heat → seizure), and the failure is **detectable weeks in advance** via
vibration — yet most mid-tier and older plants still run reactive or fixed-interval
maintenance. A single unplanned stop on a critical line (a blast-furnace blower, a
rolling-mill stand, a main pump) can cost tens of thousands of dollars per hour plus
collateral damage and safety risk.

## 2. Market

- **Anchor — Karaganda basin.** Qarmet (Temirtau) is KZ's largest steel + mining
  company: ~34,000 staff, integrated steel works, 8 coal mines, iron-ore and coal-prep
  plants, expanding to 5 Mt steel / 9 Mt coal by 2028. Thousands of monitored points of
  rotating equipment in *non-explosive* areas alone (steel plant, mills, fans, pumps,
  surface conveyors, prep plants).
- **Expand — KZ heavy industry:** Kazakhmys, Kazzinc, ERG / Aluminium of Kazakhstan,
  cement plants, power stations, oil & gas processing.
- **Then — CIS / EAEU** plants sharing the same equipment base, language, ERP (1C), and
  certification regime.
- **Beachhead segment:** the mid-market / legacy-equipment slice the premium foreign
  vendors under-serve — where the buyer wants *affordable + locally supported*, not a
  six-figure platform contract in English.

## 3. Solution

A wireless, battery-powered sensor (vibration + temperature) that mounts magnetically or
by stud on a bearing housing, does **on-edge feature extraction**, and streams compact
health features over a low-power radio to a plant gateway → cloud dashboard with alerts
in Russian/Kazakh, pushed to Telegram/WhatsApp (the channels operators actually use).

## 4. The build — import / assemble / code

### Import (commodity components — China / EU / US)
| Part | Choice | Why |
|---|---|---|
| Vibration sensor | MEMS accelerometer with wide bandwidth (e.g. ADXL1002, ~11 kHz / 21 kHz resonance, ±50 g) | Bearing defect harmonics need bandwidth to ~10–20 kHz; MEMS keeps cost/power low vs. piezo (IEPE) units that cost 10×+ |
| Temperature | RTD/thermistor or sensor-integrated | Secondary failure signal, trivial cost |
| Edge MCU | Low-power MCU with DSP (STM32L / nRF52 class) | On-edge FFT/envelope to minimize radio traffic → multi-year battery |
| Radio | Sub-GHz / LoRa mesh (or NB-IoT where cellular is better) | Long range + penetration in steel structures; mesh like incumbents |
| Gateway | Industrial edge gateway (RPi CM4-class) | Aggregates sensors → cloud over plant network / cellular |
| Power | Li-SOCl₂ primary cell (multi-year), or wired 24 V | Maintenance-free wireless nodes |
| Enclosure | IP66/67, –40…+85 °C, magnetic/stud mount | Karaganda climate + plant heat/dust |

### Assemble (locally, Kazakhstan) — *this is the wedge*
- PCB fab + SMT via contract (JLCPCB/PCBWay or a regional EMS); **final assembly,
  potting, calibration against a reference shaker, QA, and firmware flashing done
  locally.** Gateways configured locally. Local assembly + a KZ legal entity unlocks
  **local-content procurement preference** with SOEs and keeps support fast and in-language.

### Code (the real IP / moat)
- **Edge firmware:** high-rate sampling (~25.6 kHz), windowing, FFT + **envelope
  analysis** (band-pass demodulation) to extract bearing defect frequencies (BPFO, BPFI,
  BSF, FTF — computed from bearing geometry + shaft RPM), plus ISO 10816 broadband
  velocity, kurtosis, crest factor. Duty-cycled for battery life.
- **Connectivity:** MQTT/CoAP over the radio → gateway → cloud.
- **Backend:** ingestion API, time-series DB (TimescaleDB/InfluxDB), an asset/bearing
  registry (geometry, RPM, ISO class), alerting engine.
- **Analytics:** **physics-first** (ISO velocity zones + defect-frequency tracking) for
  day-one value with *zero training data* — then anomaly detection and remaining-useful-
  life (RUL) trending as data accumulates (the data moat).
- **Frontend:** web dashboard (asset health map, trends, diagnostics, alerts), RU/KZ
  localization, mobile push.
- **Integrations:** export work orders to **1C** (dominant CMMS/ERP in the CIS) and
  SAP PM for the largest plants.

> Key technical point: envelope analysis + defect-frequency detection is decades-proven
> and explainable, so the product is useful before any ML — ML is upside, not a
> prerequisite.

## 5. Wedge & moat
- **Cost:** locally assembled at a fraction of OPTIME/Augury/Waites pricing (industrial
  points run premium $/sensor + significant subscription).
- **Local presence:** on-site service, RU/KZ language, KZ entity, local-content
  compliance, no import/customs friction for the customer.
- **Domain-tuned:** mounting and models tuned to the local mix of Soviet-era + modern
  equipment and harsh dust/temperature conditions.
- **Data moat:** failure data on the specific local fleets compounds over time.

## 6. Go-to-market
1. **Paid pilot at one Qarmet shop** (e.g. a pump/fan station or a rolling-mill line):
   instrument 20–50 critical bearings, prove ROI in avoided downtime over 3–6 months.
2. **Sell the outcome (uptime), not the hardware** — per-sensor price + SaaS/sensor/month.
3. Expand within Qarmet's vast asset base, then to other KZ plants; lead with the
   local-content + local-support story foreign vendors can't match.

## 7. Roadmap
- **P0 (1–2 mo):** off-the-shelf accel + dev MCU + envelope-analysis code + simple
  dashboard on 1–2 real machines → validate signal + detection.
- **P1 (3–6 mo):** pilot — 20–50 wireless nodes + gateway at one plant; RU dashboard;
  1C export; prove ROI.
- **P2 (6–12 mo):** own ruggedized hardware (custom PCB, multi-year battery), multi-plant,
  RUL models.
- **P3 (12+ mo):** **EAC Ex / TR CU 012** certification → underground coal mining; expand CIS.

## 8. Rough unit economics (to validate)
- BOM/wireless node at small scale ≈ **$40–90** (accel ~$20, MCU+radio ~$15, battery
  ~$10–20, enclosure ~$10–20, PCB/assembly ~$10); lower at volume.
- Price ≈ **$200–400/node** + **$8–20/node/month** SaaS; gateway ~$300–600.
- Undercuts foreign incumbents while keeping healthy margin via local assembly. Even
  modest penetration of one large plant (hundreds–thousands of points) is meaningful ARR.

## 9. Key risks
1. **Ex-certification for mining** — underground coal (methane, Group I) requires
   **EAC Ex / TR CU 012**, EAEU-specific (ATEX/IECEx reports not accepted; needs
   accredited testing + production audit). *Mitigation: start non-Ex; treat mining as v2.*
2. **Sensor mounting & signal quality** — placement, resonant mounting, EM/thermal/dust
   noise. *Mitigation: mounting standards + reference calibration.*
3. **Cold-start data** — *mitigated by physics-first envelope analysis.*
4. **Industrial sales cycle** — long, relationship- and procurement-driven; SOE
   bureaucracy. *Mitigation: a plant champion + a paid pilot + the local-content angle.*
5. **False alarms erode trust** — conservative tuning; explainable diagnostics.
6. **Customer concentration** — over-reliance on Qarmet; diversify early.
7. **Talent** — needs embedded/DSP + ML + industrial sales; available via
   Karaganda/Almaty/Astana engineering schools.

## 10. Open questions / next steps
- Secure a beachhead contact + champion at Qarmet (or a nearby plant).
- Pick the first asset class (pumps/fans = simplest; rolling mills = highest value).
- Quantify the customer's current downtime cost and willingness to pay.
- Build P0 on one real machine and confirm we cleanly detect a seeded/known defect.

---

# P0 Technical Spec — validate the core claim

**Objective:** before any product hardware, prove that off-the-shelf vibration +
envelope analysis cleanly detects a *known* bearing defect. ~$150 of hardware,
~2–4 weeks part-time. De-risk the algorithm and the signal chain **separately**.

**Success criteria:**
1. On public labeled data (CWRU / IMS / NASA — below): the envelope spectrum shows
   a clear peak at the correct defect frequency (BPFO/BPFI/BSF) + harmonics for
   faulted bearings, and healthy bearings don't. Distinguish healthy vs faulted with
   margin.
2. On one real machine: capture a clean signal, compute a baseline, and (on a machine
   with a known/seeded defect) detect the defect frequency above baseline.

### Step 1 — validate the algorithm on public data FIRST (zero hardware)
Run the detector against open run-to-failure / seeded-fault bearing datasets — **CWRU
Bearing Data Center** (labeled inner/outer/ball faults, drive-end accelerometer,
12 kHz & 48 kHz), **NASA IMS** and **NASA/FEMTO PRONOSTIA** run-to-failure. If the
code finds the labeled defect frequencies there, the algorithm is proven independent
of our hardware. Only then go to the field.

### Step 2 — P0 hardware (off-the-shelf, wired)
| Part | Pick | Notes |
|---|---|---|
| Accelerometer | **ADXL1002** breakout (±50 g, flat to ~11 kHz, 21 kHz resonance, low noise) | Analog out; cheap and product-relevant. *Higher-fidelity option:* an IEPE/ICP 100 mV/g accelerometer (PCB 352-class) + IEPE conditioner — use to rule out sensor quality if results are marginal. |
| ADC / MCU | **Teensy 4.1** (600 MHz, fast ADC) | Samples ADXL1002 ≥ 51.2 kSPS, streams blocks to a laptop over USB; later becomes the edge-firmware test bed. A USB DAQ (Analog Discovery/NI) also works. |
| Mounting | Stud mount preferred; rare-earth magnet base acceptable | Mount on the **bearing housing, load zone, radial** direction. Mounting stiffness dominates high-frequency fidelity — a wobbly magnet kills the resonance band. |
| RPM | Nameplate RPM (or VFD readout; or estimate from the 1× peak) | Needed to compute defect frequencies. |
| Analysis | Laptop + Python (numpy/scipy) | All P0 analysis offline; firmware just ships raw blocks. |

### Step 3 — sampling parameters
- **Fs = 51.2 kSPS** (captures structural resonances to ~20 kHz where bearing impacts
  ring; ADXL1002's 21 kHz resonance is the energy band envelope analysis exploits).
- **Block length** ≈ 1 s (≥ 2¹⁶ samples) → ~1 Hz envelope-spectrum resolution, enough
  to resolve defect frequencies and their sidebands.
- **Averaging:** 8–16 blocks per measurement (median/mean of envelope spectra) to cut noise.
- Capture in the steady operating state; log RPM and load with each record.

### Step 4 — detection algorithm (the core IP)
Bearing defect frequencies from geometry + shaft speed, then **band-pass → Hilbert
envelope → envelope spectrum → peak-pick at defect frequencies**. Runnable outline:

```python
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert, welch

def bearing_freqs(rpm, n_balls, ball_dia, pitch_dia, contact_angle_deg=0.0):
    """Characteristic defect frequencies (Hz). Geometry from the bearing datasheet;
    if unknown, approximate BPFO≈0.4*n*fr, BPFI≈0.6*n*fr."""
    fr = rpm / 60.0
    r = (ball_dia / pitch_dia) * np.cos(np.radians(contact_angle_deg))
    return {
        "fr":   fr,                                   # shaft (1x)
        "FTF":  0.5 * fr * (1 - r),                   # cage
        "BPFO": (n_balls / 2) * fr * (1 - r),         # outer race
        "BPFI": (n_balls / 2) * fr * (1 + r),         # inner race
        "BSF":  (pitch_dia / (2 * ball_dia)) * fr * (1 - r**2),  # ball spin
    }

def envelope_spectrum(x, fs, band=(2000, 6000)):
    """Amplitude-demodulate the impact-resonance band and return its spectrum.
    `band` is the high-freq resonance window the bearing impacts excite; pick it
    with a kurtogram/spectral-kurtosis sweep, or start fixed (1-6 kHz)."""
    sos = butter(4, band, btype="bandpass", fs=fs, output="sos")
    xb = sosfiltfilt(sos, x - np.mean(x))
    env = np.abs(hilbert(xb))                  # Hilbert envelope = amplitude demod
    env -= np.mean(env)
    f, p = welch(env, fs=fs, nperseg=min(len(env), 1 << 15), scaling="spectrum")
    return f, np.sqrt(p)                        # amplitude vs frequency

def defect_score(f, amp, target, n_harmonics=4, tol=0.01):
    """Energy at a defect frequency + its harmonics (a developing fault shows a
    comb of harmonics, not just the fundamental)."""
    s = 0.0
    for h in range(1, n_harmonics + 1):
        ft = target * h
        m = np.abs(f - ft) <= max(tol * ft, f[1] - f[0])
        if m.any():
            s += amp[m].max()
    return s

# --- usage ---
# freqs = bearing_freqs(rpm=1490, n_balls=9, ball_dia=7.94, pitch_dia=39.04)
# f, amp = envelope_spectrum(signal, fs=51200, band=(2000, 6000))
# scores = {k: defect_score(f, amp, v) for k, v in freqs.items() if k != "fr"}
# -> the largest score names the failing element (outer/inner/ball/cage)
```

Pick the band with **spectral kurtosis / a kurtogram** (the band with the most
impulsive content) rather than a fixed window once the fixed-band version works —
it's the single biggest accuracy lever in real, noisy plant signals.

### Step 5 — severity & trending (beyond presence/absence)
- **ISO 10816 / 20816 overall velocity:** integrate acceleration → velocity, RMS over
  10–1000 Hz in mm/s, map to A/B/C/D severity zones for the machine class.
- **Time-domain features:** kurtosis and crest factor (rise early with impulsive
  bearing faults), broadband acceleration RMS.
- **Baseline + trend:** record a healthy baseline per asset; a **rising** defect-
  frequency score (with harmonics) is the alarm — absolute thresholds vary by machine,
  trends don't. This is also what seeds the later RUL model and the data moat.

### Step 6 — field protocol
1. One accessible machine (a pump/fan/motor), bearing datasheet in hand → compute defect freqs.
2. Record a healthy baseline (several captures across the operating range).
3. Detect on a machine with a known/seeded defect, or re-record the baseline machine
   over weeks watching for any developing trend.
4. Confirm: clean signal, correct defect frequency identified, baseline stable, fault
   distinguishable. That's the green light for P1 (wireless nodes + gateway at one plant).

