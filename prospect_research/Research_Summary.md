# Research Summary: Trading Bot and Business Dashboard Prospects

**Date:** 2026-09-28
**Deliverable:** `Trading_Bot_and_Business_Dashboard_Prospects.xlsx` (sheet "Prospects", exact 15 headers, Status left blank)

> **Read this first.** This session ran under a restrictive network policy. Company websites, careers pages and job boards were blocked (HTTP 403 at the egress proxy). Only github.com (through WebFetch) and pypi.org were reachable. Web search was capped at 200 queries for the whole session, and that cap was used up early. So most evidence comes from **search-engine result text for the cited URLs**, or from **public GitHub/PyPI data**, not from pages opened directly. Every record's Notes column says how it was verified. Re-check each live site before sending.

## Totals

| Metric | Count |
|---|---|
| **Total qualified prospects** | **113** |
| Trading prospects | 74 |
| Dashboard / business-software prospects | 39 |
| Strong evidence (active-need signal, e.g. current hiring, open integration request, live RFP) | 23 (10 trading, 13 dashboard) |
| Lower-confidence (fit-based, no active-need signal; labelled at the start of Notes) | 23 |
| Verified public email (address re-confirmed in QA on a GitHub org profile or PyPI package metadata) | 20 |
| No verified email (Email cell left blank) | 93 |
| Unverified candidate emails (left out of the Email column; shown in Notes) | 6 |
| Named contact (person tied to company by a public source) | 3 |
| Hiring evidence | 32 (14 trading, 18 dashboard) |
| Product evidence | 83 (66 trading, 17 dashboard) |
| Integration evidence | 103 (72 trading, 31 dashboard) |
| Existing-software evidence | 97 (71 trading, 26 dashboard) |
| Rejected (all reasons) | 191 (see `Rejected_Prospects.md`) |
| Removed as duplicates | 2 (FXSSI found by two segments and merged into one record; one duplicate caught by an agent) |
| Removed in final QA | 12: 5 with no confirmable official website, 7 with evidence too thin |

The 500-prospect target was **not** reached, and no records were added to pad the count.

## Countries represented

United States (21), United Kingdom (8), Australia (5), Germany (4), Switzerland (4), Netherlands (4), United Arab Emirates (4), Canada (3), Estonia (3), Spain (2), France (2), Cyprus (2), Singapore, Luxembourg, Lithuania, Indonesia, Colombia, Argentina (1 each).
**Country not verified: 45.** These cells are left blank rather than guessed.

## Prospect categories represented

**Trading (74):**
- Crypto trading / bot platforms: 13
- Trading technology vendors (broker CRM, MT plugins, prop-tech white-label): 12
- Trading software companies (copiers, journals, bridges): 9
- Trading API companies / exchanges: 7
- Algorithmic / quant firms that are hiring: 6
- Prop firms: 5
- TradingView automation platforms: 5
- Trading educators: 4
- Signal providers: 4
- Brokers: 3
- Forex software: 2
- Portfolio trackers: 2
- EA vendor: 1
- Broker CRM: 1

**Dashboard (39):**
- Reporting-dashboard agencies/products: 11
- SaaS platforms (fintech, wealth, integrations): 10
- Custom software / automation agencies: 5
- CRM dashboards: 4
- Analytics dashboards: 3
- Operations dashboards: 3
- Internal software: 3

## Main opportunity types discovered

1. **New exchange/broker/platform connectors.** Examples: REST/WebSocket adapters (Nautilus Bitget RFC, Rotki exchange requests, Hummingbot connector bounties), SDK samples, and cTrader/Match-Trader/TradeLocker support for copiers and bridges.
2. **Contract MQL4/MQL5 and MetaTrader API work.** Examples: MT4/MT5 Manager/Server API roles (Axi, HFM, Equiti), an MQL developer opening (FXSSI), an MT4 port of an MT5-only product (TradeSgnl), and an MT5 sync EA for journals.
3. **Prop-firm trader dashboards and rule/risk monitoring.** Relevant to firms adding platforms (Hola Prime, PineX Capital), to prop firms that are hiring (Tradeify, MyFunded Futures), and to white-label prop-tech vendors that may subcontract.
4. **Broker CRM ↔ MT5 reporting layers.** Deposits, trading activity and IB data in one view, for Forex CRM vendors.
5. **Frontend/dashboard contract capacity for fintech and wealth platforms.** Portfolio dashboards, investor portals, and customer dashboards or internal CRMs (Valitana, HC Global, doola, Nevis, Prospera).
6. **Subcontracted reporting dashboards for agencies.** HubSpot/RevOps and Zoho partners, white-label reporting tools.
7. **Integration and internal-tools builds at operating companies.** Shopify/ERP/Salesforce links, warehouse monitoring, restaurant reporting apps, and one public school-district RFP for a data dashboard (due 16 Oct 2026).

