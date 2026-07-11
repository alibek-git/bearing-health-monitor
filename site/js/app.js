// site/js/app.js — in-browser live demo: the synthetic machine (simulator.js)
// pushed through the real detection pipeline (dsp.js). No backend, no fetch.
import { bearingFreqs, envelopeSpectrum, detect, pickBand,
         trendRatios, firstSustainedCrossing } from './dsp.js';
import { MACHINE, makeRng, capture } from './simulator.js';
import { STRINGS, applyLang } from './i18n.js';

const DEMO_STRINGS = {
  en: {
    title: 'Bearing-health monitor — live demo',
    heading: 'Bearing-health monitor',
    sub: 'live demo — synthetic machine, real detection pipeline, running in your browser',
    back: '← overview',
    machine: 'Machine · pump, 1480 rpm, 6205 bearing',
    fault: 'Seeded fault (takes effect as severity grows)',
    faultNone: 'None (healthy machine)', faultOuter: 'Outer race (BPFO)',
    faultInner: 'Inner race (BPFI)', faultBall: 'Ball (2×BSF)',
    mode: 'Mode', modeAuto: 'Auto — degrade over time (run to failure)',
    modeManual: 'Manual — set severity by hand', severity: 'Severity',
    start: '▶ Start degradation', pause: '⏸ Pause',
    reset: 'Reset machine (new baseline)',
    kCap: 'capture (1 = 1 h)', kBand: 'demod band',
    kSlip: 'slip found / true', kMargin: 'margin vs alarm',
    events: 'Events', noEvents: 'none yet — baseline building',
    wave: 'Raw vibration (25 ms)',
    spec: 'Envelope spectrum + expected defect lines',
    trend: 'Defect-score trend vs early-life baseline (log) — the product signal',
    waiting: 'waiting for data', likely: 'likely {el} — SNR {snr}',
    noDefect: 'no defect comb above the noise floor',
    healthy: 'HEALTHY', suspect: 'SUSPECT', faulted: 'FAULTED',
    evWarn: '⚠ warn: {el} over 4× baseline, sustained since {time}',
    evAlarm: '⛔ alarm: {el} over 10× baseline, sustained since {time}',
    simulated: '(simulated)', warnLine: 'warn 4×', alarmLine: 'alarm 10×',
    hoursAxis: 'machine hours', ratioAxis: 'score / baseline', hz: 'Hz',
  },
  ru: {
    title: 'Монитор состояния подшипника — живое демо',
    heading: 'Монитор состояния подшипника',
    sub: 'живое демо — синтетическая машина, реальный конвейер детекции, прямо в браузере',
    back: '← обзор',
    machine: 'Машина · насос, 1480 об/мин, подшипник 6205',
    fault: 'Заложенный дефект (проявляется с ростом серьёзности)',
    faultNone: 'Нет (исправная машина)', faultOuter: 'Наружное кольцо (BPFO)',
    faultInner: 'Внутреннее кольцо (BPFI)', faultBall: 'Тело качения (2×BSF)',
    mode: 'Режим', modeAuto: 'Авто — деградация со временем (до отказа)',
    modeManual: 'Ручной — серьёзность задаётся вручную', severity: 'Серьёзность',
    start: '▶ Запустить деградацию', pause: '⏸ Пауза',
    reset: 'Сброс машины (новый базовый уровень)',
    kCap: 'замер (1 = 1 ч)', kBand: 'полоса демодуляции',
    kSlip: 'скольжение: найдено / истинное', kMargin: 'запас до тревоги',
    events: 'События', noEvents: 'пока нет — строится базовый уровень',
    wave: 'Сырая вибрация (25 мс)',
    spec: 'Спектр огибающей + ожидаемые линии дефектов',
    trend: 'Тренд дефектных баллов к раннему базовому уровню (лог) — сигнал продукта',
    waiting: 'ожидание данных', likely: 'вероятно {el} — SNR {snr}',
    noDefect: 'дефектная гребёнка не выделяется над шумом',
    healthy: 'ИСПРАВЕН', suspect: 'ПОДОЗРЕНИЕ', faulted: 'ДЕФЕКТ',
    evWarn: '⚠ внимание: {el} выше 4× базы, устойчиво с {time}',
    evAlarm: '⛔ тревога: {el} выше 10× базы, устойчиво с {time}',
    simulated: '(симуляция)', warnLine: 'внимание 4×', alarmLine: 'тревога 10×',
    hoursAxis: 'часы наработки', ratioAxis: 'балл / база', hz: 'Гц',
  },
  kk: {
    title: 'Подшипник күйінің мониторы — тікелей демо',
    heading: 'Подшипник күйінің мониторы',
    sub: 'тікелей демо — синтетикалық машина, нақты анықтау конвейері, бәрі браузерде',
    back: '← шолу',
    machine: 'Машина · сорғы, 1480 айн/мин, 6205 подшипнигі',
    fault: 'Енгізілген ақау (ауырлық өскен сайын көрінеді)',
    faultNone: 'Жоқ (сау машина)', faultOuter: 'Сыртқы сақина (BPFO)',
    faultInner: 'Ішкі сақина (BPFI)', faultBall: 'Домалау денесі (2×BSF)',
    mode: 'Режим', modeAuto: 'Авто — уақыт өте тозу (істен шыққанша)',
    modeManual: 'Қолмен — ауырлықты өзіңіз қоясыз', severity: 'Ауырлық',
    start: '▶ Тозуды бастау', pause: '⏸ Кідірту',
    reset: 'Машинаны қалпына келтіру (жаңа базалық деңгей)',
    kCap: 'өлшем (1 = 1 сағ)', kBand: 'демодуляция жолағы',
    kSlip: 'сырғанау: табылған / нақты', kMargin: 'дабылға дейінгі қор',
    events: 'Оқиғалар', noEvents: 'әзірге жоқ — базалық деңгей жиналуда',
    wave: 'Шикі діріл (25 мс)',
    spec: 'Қаптама (envelope) спектрі + күтілетін ақау сызықтары',
    trend: 'Ақау баллының тренді, ерте базалық деңгейге қатысты (лог) — өнім сигналы',
    waiting: 'деректер күтілуде', likely: 'ықтимал {el} — SNR {snr}',
    noDefect: 'шу деңгейінен асатын ақау тарағы жоқ',
    healthy: 'САУ', suspect: 'КҮДІКТІ', faulted: 'АҚАУЛЫ',
    evWarn: '⚠ ескерту: {el} базадан 4× асты, тұрақты, {time} бастап',
    evAlarm: '⛔ дабыл: {el} базадан 10× асты, тұрақты, {time} бастап',
    simulated: '(симуляция)', warnLine: 'ескерту 4×', alarmLine: 'дабыл 10×',
    hoursAxis: 'жұмыс сағаты', ratioAxis: 'балл / база', hz: 'Гц',
  },
};

