# demo — live dashboard on a synthetic machine

A self-contained demo you can show to anyone: a simulated 1480-rpm pump with a
6205 bearing degrades in compressed time (1 capture = 1 machine-hour), and every
capture flows through the **real detection pipeline** — the exact code validated
on CWRU and NASA IMS (matched band pick → envelope spectrum → slip alignment →
comb SNR → verdict → baseline trend with sustained warn/alarm).

The punchline for a viewer: press **Start degradation** and watch the trend
cross WARN, then ALARM — with the failing element named — long before the
severity maxes out. The simulator even runs the machine 1.8% below kinematic
frequencies, and the dashboard shows the detector *finding* that slip.

## Run

```bash
# Docker (recommended for a clean demo box) — from the REPO ROOT:
docker build -f demo/Dockerfile -t bearing-demo .
docker run --rm -p 8000:8000 bearing-demo

# or straight from the venv:
pip install -r demo/requirements.txt
uvicorn demo.app:app --port 8000
```

Open <http://localhost:8000>.

## Suggested demo script (~3 minutes)

1. Point at the **HEALTHY** verdict and flat trend — "this is the machine's
   normal life; the system learned its baseline by itself."
2. Pick a fault type (outer race is the most common real-world mode), press
   **Start degradation**.
3. Narrate the **WARN** event when it fires ("this is the SMS the fitter gets —
   days before failure in machine time"), then **ALARM** with the element named.
4. Show the envelope spectrum: the comb lines land exactly on the dashed
   expected-frequency markers — "we know *which part* of the bearing is dying,
   not just that something vibrates."
5. Reset, switch to **Manual** mode, and drag severity yourself to show the
   verdict tracking it.

## Files

- `simulator.py` — physics-faithful synthetic captures (impact trains with the
  correct modulation per fault type + cage slip)
- `app.py` — FastAPI: one endpoint advances the sim and returns verdict, spectra,
  trend ratios, and sustained-crossing events
- `static/index.html` — single-page dashboard (Chart.js from CDN)

Not a product UI — a P0 storytelling tool. The product dashboard (RU/KZ,
multi-asset, Telegram/WhatsApp alerts, 1C export) is the P1 item it prefigures.