## Important patterns discovered

- **Integration debt is the most repeated signal.** Trading products keep adding platforms (MT4 → MT5 → cTrader → Match-Trader → TradeLocker → DXtrade), and each one means a new connector plus ongoing maintenance.
- **Crypto bot platforms shipped SDKs and MCP/AI-agent servers in 2026** (Cryptohopper, 3Commas, WunderTrading, Altrady, Bit2Me, SnapTrade). That creates demand for SDK maintenance, samples and monitoring.
- **Open-source trading projects list their integration gaps publicly** (GitHub issues). These are the most verifiable "needs" in the dataset.
- **Broker tech hiring focuses on the MT4/MT5 Manager/Server API**, not EA writing, so integration and reporting skills matter more than strategy coding.
- **Dashboard hiring evidence clusters in fintech/wealth SaaS.** Agencies (RevOps/HubSpot, Zoho) show fit but rarely an explicit need.
- Several trading-tech vendors (Takeprofit Tech, TradeToolsFX, prop-tech white-labels) are **part-competitors**. Their emails pitch overflow or subcontract capacity rather than a direct build.

## Research limitations

1. **Page fetching blocked.** The egress proxy returned 403 for company sites, ATS boards (Greenhouse, Ashby, Lever, Workable), LinkedIn, Indeed, Wellfound, Built In, eFinancialCareers and the MQL5 site. Evidence therefore relies on search-result text and GitHub/PyPI.
2. **Web-search cap.** The session was limited to 200 WebSearch calls across all 9 research agents, and it was used up early. Coverage is thin in: non-US job boards (Seek, Reed, StepStone), MT4-only EA vendors, market makers, accounting/FP&A and insurance-tech, healthcare/logistics/property operations, and AI-agent-ops startups.
3. **Posting dates** were mostly not visible, so job-based evidence may be stale. Notes flag every such case.
4. **Emails are conservative.**
   - Only addresses I re-confirmed on a public page are in the Email column.
   - Six addresses seen only in search snippets (Tradeify, North Kansas City Schools, PineConnector, MetaCopier, Duplikium, Heron Copier) are in Notes, marked UNVERIFIED.
   - One verified email is a Gmail address (Aurora Trading). It is the company's published contact, but check it before use.
5. **Official domains not opened.** For HFM, Axi and Equiti the research recorded job-board URLs. The Website column uses the brokers' official domains (hfm.com, axi.com, equiti.com), which were not opened in this session.
6. **Company size.** Some prospects are mid-to-large (FundedNext, ShipMonk, Formlabs, HFM, Axi). They are included because the evidence is specific, but freelancer fit is lower.

## Emails and signature

Every Body ends with "Best regards," so your mail client's signature (name and links) follows it. No sender name was invented and no placeholders remain. Every email is built from the evidence in its row: none claims past clients, results or trading performance.

## Recommended next research (when search/fetch access allows)

- Non-US broker and prop-firm job boards: Cyprus (CyprusWork), UAE, Seek AU, eFinancialCareers. Leads to re-check: Hantec Trader MT4/MT5 integration developer role (Dubai), Instant Funding, Funding Pips, FXIFY.
- MQL5 Market and EA vendors' own sites, for MT4-only products (MT5 conversion leads). Trader Dale, EarnForex, EA Builder Pro, TradersConnect, TradeCopier.cloud were listed but not verified.
- Public RFP portals (school districts, municipalities, nonprofits) for dashboard and portal builds. These give the clearest "active need" evidence.
- Contact pages of the 93 no-email prospects, to find business emails once the sites can be opened.
