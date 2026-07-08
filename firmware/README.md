# firmware — edge sensor sampling (P0)

P0 is deliberately simple: a dev-board samples a vibration sensor at high rate and
streams raw blocks to a laptop, where `analysis/` does the work. The product node
(low-power wireless, on-edge feature extraction) comes in P2.

## P0 rig
Shopping list with suppliers, prices, and shipping-to-KZ estimates:
[`docs/p0-bom.md`](../docs/p0-bom.md).

- **Sensor:** ADXL1002 (±50 g, flat to ~11 kHz, 21 kHz resonance, low noise — the
  resonance band envelope analysis exploits). Analog output.
  *Higher-fidelity fallback:* an IEPE/ICP 100 mV/g accelerometer + conditioner.
- **MCU/ADC:** Teensy 4.1 (600 MHz, fast ADC) sampling at **51.2 kSPS**, streaming
  fixed-size blocks (e.g. 65536 samples) over USB serial.
- **Mount:** stud (preferred) or rare-earth magnet on the **bearing housing, load
  zone, radial** direction. Mount stiffness dominates high-frequency fidelity.
- **RPM:** nameplate / VFD readout / estimated from the 1× peak.

## Sketch
[`p0_sampler/p0_sampler.ino`](p0_sampler/p0_sampler.ino) — IntervalTimer-driven
sampling at 51.2 kSPS (12-bit, A0), double-buffered 2048-sample blocks streamed
over USB CDC as framed packets:

```
"VIB1" | seq u32 | n u16 | dropped u32 | payload n×u16 | csum u16   (little-endian)
```

`dropped` counts device-side overflows (host reading too slowly) — a healthy
capture keeps it at 0. Host side: `scripts/record_teensy.py` (parses, verifies
checksums + sequence continuity, saves .npy + sidecar JSON, and scores the
capture with the full detector on the spot).

**Not yet run on hardware** — the Teensy is on back-order (see
[`docs/p0-bom.md`](../docs/p0-bom.md)). The wire protocol itself is
regression-tested host-side (`tests/test_record.py`), including an end-to-end
synthetic-fault → frames → verdict test.

## Roadmap
P2 node: low-power MCU (STM32L / nRF52) + ADXL1002 + sub-GHz/LoRa radio + multi-year
Li-SOCl₂ cell + IP67 enclosure; compute envelope features on-edge to minimize radio
traffic. Underground-mining variant requires **EAC Ex / TR CU 012** certification.