// Merge under STRINGS.<lang>.demo.* at runtime (i18n.js itself stays untouched).
for (const [l, d] of Object.entries(DEMO_STRINGS)) {
  try { STRINGS[l] = STRINGS[l] || {}; STRINGS[l].demo = d; }
  catch (e) { /* STRINGS frozen — we read DEMO_STRINGS directly anyway */ }
}

const $ = id => document.getElementById(id);
const fmt = (s, vars) => s.replace(/\{(\w+)\}/g, (_, k) => vars[k]);
const EL_COLORS = { BPFO: '#1d5fd1', BPFI: '#0f8a5f', BSF: '#c07a10', FTF: '#8a8a82' };
const ELEMENTS = ['BPFO', 'BPFI', 'BSF', 'FTF'];
const N_BASE = 12, WARN = 4, ALARM = 10, SUSTAIN = 3, START_HOUR = 8;
const FREQS = bearingFreqs(MACHINE.rpm, MACHINE.geometry.nBalls,
                           MACHINE.geometry.ballDia, MACHINE.geometry.pitchDia);

let lang = 'en';
try { lang = localStorage.getItem('lang') || 'en'; } catch (e) { /* no storage */ }
if (!DEMO_STRINGS[lang]) lang = 'en';
const T = () => DEMO_STRINGS[lang];

let seedN = 0;
let rng = makeRng(0x5EED + seedN);
let running = false, mode = 'auto', fault = 'outer', severity = 0;
let history = [], events = [], logged = { warn: false, alarm: false };
let lastDet = null;

// ------------------------------------------------------------------ charts
Chart.register(window['chartjs-plugin-annotation']);

const waveChart = new Chart($('wave'), {
  type: 'line',
  data: { labels: [], datasets: [{ data: [], borderColor: '#1d5fd1', borderWidth: 1, pointRadius: 0 }] },
  options: { responsive: true, maintainAspectRatio: false, animation: false,
    scales: { x: { display: false }, y: { ticks: { font: { size: 10 } } } },
    plugins: { legend: { display: false }, tooltip: { enabled: false } } },
});

