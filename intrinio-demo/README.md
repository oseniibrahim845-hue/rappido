# Intrinio Market Intelligence Demo

**Concept prototype · Simulated data**

A single-page, responsive front-end prototype showing how market data could be turned into an interactive, customer-facing financial dashboard. It is meant as a Step 1 proof of concept for a marketing demo and as an example of front-end, data-visualisation and API-presentation work.

> This is an independent concept for discussion. It is **not** an official Intrinio product, and Intrinio did not commission or endorse it. **No live data is used.** Every price, volume, portfolio figure and risk metric is generated in the browser.

---

## What the prototype demonstrates

| Section | What it shows |
|---|---|
| **Navigation** | Sticky nav, highlights the section in view, mobile menu, "Demo Environment" status |
| **Hero** | Headline, calls to action, and a compact market snapshot that updates every few seconds |
| **Market Overview** | Six instrument cards (index, equity, crypto, FX) with sparklines that update with small random price moves |
| **Market Performance** | Chart.js price and volume charts with a symbol selector, 1D/1W/1M/3M/1Y timeframes, linked hover crosshair and tooltips |
| **Portfolio Intelligence** | KPI tiles, a sortable holdings table and an allocation view. The totals are calculated from the holdings |
| **Risk & Exposure** | Exposure meter, sector doughnut with an interactive legend, volatility and drawdown trends, and a rule-based alert |
| **Order Management** | Recent orders. Select one to see its lifecycle (created → risk check → routed → filled). Nothing is ever submitted |
| **API Workflow** | A conceptual data → processing → analytics → dashboard → reporting pipeline |
| **API Code Preview** | Editor-style card with a JS workflow and a sample response shape. The "Copy Example" button copies the code |
| **Data to Product / CTA / Footer** | Use cases, a "Discuss Step 1" email link, and the disclaimers |

## All data is simulated

- The values are defined in the `SIMULATED DATA` section of `script.js` (`QUOTES`, `SERIES_PARAMS`, `PORTFOLIO`, `SECTORS`, `ORDERS`).
- Chart histories use a seeded random walk (a Brownian bridge), so each dataset is realistic, ends at the snapshot price, and stays the same between reloads.
- The page makes no market-data requests, uses no API keys, and connects to no brokerage account.
- The code example is illustrative only. `getMarketData()` and the other function names are placeholders, not real Intrinio endpoints.

## How to run

No build step and no backend.

1. Open `index.html` in any modern browser (double-clicking it works), **or**
2. Serve the folder locally, for example `npx serve .` or `python3 -m http.server`, then open the printed URL.

Chart.js 4 and the Inter / JetBrains Mono fonts load from public CDNs. Without an internet connection the page still works: the fonts fall back to system fonts, the sector chart is drawn with CSS, and a note replaces the performance chart. To run fully offline, download `chart.umd.js` next to `index.html` and change the `<script>` `src`.

```
intrinio-demo/
├── index.html   # markup for all sections
├── style.css    # design tokens (:root) + components + responsive rules
├── script.js    # simulated data, data layer, rendering, interactions
└── README.md
```

To customise:

- **Contact button:** set `CONFIG.contactEmail` at the top of `script.js`.
- **Colours:** edit the CSS custom properties in `:root` in `style.css`.
- **Instruments / holdings:** edit the arrays in the `SIMULATED DATA` section.

## Connecting a real API later

The rendering code reads data only through a small data layer in `script.js`:

| Function | Returns | Replace with |
|---|---|---|
| `getQuote(symbol)` | `{ price, prev, dp, ccy, ... }` | a real-time or delayed quote endpoint |
| `getSparkSeries(symbol)` | `number[]` (intraday closes) | an intraday price endpoint |
| `getSeries(symbol, tf)` | `{ labels, prices, volumes, start }` | historical price / volume bars for the timeframe |
| `tick()` | updates quotes on a timer | a WebSocket or streaming subscription |

A production integration would typically:

1. **Keep the API key on a server.** A small backend or serverless proxy calls the data provider, caches the responses, and passes only the fields the page needs to the browser. Keys never reach the client.
2. **Make the data layer async** (`await getSeries(...)`) and add loading, empty and error states.
3. **Map provider responses** into the shapes above in a single adapter, so the UI code stays the same.
4. **Stream quotes** over WebSockets rather than by polling, and throttle UI updates.
5. **Show data provenance and licensing** clearly, for example "15-min delayed" or "real-time", with timestamps.

## Possible next steps for production

- **Step 1 (this prototype):** refine the visuals and copy for a marketing page or embeddable demo.
- **Step 2:** connect one or two real endpoints (quotes and historical prices) through a secure proxy, using sandbox or delayed data.
- **Step 3:** port to a component framework (React, Vue or Svelte) and add tests, accessibility audits and performance budgets.
- **Step 4:** add real features such as watchlists, a fundamentals panel, screeners, and exportable reports.
- Also: analytics events for marketing, a light theme, i18n and number formatting per locale, and an embeddable widget build.

---

*Demo only. Data shown is simulated. Built as a technical proof of concept.*
