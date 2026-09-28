/* ==========================================================================
   Intrinio Market Intelligence Demo · Concept prototype
   --------------------------------------------------------------------------
   EVERYTHING ON THIS PAGE IS SIMULATED. No network requests are made for
   market data and no API credentials are used. Datasets are generated in the
   browser with a seeded random walk so they look realistic and stay stable
   between reloads.

   To connect a real data source later, replace the functions in the
   "DATA LAYER" section (getQuote / getSeries) with API calls; the rendering
   code only depends on the shapes they return. See README.md.
   ========================================================================== */

(() => {
  "use strict";

  /* ------------------------------------------------------------------------
     CONFIG
     ------------------------------------------------------------------------ */
  const CONFIG = {
    // Address used by the "Discuss Step 1" button. Leave empty to open a
    // blank email with the subject pre-filled.
    contactEmail: "",
    contactSubject: "Intrinio Market Intelligence Demo - Step 1 prototype",
    tickIntervalMs: 2500,        // how often simulated quotes move
    sectorThreshold: 45.0,       // % limit used by the Risk Monitor rule
  };

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------------------
     SIMULATED DATA
     ------------------------------------------------------------------------ */

  // Snapshot quotes. `prev` is the previous close used for daily change.
  const QUOTES = {
    SPX:     { label: "S&P 500",    name: "US large-cap index",  cls: "Index",  price: 6642.18,  prev: 6571.90,  dp: 2, ccy: "",  vol: 0.00035 },
    NDX:     { label: "NASDAQ 100", name: "US tech-heavy index", cls: "Index",  price: 24518.60, prev: 23901.90, dp: 2, ccy: "",  vol: 0.00045 },
    AAPL:    { label: "AAPL",       name: "Apple Inc.",          cls: "Equity", price: 232.10,   prev: 225.71,   dp: 2, ccy: "$", vol: 0.0006 },
    NVDA:    { label: "NVDA",       name: "NVIDIA Corp.",        cls: "Equity", price: 177.05,   prev: 168.87,   dp: 2, ccy: "$", vol: 0.0009 },
    MSFT:    { label: "MSFT",       name: "Microsoft Corp.",     cls: "Equity", price: 511.40,   prev: 515.50,   dp: 2, ccy: "$", vol: 0.0005 },
    SPY:     { label: "SPY",        name: "S&P 500 ETF",         cls: "ETF",    price: 668.20,   prev: 661.09,   dp: 2, ccy: "$", vol: 0.00035 },
    QQQ:     { label: "QQQ",        name: "Nasdaq-100 ETF",      cls: "ETF",    price: 596.80,   prev: 581.80,   dp: 2, ccy: "$", vol: 0.00045 },
    "BTC/USD": { label: "BTC/USD",  name: "Bitcoin / US Dollar", cls: "Crypto", price: 96680.00, prev: 92307.00, dp: 2, ccy: "$", vol: 0.0012 },
    "EUR/USD": { label: "EUR/USD",  name: "Euro / US Dollar",    cls: "FX",     price: 1.1742,   prev: 1.1768,   dp: 4, ccy: "",  vol: 0.0002 },
  };

  const OVERVIEW_SYMBOLS = ["SPX", "NDX", "AAPL", "NVDA", "BTC/USD", "EUR/USD"];
  const PREVIEW_SYMBOLS = [
    { sym: "SPX", label: "S&P 500" },
    { sym: "NDX", label: "NASDAQ" },
    { sym: "BTC/USD", label: "BTC/USD" },
    { sym: "AAPL", label: "AAPL" },
  ];

  // Per-symbol parameters for the main performance chart.
  // `ret` = total simulated return over each timeframe, `dvol` = daily volatility,
  // `adv` = average daily volume (shares, or coins for BTC).
  const SERIES_PARAMS = {
    AAPL:      { dvol: 0.015, adv: 52e6,  crypto: false, ret: { "1W": 0.018, "1M": 0.042, "3M": 0.096, "1Y": 0.148 } },
    NVDA:      { dvol: 0.028, adv: 210e6, crypto: false, ret: { "1W": 0.039, "1M": 0.075, "3M": 0.122, "1Y": 0.384 } },
    SPY:       { dvol: 0.009, adv: 68e6,  crypto: false, ret: { "1W": 0.009, "1M": 0.021, "3M": 0.053, "1Y": 0.162 } },
    QQQ:       { dvol: 0.012, adv: 42e6,  crypto: false, ret: { "1W": 0.016, "1M": 0.034, "3M": 0.078, "1Y": 0.215 } },
    "BTC/USD": { dvol: 0.030, adv: 28e3,  crypto: true,  ret: { "1W": 0.052, "1M": -0.031, "3M": 0.114, "1Y": 0.460 } },
  };

  // Sample portfolio. Cash + holdings = total portfolio value.
  const PORTFOLIO = {
    cash: 68564,
    holdings: [
      { symbol: "AAPL",    name: "Apple Inc.",          qty: 180 },
      { symbol: "NVDA",    name: "NVIDIA Corp.",        qty: 220 },
      { symbol: "MSFT",    name: "Microsoft Corp.",     qty: 60 },
      { symbol: "SPY",     name: "S&P 500 ETF",         qty: 45 },
      { symbol: "QQQ",     name: "Nasdaq-100 ETF",      qty: 40 },
      { symbol: "BTC",     name: "Bitcoin",             qty: 0.15, quote: "BTC/USD" },
    ],
  };

  // Look-through sector exposure of the invested portion (simulated).
  const SECTORS = [
    { name: "Technology", value: 58.3 },
    { name: "Financials", value: 11.6 },
    { name: "Healthcare", value: 10.2 },
    { name: "Energy",     value: 7.5 },
    { name: "Consumer",   value: 12.4 },
  ];

  const ORDERS = [
    {
      id: "ORD-10482", symbol: "AAPL", side: "BUY", qty: 50, price: 231.42, status: "Filled", type: "Limit",
      steps: [
        { title: "Order created", meta: "09:31:04.112 · Limit 50 @ 231.45" },
        { title: "Pre-trade risk check passed", meta: "09:31:04.130 · 3 rules evaluated" },
        { title: "Routed to venue", meta: "09:31:04.212 · Simulated venue" },
        { title: "Filled", meta: "09:31:05.806 · 50 / 50 @ 231.42" },
      ],
      current: 4,
    },
    {
      id: "ORD-10483", symbol: "NVDA", side: "BUY", qty: 20, price: 176.31, status: "Filled", type: "Market",
      steps: [
        { title: "Order created", meta: "10:02:47.520 · Market 20" },
        { title: "Pre-trade risk check passed", meta: "10:02:47.541 · 3 rules evaluated" },
        { title: "Routed to venue", meta: "10:02:47.598 · Simulated venue" },
        { title: "Filled", meta: "10:02:47.911 · 20 / 20 @ 176.31" },
      ],
      current: 4,
    },
    {
      id: "ORD-10484", symbol: "MSFT", side: "SELL", qty: 15, price: 512.20, status: "Pending", type: "Limit",
      steps: [
        { title: "Order created", meta: "11:15:09.004 · Limit 15 @ 512.20" },
        { title: "Pre-trade risk check passed", meta: "11:15:09.027 · 3 rules evaluated" },
        { title: "Routed to venue", meta: "11:15:09.101 · Working" },
        { title: "Awaiting fill", meta: "0 / 15 filled" },
      ],
      current: 4,
    },
  ];

  /* ------------------------------------------------------------------------
     HELPERS
     ------------------------------------------------------------------------ */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  const fmtNum = (v, dp = 2) =>
    v.toLocaleString("en-US", { minimumFractionDigits: dp, maximumFractionDigits: dp });
  const fmtMoney = (v, dp = 0) => (v < 0 ? "−$" : "$") + fmtNum(Math.abs(v), dp);
  const fmtSignedMoney = (v, dp = 0) => (v >= 0 ? "+$" : "−$") + fmtNum(Math.abs(v), dp);
  const fmtPct = (v, dp = 2) => (v >= 0 ? "+" : "−") + fmtNum(Math.abs(v), dp) + "%";
  const fmtQuote = (q, v = q.price) => q.ccy + fmtNum(v, q.dp);
  const fmtCompact = (v) =>
    v >= 1e9 ? fmtNum(v / 1e9, 2) + "B" :
    v >= 1e6 ? fmtNum(v / 1e6, 1) + "M" :
    v >= 1e3 ? fmtNum(v / 1e3, 1) + "K" : fmtNum(v, 0);

  const ARROW_UP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 15 6-6 6 6"/></svg>';
  const ARROW_DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';

  // Deterministic PRNG so datasets are stable between reloads.
  function mulberry32(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const hash = (str) => {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  };
  // Approximately normal random number (Box-Muller).
  const gauss = (rng) => Math.sqrt(-2 * Math.log(rng() || 1e-9)) * Math.cos(2 * Math.PI * rng());

  // Random walk forced to start at `start` and finish at `end` (a Brownian bridge).
  function bridge(start, end, n, stepVol, rng) {
    const logs = [0];
    for (let i = 1; i < n; i++) logs.push(logs[i - 1] + gauss(rng) * stepVol);
    const drift = Math.log(end / start);
    const last = logs[n - 1];
    return logs.map((l, i) => {
      const t = n === 1 ? 1 : i / (n - 1);
      return start * Math.exp(l - t * last + t * drift);
    });
  }

  function showToast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("is-visible");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => el.classList.remove("is-visible"), 2600);
  }

  // Most recent trading day (skip weekends) used to anchor chart labels.
  function lastTradingDay(crypto) {
    const d = new Date();
    d.setHours(16, 0, 0, 0);
    if (!crypto) while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
    return d;
  }
  function stepBackTradingDay(d, crypto) {
    const r = new Date(d);
    do { r.setDate(r.getDate() - 1); } while (!crypto && (r.getDay() === 0 || r.getDay() === 6));
    return r;
  }

  /* ------------------------------------------------------------------------
     DATA LAYER (swap these for real API calls in a production build)
     ------------------------------------------------------------------------ */

  const getQuote = (symbol) => QUOTES[symbol];

  // Intraday sparkline series for overview cards (random walk from prev close to price).
  const sparkCache = {};
  function getSparkSeries(symbol) {
    if (!sparkCache[symbol]) {
      const q = QUOTES[symbol];
      const rng = mulberry32(hash("spark:" + symbol));
      const dayMove = Math.abs(Math.log(q.price / q.prev));
      sparkCache[symbol] = bridge(q.prev, q.price, 48, Math.max(dayMove, q.vol * 6) / 5, rng);
    }
    return sparkCache[symbol];
  }

  // Price + volume series for the performance chart.
  const seriesCache = {};
  function getSeries(symbol, tf) {
    const key = symbol + "|" + tf;
    if (seriesCache[key]) return seriesCache[key];

    const p = SERIES_PARAMS[symbol];
    const q = QUOTES[symbol];
    const rng = mulberry32(hash(key));
    const crypto = p.crypto;

    // Timeframe layout: number of points, step length in "days", label builder.
    let n, stepDays, labels = [];
    const end = lastTradingDay(crypto);

    if (tf === "1D") {
      n = crypto ? 96 : 79;                 // 15-min (24h) or 5-min (09:30-16:00)
      stepDays = crypto ? 1 / 96 : 1 / 78;
      const startMin = crypto ? 0 : 9 * 60 + 30;
      const stepMin = crypto ? 15 : 5;
      for (let i = 0; i < n; i++) {
        const m = startMin + i * stepMin;
        labels.push(String(Math.floor(m / 60) % 24).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0"));
      }
    } else if (tf === "1W") {
      const days = crypto ? 7 : 5;
      const perDay = crypto ? 12 : 13;      // 2h bars (crypto) or 30-min bars
      n = days * perDay;
      stepDays = 1 / perDay;
      const dayList = [end];
      for (let i = 1; i < days; i++) dayList.unshift(stepBackTradingDay(dayList[0], crypto));
      dayList.forEach((d) => {
        for (let j = 0; j < perDay; j++) {
          const m = crypto ? j * 120 : 9 * 60 + 30 + j * 30;
          labels.push(
            d.toLocaleDateString("en-US", { weekday: "short", day: "numeric" }) + " " +
            String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0")
          );
        }
      });
    } else if (tf === "1Y") {
      n = 52; stepDays = crypto ? 7 : 5;
      let d = new Date(end);
      for (let i = 0; i < n; i++) { labels.unshift(d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "2-digit" })); d.setDate(d.getDate() - 7); }
    } else {
      n = tf === "1M" ? (crypto ? 30 : 22) : (crypto ? 90 : 64);
      stepDays = 1;
      let d = new Date(end);
      for (let i = 0; i < n; i++) { labels.unshift(d.toLocaleDateString("en-US", { month: "short", day: "numeric" })); d = stepBackTradingDay(d, crypto); }
    }

    const endPrice = q._snapshot ?? q.price;
    const start = tf === "1D" ? q.prev : endPrice / (1 + p.ret[tf]);
    const stepVol = p.dvol * Math.sqrt(stepDays);
    const prices = bridge(start, endPrice, n, stepVol, rng);

    // Volume: U-shaped intraday profile, larger on big moves.
    const barVolume = p.adv * stepDays;
    const volumes = prices.map((price, i) => {
      const prevP = i ? prices[i - 1] : start;
      const move = Math.abs(Math.log(price / prevP)) / stepVol;
      let shape = 1;
      if (tf === "1D" && !crypto) { const x = i / (n - 1); shape = 0.55 + 1.6 * Math.pow(2 * x - 1, 4); }
      return Math.round(barVolume * shape * (0.7 + 0.35 * move + 0.3 * rng()));
    });

    return (seriesCache[key] = { labels, prices, volumes, start });
  }

  /* ------------------------------------------------------------------------
     SPARKLINES (plain SVG, no library)
     ------------------------------------------------------------------------ */
  let sparkId = 0;
  function sparkSVG(svg, values, { up, width = 200, height = 44, baseline = null } = {}) {
    const min = Math.min(...values, baseline ?? Infinity);
    const max = Math.max(...values, baseline ?? -Infinity);
    const pad = 3;
    const x = (i) => (i / (values.length - 1)) * width;
    const y = (v) => pad + (1 - (v - min) / (max - min || 1)) * (height - pad * 2);
    const line = values.map((v, i) => (i ? "L" : "M") + x(i).toFixed(1) + " " + y(v).toFixed(1)).join(" ");
    const area = line + ` L${width} ${height} L0 ${height} Z`;
    const color = up ? "var(--up)" : "var(--down)";
    if (!svg.dataset.gid) svg.dataset.gid = "sg" + ++sparkId;
    const gid = svg.dataset.gid;
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("preserveAspectRatio", "none");
    svg.innerHTML = `
      <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${up ? "#2ebd85" : "#f0616d"}" stop-opacity=".22"/>
        <stop offset="1" stop-color="${up ? "#2ebd85" : "#f0616d"}" stop-opacity="0"/>
      </linearGradient></defs>
      ${baseline != null ? `<line x1="0" x2="${width}" y1="${y(baseline).toFixed(1)}" y2="${y(baseline).toFixed(1)}" stroke="var(--border)" stroke-dasharray="3 3" vector-effect="non-scaling-stroke"/>` : ""}
      <path d="${area}" fill="url(#${gid})"/>
      <path d="${line}" fill="none" stroke="${color}" stroke-width="1.75" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>`;
  }

  /* ------------------------------------------------------------------------
     HERO PREVIEW + MARKET OVERVIEW
     ------------------------------------------------------------------------ */
  function changeHTML(q) {
    const chg = q.price - q.prev;
    const pct = (chg / q.prev) * 100;
    const up = chg >= 0;
    return { up, pct, chg, html: `<span class="${up ? "is-up" : "is-down"}">${fmtPct(pct)}</span>` };
  }

  function buildPreview() {
    const list = $("#previewList");
    list.innerHTML = PREVIEW_SYMBOLS.map(({ sym, label }) => `
      <li class="preview__row" data-sym="${sym}">
        <div>
          <div class="preview__name">${label}</div>
          <div class="preview__desc">${QUOTES[sym].name}</div>
        </div>
        <svg class="preview__spark" aria-hidden="true"></svg>
        <div class="preview__vals">
          <div class="preview__price mono"></div>
          <div class="preview__chg mono"></div>
        </div>
      </li>`).join("");
    updatePreview();
  }

  function updatePreview() {
    $$(".preview__row").forEach((row) => {
      const q = QUOTES[row.dataset.sym];
      const c = changeHTML(q);
      $(".preview__price", row).textContent = fmtQuote(q);
      $(".preview__chg", row).innerHTML = c.html;
      sparkSVG($(".preview__spark", row), getSparkSeries(row.dataset.sym), { up: c.up, width: 88, height: 28 });
    });
    $("#previewClock").textContent = new Date().toLocaleTimeString("en-US", { hour12: false });
  }

  function buildOverview() {
    $("#tickerGrid").innerHTML = OVERVIEW_SYMBOLS.map((sym) => {
      const q = QUOTES[sym];
      return `
        <article class="card ticker" data-sym="${sym}">
          <div class="ticker__top">
            <div>
              <div class="ticker__sym">${q.label}</div>
              <div class="ticker__name">${q.name}</div>
            </div>
            <span class="ticker__class">${q.cls}</span>
          </div>
          <div class="ticker__mid">
            <div class="ticker__price mono"></div>
            <span class="pill ticker__chg"></span>
          </div>
          <svg class="ticker__spark" aria-hidden="true"></svg>
          <div class="ticker__foot mono"><span class="ticker__abs"></span><span>Prev ${fmtQuote(q, q.prev)}</span></div>
        </article>`;
    }).join("");
    updateOverview();
  }

  function updateOverview(changed = {}) {
    $$(".ticker").forEach((card) => {
      const sym = card.dataset.sym;
      const q = QUOTES[sym];
      const c = changeHTML(q);
      const priceEl = $(".ticker__price", card);
      priceEl.textContent = fmtQuote(q);
      if (changed[sym] && !reduceMotion) {
        priceEl.classList.remove("flash-up", "flash-down");
        void priceEl.offsetWidth; // restart transition
        priceEl.classList.add(changed[sym] > 0 ? "flash-up" : "flash-down");
        setTimeout(() => priceEl.classList.remove("flash-up", "flash-down"), 120);
      }
      const pill = $(".ticker__chg", card);
      pill.className = "pill ticker__chg mono " + (c.up ? "pill--up" : "pill--down");
      pill.innerHTML = (c.up ? ARROW_UP : ARROW_DOWN) + fmtPct(c.pct);
      $(".ticker__abs", card).textContent =
        (c.up ? "+" : "−") + q.ccy + fmtNum(Math.abs(c.chg), q.dp) + " today";
      sparkSVG($(".ticker__spark", card), getSparkSeries(sym), { up: c.up, baseline: q.prev });
    });
  }

  // Simulated "live" movement: small random steps, appended to each sparkline.
  function tick() {
    if (document.hidden) return;
    const changed = {};
    Object.keys(QUOTES).forEach((sym) => {
      const q = QUOTES[sym];
      const next = q.price * Math.exp(gauss(Math.random) * q.vol);
      changed[sym] = next - q.price;
      q.price = +next.toFixed(q.dp);
      const s = sparkCache[sym];
      if (s) { s.push(q.price); s.shift(); }
    });
    updatePreview();
    updateOverview(changed);
  }

  /* ------------------------------------------------------------------------
     PERFORMANCE CHART (Chart.js)
     ------------------------------------------------------------------------ */
  const chartState = { symbol: "AAPL", tf: "1M" };
  let priceChart = null;
  let volumeChart = null;
  const Y_AXIS_WIDTH = 64; // fixed so price and volume x-axes line up

  // Draws a vertical crosshair at the hovered index.
  const crosshairPlugin = {
    id: "crosshair",
    afterDatasetsDraw(chart) {
      const active = chart.getActiveElements();
      if (!active.length) return;
      const x = active[0].element.x;
      const { top, bottom } = chart.chartArea;
      const ctx = chart.ctx;
      ctx.save();
      ctx.strokeStyle = "rgba(163,172,186,0.35)";
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, bottom); ctx.stroke();
      ctx.restore();
    },
  };

  function syncHover(source, target, index) {
    if (!target) return;
    if (index == null) {
      target.setActiveElements([]);
      target.tooltip && target.tooltip.setActiveElements([], { x: 0, y: 0 });
    } else {
      target.setActiveElements([{ datasetIndex: 0, index }]);
    }
    target.update("none");
  }

  function initCharts() {
    if (typeof window.Chart === "undefined") {
      $("#chartFallback").hidden = false;
      $$(".chart-wrap, .chart-label-row").forEach((el) => (el.hidden = true));
      return false;
    }
    const Chart = window.Chart;
    Chart.defaults.font.family = "Inter, system-ui, sans-serif";
    Chart.defaults.font.size = 11.5;
    Chart.defaults.color = cssVar("--text-muted");
    Chart.defaults.borderColor = cssVar("--border-soft");

    const tooltipStyle = {
      backgroundColor: "#1b2130",
      borderColor: "#2e3746",
      borderWidth: 1,
      titleColor: cssVar("--text-secondary"),
      bodyColor: cssVar("--text-primary"),
      footerColor: cssVar("--text-secondary"),
      titleFont: { weight: "500" },
      bodyFont: { family: "JetBrains Mono, monospace", size: 12 },
      footerFont: { family: "JetBrains Mono, monospace", size: 11.5, weight: "400" },
      padding: 10,
      cornerRadius: 6,
      displayColors: false,
      caretSize: 0,
    };

    priceChart = new Chart($("#priceChart"), {
      type: "line",
      data: { labels: [], datasets: [{ data: [], borderWidth: 2, pointRadius: 0, pointHoverRadius: 4, pointHoverBorderWidth: 2, tension: 0.15, fill: true }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: reduceMotion ? false : { duration: 350 },
        interaction: { mode: "index", intersect: false },
        layout: { padding: { top: 4 } },
        scales: {
          x: { offset: true, grid: { display: false }, ticks: { maxTicksLimit: 7, maxRotation: 0, autoSkipPadding: 16 }, border: { display: false } },
          y: {
            position: "right",
            afterFit: (scale) => { scale.width = Y_AXIS_WIDTH; },
            grid: { color: "rgba(34,42,55,0.6)" },
            border: { display: false },
            ticks: { maxTicksLimit: 6, callback: (v) => fmtCompactPrice(v) },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            ...tooltipStyle,
            callbacks: {
              label: (ctx) => "Price   " + fmtQuote(QUOTES[chartState.symbol], ctx.parsed.y),
              footer: (items) => {
                const s = getSeries(chartState.symbol, chartState.tf);
                const i = items[0].dataIndex;
                const pct = ((s.prices[i] - s.start) / s.start) * 100;
                return ["Volume  " + fmtCompact(s.volumes[i]), "vs open " + fmtPct(pct)];
              },
            },
          },
        },
        onHover: (e, els) => syncHover(priceChart, volumeChart, els.length ? els[0].index : null),
      },
      plugins: [crosshairPlugin],
    });

    volumeChart = new Chart($("#volumeChart"), {
      type: "bar",
      data: { labels: [], datasets: [{ data: [], borderRadius: 2, borderSkipped: "bottom", barPercentage: 0.8, categoryPercentage: 0.9 }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: reduceMotion ? false : { duration: 350 },
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { display: false },
          y: { position: "right", afterFit: (scale) => { scale.width = Y_AXIS_WIDTH; }, grid: { display: false }, border: { display: false }, ticks: { maxTicksLimit: 2, callback: (v) => fmtCompact(v) } },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            ...tooltipStyle,
            callbacks: { label: (ctx) => "Volume  " + fmtCompact(ctx.parsed.y) },
          },
        },
        onHover: (e, els) => syncHover(volumeChart, priceChart, els.length ? els[0].index : null),
      },
      plugins: [crosshairPlugin],
    });

    // Clear the paired highlight when the pointer leaves either chart.
    [[priceChart, volumeChart], [volumeChart, priceChart]].forEach(([a, b]) =>
      a.canvas.addEventListener("mouseleave", () => syncHover(a, b, null))
    );
    return true;
  }

  function fmtCompactPrice(v) {
    const q = QUOTES[chartState.symbol];
    if (v >= 10000) return q.ccy + fmtNum(v / 1000, 1) + "K";
    return q.ccy + fmtNum(v, v >= 1000 ? 0 : 2);
  }

  function renderPerformance() {
    const { symbol, tf } = chartState;
    const s = getSeries(symbol, tf);
    const q = QUOTES[symbol];
    const last = s.prices[s.prices.length - 1];
    const chg = last - s.start;
    const pct = (chg / s.start) * 100;
    const up = chg >= 0;

    $("#chartPrice").textContent = fmtQuote(q, last);
    $("#chartChange").innerHTML =
      `<span class="pill mono ${up ? "pill--up" : "pill--down"}">${up ? ARROW_UP : ARROW_DOWN}${fmtPct(pct)}</span>` +
      ` <span class="mono ${up ? "is-up" : "is-down"}">${up ? "+" : "−"}${q.ccy}${fmtNum(Math.abs(chg), q.dp)}</span>` +
      ` <span style="color:var(--text-muted);font-size:12px">· ${tf === "1D" ? "today" : "past " + tf}</span>`;

    const avgVol = s.volumes.reduce((a, b) => a + b, 0) / s.volumes.length;
    $("#chartStats").innerHTML = [
      ["Open", fmtQuote(q, s.start)],
      ["High", fmtQuote(q, Math.max(...s.prices))],
      ["Low", fmtQuote(q, Math.min(...s.prices))],
      ["Avg volume / bar", fmtCompact(avgVol)],
    ].map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("");

    if (!priceChart) return;
    const lineColor = up ? "#2ebd85" : "#f0616d";
    const ds = priceChart.data.datasets[0];
    priceChart.data.labels = s.labels;
    ds.data = s.prices;
    ds.borderColor = lineColor;
    ds.pointHoverBackgroundColor = lineColor;
    ds.pointHoverBorderColor = cssVar("--surface-1");
    ds.backgroundColor = (ctx) => {
      const area = ctx.chart.chartArea;
      if (!area) return "transparent";
      const g = ctx.chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
      g.addColorStop(0, up ? "rgba(46,189,133,0.18)" : "rgba(240,97,109,0.18)");
      g.addColorStop(1, "rgba(0,0,0,0)");
      return g;
    };
    priceChart.update();

    const vds = volumeChart.data.datasets[0];
    volumeChart.data.labels = s.labels;
    vds.data = s.volumes;
    vds.backgroundColor = s.prices.map((p, i) =>
      p >= (i ? s.prices[i - 1] : s.start) ? "rgba(46,189,133,0.45)" : "rgba(240,97,109,0.45)"
    );
    vds.hoverBackgroundColor = s.prices.map((p, i) =>
      p >= (i ? s.prices[i - 1] : s.start) ? "#2ebd85" : "#f0616d"
    );
    volumeChart.update();
  }

  function bindChartControls() {
    $("#symbolSelect").addEventListener("change", (e) => {
      chartState.symbol = e.target.value;
      renderPerformance();
    });
    $$("#timeframeGroup button").forEach((btn) =>
      btn.addEventListener("click", () => {
        $$("#timeframeGroup button").forEach((b) => { b.classList.remove("is-active"); b.setAttribute("aria-pressed", "false"); });
        btn.classList.add("is-active");
        btn.setAttribute("aria-pressed", "true");
        chartState.tf = btn.dataset.tf;
        renderPerformance();
      })
    );
  }

  /* ------------------------------------------------------------------------
     PORTFOLIO
     ------------------------------------------------------------------------ */
  function computePortfolio() {
    const rows = PORTFOLIO.holdings.map((h) => {
      const q = QUOTES[h.quote || h.symbol];
      // Snapshot pricing: portfolio uses the opening snapshot, not the ticking quote.
      const price = q._snapshot ?? q.price;
      const value = h.qty * price;
      const dayPnl = h.qty * (price - q.prev);
      return { ...h, price, value, dayPnl, dayPct: ((price - q.prev) / q.prev) * 100, dp: q.dp };
    });
    const invested = rows.reduce((a, r) => a + r.value, 0);
    const total = invested + PORTFOLIO.cash;
    rows.forEach((r) => (r.weight = (r.value / total) * 100));
    const dayPnl = rows.reduce((a, r) => a + r.dayPnl, 0);
    return { rows, invested, total, dayPnl, cash: PORTFOLIO.cash };
  }

  let portfolio;
  const sortState = { key: "value", dir: "desc" };

  function renderKPIs() {
    const p = portfolio;
    const exposure = (p.invested / p.total) * 100;
    const cashPct = (p.cash / p.total) * 100;
    const dayPct = (p.dayPnl / (p.total - p.dayPnl)) * 100;
    const kpis = [
      { label: "Portfolio Value", value: fmtMoney(p.total), sub: `<span class="pill pill--up mono">${ARROW_UP}${fmtPct(dayPct)}</span> today` },
      { label: "Daily P&L", value: fmtSignedMoney(p.dayPnl), cls: p.dayPnl >= 0 ? "is-up" : "is-down", sub: "Realized + unrealized" },
      { label: "Exposure", value: fmtNum(exposure, 1) + "%", sub: fmtMoney(p.invested) + " invested" },
      { label: "Cash", value: fmtNum(cashPct, 1) + "%", sub: fmtMoney(p.cash) + " available" },
      { label: "Risk Score", value: "Moderate", sub: `<span class="pill pill--warn">5.8 / 10</span> 1 active alert` },
    ];
    $("#kpiGrid").innerHTML = kpis.map((k) => `
      <div class="card kpi">
        <div class="kpi__label">${k.label}</div>
        <div class="kpi__value ${k.label === "Risk Score" ? "" : "mono"} ${k.cls || ""}">${k.value}</div>
        <div class="kpi__sub">${k.sub}</div>
      </div>`).join("");

    $("#exposureValue").textContent = fmtNum(exposure, 1) + "%";
    requestAnimationFrame(() => ($("#exposureFill").style.width = exposure.toFixed(1) + "%"));
  }

  function renderHoldings() {
    const rows = [...portfolio.rows].sort((a, b) => {
      const va = a[sortState.key], vb = b[sortState.key];
      const cmp = typeof va === "string" ? va.localeCompare(vb) : va - vb;
      return sortState.dir === "asc" ? cmp : -cmp;
    });
    const maxW = Math.max(...portfolio.rows.map((r) => r.weight));

    $("#holdingsTable tbody").innerHTML = rows.map((r) => {
      const up = r.dayPnl >= 0;
      const qty = r.qty < 1 ? fmtNum(r.qty, 2) : fmtNum(r.qty, 0);
      return `
        <tr>
          <td class="t-left"><div class="sym-cell">
            <span class="sym-cell__logo" aria-hidden="true">${r.symbol.slice(0, 2)}</span>
            <div><div class="sym-cell__sym">${r.symbol}</div><div class="sym-cell__name">${r.name}</div></div>
          </div></td>
          <td>${qty}</td>
          <td>$${fmtNum(r.price, 2)}</td>
          <td>$${fmtNum(r.value, 0)}</td>
          <td class="${up ? "is-up" : "is-down"}">${fmtSignedMoney(r.dayPnl)} <small style="opacity:.75">(${fmtPct(r.dayPct)})</small></td>
          <td><span class="weight-cell"><span class="weight-bar" aria-hidden="true"><span style="width:${(r.weight / maxW) * 100}%"></span></span>${fmtNum(r.weight, 1)}%</span></td>
        </tr>`;
    }).join("");

    const p = portfolio;
    $("#holdingsTable tfoot").innerHTML = `
      <tr>
        <td class="t-left" style="font-family:var(--font-sans)">Total invested · Cash ${fmtMoney(p.cash)}</td>
        <td></td><td></td>
        <td>$${fmtNum(p.invested, 0)}</td>
        <td class="${p.dayPnl >= 0 ? "is-up" : "is-down"}">${fmtSignedMoney(p.dayPnl)}</td>
        <td>${fmtNum((p.invested / p.total) * 100, 1)}%</td>
      </tr>`;

    $$("#holdingsTable th[data-sort]").forEach((th) => {
      const active = th.dataset.sort === sortState.key;
      th.classList.toggle("is-sorted", active);
      if (active) th.setAttribute("aria-sort", sortState.dir === "asc" ? "ascending" : "descending");
      else th.removeAttribute("aria-sort");
    });
  }

  function renderAllocation() {
    const p = portfolio;
    const items = [...p.rows]
      .sort((a, b) => b.weight - a.weight)
      .map((r) => ({ label: r.symbol, weight: r.weight, value: r.value }));
    items.push({ label: "Cash", weight: (p.cash / p.total) * 100, value: p.cash, cash: true });
    const max = Math.max(...items.map((i) => i.weight));
    $("#allocList").innerHTML = items.map((i) => `
      <li class="alloc-row">
        <span><strong style="font-weight:600">${i.label}</strong></span>
        <span class="alloc-row__bar ${i.cash ? "alloc-row__bar--cash" : ""}" aria-hidden="true"><span style="width:0" data-w="${(i.weight / max) * 100}"></span></span>
        <span class="alloc-row__val">${fmtNum(i.weight, 1)}% · ${fmtMoney(i.value)}</span>
      </li>`).join("");
  }

  function animateAllocation() {
    requestAnimationFrame(() =>
      $$("#allocList [data-w]").forEach((el) => (el.style.width = el.dataset.w + "%"))
    );
  }

  function bindSorting() {
    $$("#holdingsTable th[data-sort]").forEach((th) => {
      th.tabIndex = 0;
      const activate = () => {
        const key = th.dataset.sort;
        if (sortState.key === key) sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
        else { sortState.key = key; sortState.dir = key === "symbol" ? "asc" : "desc"; }
        renderHoldings();
      };
      th.addEventListener("click", activate);
      th.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activate(); } });
    });
  }

  // Generic accessible tabs: `onChange(tab)` is called after switching.
  function bindTabs(tabs, getPanel, onChange) {
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        getPanel(t).hidden = !on;
      });
      if (focus) tab.focus();
      onChange && onChange(tab);
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        const next = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
        select(next, true);
      });
    });
  }

  /* ------------------------------------------------------------------------
     RISK
     ------------------------------------------------------------------------ */
  function renderRisk() {
    const colors = ["--series-1", "--series-2", "--series-3", "--series-4", "--series-5"].map(cssVar);
    const tech = SECTORS[0];
    $("#techCurrent").textContent = fmtNum(tech.value, 1) + "%";

    const legend = $("#sectorLegend");
    legend.innerHTML = SECTORS.map((s, i) => `
      <li data-i="${i}">
        <span class="legend__swatch" style="background:${colors[i]}"></span>
        <span>${s.name}</span>
        <span class="legend__val">${fmtNum(s.value, 1)}%</span>
        <span class="legend__flag" ${s.value > CONFIG.sectorThreshold ? 'title="Above threshold"' : ""}>${s.value > CONFIG.sectorThreshold ? "▲" : ""}</span>
      </li>`).join("");

    const setCenter = (i) => {
      const s = SECTORS[i];
      $("#sectorCenter").textContent = fmtNum(s.value, 1) + "%";
      $("#sectorCenter").nextElementSibling.textContent = s.name;
      $$("li", legend).forEach((li) => li.classList.toggle("is-dim", +li.dataset.i !== i));
    };
    const resetCenter = () => {
      setCenter(0);
      $$("li", legend).forEach((li) => li.classList.remove("is-dim"));
    };
    resetCenter();

    // Volatility & drawdown sparklines (simulated history).
    const rng = mulberry32(hash("risk"));
    const volSeries = bridge(15.8, 18.6, 60, 0.035, rng);
    sparkSVG($("#volSpark"), volSeries, { up: false, height: 48 });
    let peak = 100, level = 100;
    const dd = [];
    for (let i = 0; i < 90; i++) {
      level *= Math.exp(gauss(rng) * 0.009 + (i > 35 && i < 60 ? -0.0028 : 0.0012));
      peak = Math.max(peak, level);
      dd.push(((level - peak) / peak) * 100);
    }
    sparkSVG($("#ddSpark"), dd, { up: false, height: 48 });

    if (typeof window.Chart === "undefined") {
      $(".doughnut-wrap canvas").replaceWith(Object.assign(document.createElement("div"), {
        style: `width:180px;height:180px;border-radius:50%;background:conic-gradient(${SECTORS.map((s, i, a) => {
          const from = a.slice(0, i).reduce((x, y) => x + y.value, 0), to = from + s.value;
          return `${colors[i]} ${from}% ${to}%`;
        }).join(",")});-webkit-mask:radial-gradient(circle,transparent 58%,#000 59%);mask:radial-gradient(circle,transparent 58%,#000 59%)`,
      }));
      return;
    }

    const chart = new window.Chart($("#sectorChart"), {
      type: "doughnut",
      data: {
        labels: SECTORS.map((s) => s.name),
        datasets: [{
          data: SECTORS.map((s) => s.value),
          backgroundColor: colors,
          borderColor: cssVar("--surface-1"),
          borderWidth: 2,
          hoverBorderColor: cssVar("--surface-1"),
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        layout: { padding: 6 },
        animation: reduceMotion ? false : { duration: 500 },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#1b2130", borderColor: "#2e3746", borderWidth: 1, padding: 10, cornerRadius: 6,
            bodyFont: { family: "JetBrains Mono, monospace", size: 12 },
            callbacks: { label: (ctx) => ` ${ctx.label}  ${fmtNum(ctx.parsed, 1)}%` },
          },
        },
        onHover: (e, els) => (els.length ? setCenter(els[0].index) : resetCenter()),
      },
    });
    chart.canvas.addEventListener("mouseleave", resetCenter);

    // Legend hover highlights the matching segment.
    $$("li", legend).forEach((li) => {
      const i = +li.dataset.i;
      li.addEventListener("mouseenter", () => {
        chart.setActiveElements([{ datasetIndex: 0, index: i }]);
        chart.update("none");
        setCenter(i);
      });
      li.addEventListener("mouseleave", () => {
        chart.setActiveElements([]);
        chart.update("none");
        resetCenter();
      });
    });
  }

  /* ------------------------------------------------------------------------
     ORDERS
     ------------------------------------------------------------------------ */
  function renderOrders() {
    const body = $("#ordersBody");
    body.innerHTML = ORDERS.map((o, i) => {
      const filled = o.status === "Filled";
      return `
        <tr tabindex="0" data-i="${i}" aria-label="${o.side} ${o.qty} ${o.symbol}, ${o.status}. Show lifecycle">
          <td class="t-left"><div class="sym-cell"><span class="sym-cell__logo" aria-hidden="true">${o.symbol.slice(0, 2)}</span><div><div class="sym-cell__sym">${o.symbol}</div><div class="sym-cell__name mono">${o.id}</div></div></div></td>
          <td class="t-left"><span class="side side--${o.side.toLowerCase()}">${o.side}</span></td>
          <td>${o.qty} shares</td>
          <td>$${fmtNum(o.price, 2)}</td>
          <td><span class="pill ${filled ? "pill--up" : "pill--warn"}" style="font-family:var(--font-sans)">
            ${filled
              ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
              : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'}
            ${o.status}</span></td>
        </tr>`;
    }).join("");

    const select = (i) => {
      const o = ORDERS[i];
      $$("tr", body).forEach((tr) => tr.classList.toggle("is-selected", +tr.dataset.i === i));
      $("#lifecycleTitle").textContent = `${o.side} ${o.qty} ${o.symbol}`;
      $("#lifecycleSub").textContent = `${o.id} · ${o.type} order · ${o.status}`;
      $("#lifecycleSteps").innerHTML = o.steps.map((s, idx) => {
        const state = idx < o.current - (o.status === "Filled" ? 0 : 1) ? "is-done" : idx === o.current - 1 ? "is-current" : "is-todo";
        return `<li class="${state}"><span class="timeline__dot" aria-hidden="true"></span>
          <div class="timeline__title">${s.title}</div><div class="timeline__meta">${s.meta}</div></li>`;
      }).join("");
    };

    $$("tr", body).forEach((tr) => {
      tr.addEventListener("click", () => select(+tr.dataset.i));
      tr.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(+tr.dataset.i); } });
    });
    select(0);
  }

  /* ------------------------------------------------------------------------
     CODE PREVIEW + COPY
     ------------------------------------------------------------------------ */
  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) { /* fall through to legacy path */ }
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:-1000px;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
    ta.remove();
    return ok;
  }

  function bindCode() {
    const tabs = $$(".code-tabs button");
    bindTabs(tabs, (t) => $("#code-" + t.dataset.code));

    const btn = $("#copyBtn");
    btn.addEventListener("click", async () => {
      const active = tabs.find((t) => t.classList.contains("is-active"));
      const text = $("#code-" + active.dataset.code).textContent;
      const ok = await copyText(text);
      const label = $("span", btn);
      $("#copyStatus").textContent = ok ? "Copied to clipboard" : "Copy failed. Select the code and copy manually.";
      if (ok) {
        btn.classList.add("is-copied");
        label.textContent = "Copied";
        clearTimeout(bindCode._t);
        bindCode._t = setTimeout(() => {
          btn.classList.remove("is-copied");
          label.textContent = "Copy Example";
          $("#copyStatus").textContent = "";
        }, 2200);
      }
    });
  }

  /* ------------------------------------------------------------------------
     NAVIGATION
     ------------------------------------------------------------------------ */
  function bindNav() {
    const toggle = $("#navToggle");
    const links = $("#navLinks");
    const setOpen = (open) => {
      links.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };
    toggle.addEventListener("click", () => setOpen(!links.classList.contains("is-open")));
    links.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    document.addEventListener("click", (e) => {
      if (links.classList.contains("is-open") && !e.target.closest(".nav")) setOpen(false);
    });

    // Highlight the nav link for the section in view.
    const navLinks = $$('#navLinks a[href^="#"]:not(.btn)');
    const byId = Object.fromEntries(navLinks.map((a) => [a.getAttribute("href").slice(1), a]));
    const sections = Object.keys(byId).map((id) => document.getElementById(id)).filter(Boolean);
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((a) => a.classList.remove("is-active"));
        byId[entry.target.id].classList.add("is-active");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach((s) => io.observe(s));
  }

  function bindCTA() {
    const btn = $("#ctaBtn");
    const href = `mailto:${encodeURIComponent(CONFIG.contactEmail)}?subject=${encodeURIComponent(CONFIG.contactSubject)}`;
    btn.setAttribute("href", href);
    btn.addEventListener("click", () => showToast("Opening your email client…"));
  }

  /* ------------------------------------------------------------------------
     INIT
     ------------------------------------------------------------------------ */
  function init() {
    // Freeze the snapshot price used by the portfolio before quotes start ticking.
    Object.values(QUOTES).forEach((q) => (q._snapshot = q.price));

    bindNav();
    buildPreview();
    buildOverview();

    initCharts();
    bindChartControls();
    renderPerformance();

    portfolio = computePortfolio();
    renderKPIs();
    renderHoldings();
    renderAllocation();
    bindSorting();
    bindTabs(
      $$('.tabs [role="tab"]'),
      (t) => document.getElementById(t.getAttribute("aria-controls")),
      (t) => { if (t.id === "tab-allocation") animateAllocation(); }
    );

    renderRisk();
    renderOrders();
    bindCode();
    bindCTA();

    setInterval(tick, CONFIG.tickIntervalMs);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