const specChart = new Chart($('spec'), {
  type: 'line',
  data: { labels: [], datasets: [{ data: [], borderColor: '#26251f', borderWidth: 1, pointRadius: 0 }] },
  options: { responsive: true, maintainAspectRatio: false, animation: false,
    scales: { x: { type: 'linear', min: 0, max: 320,
                   title: { display: true, text: 'Hz', font: { size: 10 } }, ticks: { font: { size: 10 } } },
              y: { display: false } },
    plugins: { legend: { display: false }, tooltip: { enabled: false }, annotation: { annotations: {} } } },
});

const trendChart = new Chart($('trend'), {
  type: 'line',
  data: { labels: [], datasets: [] },
  options: { responsive: true, maintainAspectRatio: false, animation: false,
    scales: { x: { title: { display: true, text: 'machine hours', font: { size: 10 } },
                   ticks: { font: { size: 10 }, maxTicksLimit: 14 } },
              y: { type: 'logarithmic', min: 0.2,
                   title: { display: true, text: 'score / baseline', font: { size: 10 } } } },
    plugins: { legend: { labels: { boxWidth: 10, font: { size: 11 } } },
      annotation: { annotations: {
        warn: { type: 'line', yMin: WARN, yMax: WARN, borderColor: '#c07a10', borderWidth: 1, borderDash: [6, 4],
                label: { display: true, content: 'warn 4×', position: 'start', font: { size: 10 },
                         backgroundColor: 'rgba(0,0,0,0)', color: '#c07a10' } },
        alarm: { type: 'line', yMin: ALARM, yMax: ALARM, borderColor: '#a02c2c', borderWidth: 1, borderDash: [6, 4],
                 label: { display: true, content: 'alarm 10×', position: 'start', font: { size: 10 },
                          backgroundColor: 'rgba(0,0,0,0)', color: '#a02c2c' } },
      } } } },
});

// ------------------------------------------------------------------ helpers
function simTime(i) {              // capture i (0-based) -> "d1 08:00"
  const h = START_HOUR + i;
  return 'd' + (Math.floor(h / 24) + 1) + ' ' + String(h % 24).padStart(2, '0') + ':00';
}

function renderVerdict(det) {
  const t = T();
  $('verdict').className = 'verdict ' + det.verdict;
  $('v-text').textContent = t[det.verdict] || det.verdict.toUpperCase();
  $('v-detail').textContent = det.element
    ? fmt(t.likely, { el: det.element, snr: det.snr[det.element].toFixed(1) })
    : t.noDefect;
}

function renderLog() {
  const t = T();
  if (!events.length) {
    $('log').innerHTML = '<li style="color:var(--mut)">' + t.noEvents + '</li>';
    return;
  }
  $('log').innerHTML = events.slice().reverse().map(e =>
    '<li>' + fmt(t[e.level === 'alarm' ? 'evAlarm' : 'evWarn'],
                 { el: e.element, time: simTime(e.index) }) + '</li>').join('');
}

function checkCrossing(ratios, threshold, level) {
  if (logged[level]) return;
  const c = firstSustainedCrossing(ratios, threshold, SUSTAIN);
  if (c.index !== null) {
    logged[level] = true;
    events.push({ level, element: c.element, index: c.index });
    renderLog();
  }
}

function render(x, band, sp, det, ratios) {
  const t = T();
  $('clock').textContent = simTime(history.length - 1) + ' ' + t.simulated;
  $('k-cap').textContent = history.length;
  $('k-band').textContent = Math.round(band[0]) + '–' + Math.round(band[1]) + ' Hz';
  $('k-slip').textContent = det.slip.toFixed(3) + ' / ' + MACHINE.slip.toFixed(3);
  $('k-margin').textContent = det.margin.toFixed(2) + '×';
  renderVerdict(det);

  const w = [];                                       // first 640 samples (25 ms), decimated ×2
  for (let i = 0; i < 640 && i < x.length; i += 2) w.push(x[i]);
  waveChart.data.labels = w.map((_, i) => i);
  waveChart.data.datasets[0].data = w;
  waveChart.update();

  const sf = [], sa = [];                             // envelope spectrum, 0..320 Hz
  for (let i = 0; i < sp.f.length && sp.f[i] <= 320; i++) { sf.push(sp.f[i]); sa.push(sp.amp[i]); }
  specChart.data.labels = sf;
  specChart.data.datasets[0].data = sa;
  const s = det.slip || 1;                            // slip-scaled expected defect lines
  const lines = { BPFO: FREQS.BPFO * s, BPFI: FREQS.BPFI * s, BSF: 2 * FREQS.BSF * s, FTF: FREQS.FTF * s };
  const ann = {};
  for (const [k, fq] of Object.entries(lines)) {
    if (fq > 320) continue;
    ann[k] = { type: 'line', xMin: fq, xMax: fq, borderColor: EL_COLORS[k], borderWidth: 1.3,
               borderDash: [4, 3], label: { display: true, content: k === 'BSF' ? '2×BSF' : k,
               position: 'end', font: { size: 9 }, color: EL_COLORS[k], backgroundColor: 'rgba(0,0,0,0)' } };
  }
  specChart.options.plugins.annotation.annotations = ann;
  specChart.update();

  if (ratios) {
    trendChart.data.labels = ratios.map((_, i) => i + 1);
    trendChart.data.datasets = ELEMENTS.map(k => ({ label: k, data: ratios.map(r => r[k]),
      borderColor: EL_COLORS[k], borderWidth: 1.6, pointRadius: 0, tension: .25 }));
    trendChart.update();
  }
}

