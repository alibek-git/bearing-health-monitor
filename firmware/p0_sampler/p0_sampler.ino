// p0_sampler — Teensy 4.1 + ADXL1002 breakout: sample and stream raw blocks.
//
// The P0 rig keeps firmware deliberately dumb: sample the accelerometer's analog
// output at FS, frame fixed-size blocks, write them to USB serial at full rate.
// All analysis happens on the host (scripts/record_teensy.py -> analysis/).
//
// Wiring (EVAL-ADXL1002Z): VOUT -> A0, VDD -> 3V3, GND -> GND. At a 3.3 V supply
// the ADXL1002 is ratiometric: ~26.4 mV/g, mid-supply at 0 g. Keep the analog
// lead short; the host removes the DC offset.
//
// Frame format (little-endian), one frame per block:
//   magic  "VIB1"   4 B
//   seq    uint32   frames sent since boot (host detects gaps)
//   n      uint16   samples in this frame (= BLOCK)
//   dropped uint32  blocks lost since boot (host wasn't reading fast enough)
//   payload n * uint16  raw 12-bit ADC counts (0..4095, Vref 3.3 V)
//   csum   uint16   sum of payload words, mod 65536 (resync guard)
//
// Sampling uses IntervalTimer + analogRead: bulletproof Teensyduino core API,
// comfortably fast at 12-bit/no-averaging on Teensy 4.x for FS = 51.2 kHz
// (~19.5 us period vs ~3 us conversion). The DMA/ADC-library path is the later
// upgrade if ISR jitter ever shows in the spectra — for envelope analysis it
// hasn't mattered at P0.
//
// NOT YET TESTED ON HARDWARE (board on back-order) — flash, run
// scripts/record_teensy.py, and check the "dropped" counter stays 0.

#include <Arduino.h>

const int      PIN_VIB = A0;
const uint32_t FS      = 51200;   // Hz — must match --fs on the host
const uint16_t BLOCK   = 2048;    // samples per frame (~25 frames/s, ~103 KB/s)

uint16_t          buf[2][BLOCK];
volatile uint16_t widx    = 0;
volatile uint8_t  wbuf    = 0;
volatile uint8_t  rbuf    = 0;
volatile bool     ready   = false;
volatile uint32_t dropped = 0;
uint32_t          seq     = 0;

IntervalTimer timer;

void sampleISR() {
  buf[wbuf][widx] = (uint16_t)analogRead(PIN_VIB);
  if (++widx >= BLOCK) {
    widx = 0;
    if (ready) dropped++;   // previous block never got sent
    rbuf  = wbuf;
    wbuf ^= 1;
    ready = true;
  }
}

void setup() {
  analogReadResolution(12);
  analogReadAveraging(1);
  Serial.begin(0);                  // USB CDC: baud is ignored, always 480 Mbit
  while (!Serial && millis() < 4000) {}
  timer.begin(sampleISR, 1000000.0 / FS);
}

void loop() {
  if (!ready) return;
  noInterrupts();
  uint8_t b = rbuf;
  ready = false;
  interrupts();

  uint16_t csum = 0;
  for (uint16_t i = 0; i < BLOCK; i++) csum += buf[b][i];

  uint32_t seq_le = seq, drop_le = dropped;
  uint16_t n_le   = BLOCK;
  Serial.write((const uint8_t *)"VIB1", 4);
  Serial.write((const uint8_t *)&seq_le, 4);
  Serial.write((const uint8_t *)&n_le, 2);
  Serial.write((const uint8_t *)&drop_le, 4);
  Serial.write((const uint8_t *)buf[b], BLOCK * 2);
  Serial.write((const uint8_t *)&csum, 2);
  seq++;
}
