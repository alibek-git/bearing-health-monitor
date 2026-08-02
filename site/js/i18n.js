// site/js/i18n.js — trilingual strings + language plumbing for the landing page.
// Usage (module script):
//   import { STRINGS, applyLang, detectLang } from "./js/i18n.js";
//   applyLang(detectLang());

export const STRINGS = {
  en: {
    title: "Bearing Health Monitor — know which bearing is failing, before it stops the line",
    hero_h1: "Know which bearing is failing — before it stops the line",
    hero_sub: "Wireless vibration monitoring for heavy industry — assembled and supported in Kazakhstan.",
    hero_cta: "See the live demo",
    fig_cap: "Defect-score trend vs early-life baseline: warn at 4×, alarm at 10×.",
    p1_h: "Validated on public datasets",
    p1_p: "On NASA IMS run-to-failure data the detector names the failing element and raises a sustained alarm about 2.5 days before the bearing dies — roughly 2 days before its neighbours on the same shaft.",
    p1_note: "Measured on one bearing on one test rig. Longer lead times are expected from the physics but are not yet validated by us.",
    p2_h: "Physics first, not a black box",
    p2_p: "Works from day one with zero training data. Every verdict is explainable: which bearing element is damaged, and what margin is left to the alarm threshold.",
    p3_h: "Built and supported locally",
    p3_p: "Assembled in Karaganda, with interfaces and support in Russian and Kazakh. Works with legacy equipment.",
    how_h: "How it works",
    s1: "A sensor on the bearing housing",
    s2: "Envelope analysis of the vibration signal",
    s3: "Trend against an early-life baseline",
    s4: "Alert in Telegram or WhatsApp before failure",
    foot_contact: "Contact",
    foot_note: "The demo runs a synthetic machine in your browser, using the same detection algorithm as the product.",
  },
  ru: {
    title: "Bearing Health Monitor — узнайте, какой подшипник выходит из строя, до остановки линии",
    hero_h1: "Узнайте, какой подшипник выходит из строя — до остановки линии",
    hero_sub: "Беспроводной мониторинг вибрации для тяжёлой промышленности. Сборка и поддержка — в Казахстане.",
    hero_cta: "Посмотреть живое демо",
    fig_cap: "Тренд дефект-балла относительно базовой линии: предупреждение при 4×, тревога при 10×.",
    p1_h: "Проверено на открытых данных",
    p1_p: "На данных NASA IMS с испытаний до разрушения детектор называет повреждённый элемент и поднимает устойчивую тревогу примерно за 2,5 суток до отказа — и примерно на 2 суток раньше соседних подшипников на том же валу.",
    p1_note: "Измерено на одном подшипнике на одном стенде. Физика допускает и больший запас времени, но нами это пока не подтверждено.",
    p2_h: "Физика, а не «чёрный ящик»",
    p2_p: "Работает с первого дня, без обучающих данных. Каждый вердикт объясним: какой элемент подшипника повреждён и какой запас остаётся до порога тревоги.",
    p3_h: "Сделано и поддерживается здесь",
    p3_p: "Сборка в Караганде, интерфейс и поддержка на русском и казахском языках. Работает со старым парком оборудования.",
    how_h: "Как это работает",
    s1: "Датчик на корпусе подшипника",
    s2: "Анализ огибающей вибросигнала",
    s3: "Тренд относительно базовой линии",
    s4: "Оповещение в Telegram или WhatsApp до отказа",
    foot_contact: "Контакт",
    foot_note: "Демо запускает синтетическую машину прямо в браузере — с тем же алгоритмом обнаружения, что и в продукте.",
  },
  kk: {
    title: "Bearing Health Monitor — қай мойынтірек істен шығып жатқанын желі тоқтағанға дейін біліңіз",
    hero_h1: "Қай мойынтірек істен шығып жатқанын желі тоқтағанға дейін біліңіз",
    hero_sub: "Ауыр өнеркәсіпке арналған сымсыз діріл мониторингі. Құрастыру мен қолдау — Қазақстанда.",
    hero_cta: "Тікелей демоны көру",
    fig_cap: "Ақау балының бастапқы деңгейге қатысты тренді: 4× — ескерту, 10× — дабыл.",
    p1_h: "Ашық деректерде тексерілген",
    p1_p: "NASA IMS-тің бұзылғанға дейінгі сынақ деректерінде детектор зақымдалған элементті дәл атап, істен шығудан шамамен 2,5 тәулік бұрын тұрақты дабыл береді — сол біліктегі көрші мойынтіректерден шамамен 2 тәулік бұрын.",
    p1_note: "Бір стендтегі бір мойынтіректе өлшенген. Физика бойынша қор уақыты одан да ұзақ болуы мүмкін, бірақ біз оны әлі растаған жоқпыз.",
    p2_h: "«Қара жәшік» емес — физика",
    p2_p: "Бірінші күннен бастап оқыту деректерінсіз жұмыс істейді. Әр қорытынды түсінікті: мойынтіректің қай элементі зақымдалған және дабыл шегіне дейін қанша қор бар.",
    p3_h: "Жергілікті өндіріс пен қолдау",
    p3_p: "Құрастыру — Қарағандыда. Интерфейс пен қолдау орыс және қазақ тілдерінде. Ескі жабдықпен де жұмыс істейді.",
    how_h: "Қалай жұмыс істейді",
    s1: "Мойынтірек корпусындағы датчик",
    s2: "Діріл сигналының конверттік талдауы",
    s3: "Бастапқы деңгейге қатысты тренд",
    s4: "Істен шығудан бұрын Telegram немесе WhatsApp арқылы хабарлама",
    foot_contact: "Байланыс",
    foot_note: "Демо синтетикалық машинаны браузеріңізде тікелей іске қосады — өнімдегі дәл сол анықтау алгоритмімен.",
  },
};

// Pick the startup language: saved choice first, then the browser locale
// (kk -> kk; ru/be/uk -> ru; anything else -> en).
export function detectLang() {
  try {
    const saved = localStorage.getItem("lang");
    if (saved && STRINGS[saved]) return saved;
  } catch (e) { /* storage unavailable (private mode etc.) */ }
  const nav = ((typeof navigator !== "undefined" && navigator.language) || "en").toLowerCase();
  if (nav.startsWith("kk")) return "kk";
  if (/^(ru|be|uk)/.test(nav)) return "ru";
  return "en";
}

// Fill every [data-i18n] element with the string for `lang`, mark the active
// [data-lang] switcher button, and persist the choice.
export function applyLang(lang) {
  if (!STRINGS[lang]) lang = "en";
  const t = STRINGS[lang];
  document.documentElement.lang = lang;
  for (const el of document.querySelectorAll("[data-i18n]")) {
    const key = el.getAttribute("data-i18n");
    if (key in t) el.textContent = t[key];
  }
  for (const btn of document.querySelectorAll("[data-lang]")) {
    const active = btn.getAttribute("data-lang") === lang;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", String(active));
  }
  try { localStorage.setItem("lang", lang); } catch (e) { /* non-fatal */ }
  return lang;
}
