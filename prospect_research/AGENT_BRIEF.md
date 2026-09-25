# Prospect research brief (shared by all research agents)

Goal: find real, currently operating companies for outreach by Oseni Ibrahim (Trading Bot Developer:
trading dashboards, trading bots/automation, portfolio/risk/reporting dashboards, OMS/CRM dashboards,
API integrations for brokers, exchanges, crypto and fintech firms).

TOOLING CONSTRAINT: shell network access and WebFetch are BLOCKED. Only the WebSearch tool works.
All verification must come from WebSearch results returned in THIS session.

Rules (strict):
1. Every row must be backed by at least one WebSearch result URL you actually saw in your results
   (put it in "source"). "evidence" = a short factual statement drawn from that search result
   (what the company does / offers), not from memory.
2. Email: include ONLY if an email address appeared literally in your WebSearch output AND its domain
   matches the company's own domain (or is clearly the company's official address). Record where you
   saw it in "email_source". NEVER guess or construct emails (no info@/sales@ assumptions, no
   "email format" patterns from LeadIQ/RocketReach/etc). Obfuscated "[email protected]" = no email.
   Personal emails of individuals are NOT allowed; use generic business addresses (info@, sales@,
   partners@, support@, contact@, business@ ...).
3. "name": only a real named person if a search result shows them as founder/CEO/CTO/head of the
   company; otherwise empty string.
4. No duplicates within your file. Skip big-tech giants with no plausible need? No - include any
   genuine company in scope, but prefer small/mid firms that would plausibly hire a freelance developer.
5. Output: write JSON Lines to the file path you are given, one object per line with keys:
   company, website, country, industry, name, email, email_source, source, evidence, problem,
   opportunity, notes
   - website: root URL like https://example.com
   - country: HQ country (from search evidence where possible)
   - industry: short label e.g. "Crypto Exchange", "Forex/CFD Broker", "Trading Analytics",
     "Portfolio Management", "Wealth Tech", "OMS/EMS", "Risk Management", "Broker Technology",
     "Brokerage CRM", "Market Data/API", "Crypto Trading Bots", "Crypto Portfolio Tracker",
     "Prop Trading Firm", "Regtech/Reporting", "Algorithmic Trading", "Fintech Infrastructure"
   - problem: one sentence, specific plausible pain point tied to their product (phrase as likely/
     common need, not as a claimed fact)
   - opportunity: one sentence on what Oseni could build for them (dashboard, bot, API integration,
     risk monitor, reporting automation, CRM dashboard ...)
   - notes: anything useful (e.g. "email seen in search snippet", "contact form only")
6. Write/append incrementally (e.g. every ~15 rows) so progress is not lost. Use Bash with python or
   cat >> to append valid JSON lines. Validate at the end that every line parses as JSON.
7. Batch efficiently: search lists/directories ("top forex brokers Cyprus", "crypto exchanges
   Nigeria", "portfolio management software startups Germany") to discover many companies per
   query, then run targeted searches like "<company> contact email" to try to confirm emails.
   Diversify countries.
8. Report at the end: rows written, rows with email.
