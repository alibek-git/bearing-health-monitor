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

## Sketch (to add)
`p0_sampler/` — Arduino/Teensy sketch: configure ADC, sample at Fs, frame blocks
(magic + length + samples), write to USB at full rate. The host side is
`scripts/record_teensy.py` (planned).

## Roadmap
P2 node: low-power MCU (STM32L / nRF52) + ADXL1002 + sub-GHz/LoRa radio + multi-year
Li-SOCl₂ cell + IP67 enclosure; compute envelope features on-edge to minimize radio
traffic. Underground-mining variant requires **EAC Ex / TR CU 012** certification.