// ------------------------------------------------------------------ tick
function tick() {
  if (!running) return;
  try {
    if (mode === 'auto') {
      severity = Math.min(1, severity + 0.012 * (0.7 + 0.6 * rng()));
      $('sev').value = severity;
      $('sev-val').textContent = severity.toFixed(2);
    }
    const x = capture(fault, severity, rng);
    const band = pickBand(x, MACHINE.fs, FREQS);       // ~100-200 ms, acceptable per tick
    const sp = envelopeSpectrum(x, MACHINE.fs, band);
    const det = detect(sp.f, sp.amp, FREQS);
    history.push(det.scores);
    let ratios = null;
    if (history.length >= N_BASE) {
      ratios = trendRatios(history, N_BASE).ratios;
      checkCrossing(ratios, ALARM, 'alarm');
      checkCrossing(ratios, WARN, 'warn');
    }
    lastDet = det;
    render(x, band, sp, det, ratios);
  } catch (e) {
    console.error('capture failed:', e);
  }
}

// ------------------------------------------------------------------ controls
$('fault').onchange = () => { fault = $('fault').value; };
$('mode').onchange = () => { mode = $('mode').value; $('sev').disabled = mode !== 'manual'; };
$('sev').oninput = () => { severity = +$('sev').value; $('sev-val').textContent = severity.toFixed(2); };
$('run').onclick = () => { running = !running; $('run').textContent = running ? T().pause : T().start; };
$('reset').onclick = () => {
  seedN += 1;
  rng = makeRng(0x5EED + seedN * 99991);
  running = false; severity = 0;
  history = []; events = []; logged = { warn: false, alarm: false }; lastDet = null;
  $('run').textContent = T().start;
  $('sev').value = 0; $('sev-val').textContent = '0.00';
  $('clock').textContent = '—'; $('k-cap').textContent = '0';
  $('k-band').textContent = '—'; $('k-slip').textContent = '—'; $('k-margin').textContent = '—';
  $('verdict').className = 'verdict healthy';
  $('v-text').textContent = '—'; $('v-detail').textContent = T().waiting;
  waveChart.data.labels = []; waveChart.data.datasets[0].data = []; waveChart.update();
  specChart.data.labels = []; specChart.data.datasets[0].data = [];
  specChart.options.plugins.annotation.annotations = {}; specChart.update();
  trendChart.data.labels = []; trendChart.data.datasets = []; trendChart.update();
  renderLog();
};

// ------------------------------------------------------------------ language
function applyDemoStrings() {
  const t = T();
  document.querySelectorAll('[data-demo-i18n]').forEach(el => {
    const s = t[el.dataset.demoI18n];
    if (s != null) el.textContent = s;
  });
  document.title = t.title;
  document.documentElement.lang = lang;
  $('run').textContent = running ? t.pause : t.start;
  if (lastDet) renderVerdict(lastDet); else $('v-detail').textContent = t.waiting;
  renderLog();
  trendChart.options.plugins.annotation.annotations.warn.label.content = t.warnLine;
  trendChart.options.plugins.annotation.annotations.alarm.label.content = t.alarmLine;
  trendChart.options.scales.x.title.text = t.hoursAxis;
  trendChart.options.scales.y.title.text = t.ratioAxis;
  specChart.options.scales.x.title.text = t.hz;
  trendChart.update(); specChart.update();
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
}

function setLang(l) {
  if (!DEMO_STRINGS[l]) return;
  lang = l;
  try { localStorage.setItem('lang', l); } catch (e) { /* no storage */ }
  try { applyLang(l); } catch (e) { console.warn('applyLang failed:', e); }
  applyDemoStrings();
}

document.querySelectorAll('.lang-btn').forEach(b => { b.onclick = () => setLang(b.dataset.lang); });

// ------------------------------------------------------------------ init
fault = $('fault').value;
mode = $('mode').value;
$('sev').disabled = mode !== 'manual';
setLang(lang);
setInterval(tick, 1000);
