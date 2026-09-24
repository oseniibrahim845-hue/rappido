# Lead research brief (read fully before starting)

You are researching REAL B2B companies for a cold-outreach list. The sender builds OpenClaw-based AI agents that
automate invoice tracking, payment follow-ups, AR, reconciliation, finance reporting, and CRM/ERP/accounting updates.

## Tooling constraints
- Direct website fetching (WebFetch/curl) is BLOCKED by the network policy. Use **WebSearch only**.
- WebSearch returns titles/URLs plus a summary. Treat a fact as verified only if it is supported by the results
  (prefer results from the company's own domain; LinkedIn, Crunchbase, G2, Capterra, app marketplaces, official
  registries, and reputable press are acceptable secondary sources).
- Efficient tactic: use list-style searches ("top e-invoicing providers Germany", "bookkeeping firms Manchester Xero partner")
  to discover candidates, then one targeted search per company, e.g. `"<company>" contact email` or
  `"@<domain>" <company>` or `<company> founder CEO`, to confirm website, location, contact person and email.

## Hard rules (non-negotiable)
1. Never invent a company, person, email, fact, or URL. If unsure, leave the field empty.
2. EMAIL: only record an email if the exact address appears in search results AND its domain matches (or is clearly
   owned by) the company. Role addresses (info@, hello@, contact@, sales@, support@, finance@) are fine.
   NEVER construct an email from a name pattern. No gmail/yahoo/hotmail etc. If none found -> "" (empty).
   In "email_source" put the URL of the result where the email appeared.
3. PERSON: only record contact_full_name/first_name/job_title if a search result clearly names that person in that role
   at this company (founder, CEO, MD, CFO, COO, managing partner, head of finance/ops/product...). Otherwise empty.
4. Skip companies already in the exclusion file: /tmp/claude-0/-home-user-rappido/fe5a4016-459b-5738-a814-2abcc5b6e35f/scratchpad/master_companies.txt
   (one "company | domain" per line). Also do not duplicate within your own output. One row per company.
5. Skip: restaurants, hotels, retail, freelancers, unverifiable firms, companies without a business website, and
   companies acquired/shut down (if a brand was absorbed, use the surviving company only if it fits).
6. Personalization must be a concrete, evidenced fact about THIS company (product feature, service line,
   integrations, niche, market). No generic praise. No claims that they "lack automation".
7. Buying intent: be honest. High = strong evidence (automation product/complex workflows/many integrations/large B2B
   base/hiring finance or automation roles). Medium = relevant with clear finance workflow. Low = relevant but weak evidence.
   A realistic mix is expected; do not mark everything High.
8. Forbidden words in any text you write: seamless, tailored, stunning, revolutionize, game changer, cutting edge,
   unlock, supercharge, transform your business.

## Output
Append one JSON object per line (JSONL) to YOUR output file (path given in your task). Write in chunks of ~10 rows as
you go (e.g. `cat >> file <<'JSONL' ... JSONL` via Bash, or python) so work is never lost. Valid JSON only, UTF-8, one
object per line. Fields (all strings; use "" when unknown):

{
 "company": "Official company/brand name",
 "website": "https://domain.tld (homepage, no tracking params)",
 "country": "e.g. United States / United Kingdom / Germany / Netherlands / France / Canada / Australia / Switzerland / Austria / Belgium / Ireland / Sweden / Denmark / Norway / Finland / other",
 "state": "state/region/county if known",
 "city": "HQ city if known",
 "company_type": "EXACTLY one of: Invoicing Software | Accounting Software | Accounts Receivable Software | E-Invoicing | Billing & Subscription Management | Accounting & Bookkeeping Firm | ERP Implementation & Consulting | Payments & Fintech | Business Management Software | Financial Administration Services",
 "industry": "short, e.g. 'SaaS - AR automation', 'Accounting services', 'B2B payments'",
 "invoice_product_or_service": "what they offer that touches invoices/billing/finance (1 sentence)",
 "accounting_platform": "accounting platforms they integrate with or work in (e.g. 'Xero, QuickBooks Online, Sage') if evidenced",
 "erp": "ERPs they integrate/implement (e.g. 'NetSuite, SAP S/4HANA, Microsoft Dynamics 365 BC') if evidenced",
 "payment_platform": "payment rails/providers if evidenced (e.g. 'Stripe, GoCardless')",
 "company_size": "employee range if evidenced (e.g. '11-50' from LinkedIn)",
 "linkedin": "company LinkedIn URL if it appeared in results, else ''",
 "contact_full_name": "", "first_name": "", "job_title": "",
 "email": "", "email_source": "",
 "buying_intent": "High | Medium | Low",
 "automation_opportunity": "Starts with 'Potential opportunity: automate ...' - specific to their workflow",
 "personalization_detail": "One factual sentence, e.g. 'The company provides outsourced bookkeeping for UK e-commerce brands on Xero.'",
 "personalization_reason": "Why that detail matters for an invoice/finance automation pitch (1 sentence)",
 "personalized_opening": "One natural sentence starting 'I noticed that <Company> ...' or 'I saw that <Company> ...' referencing the detail",
 "subject_line": "Specific short subject (<= 8 words), vary wording between rows, mention company or workflow",
 "workflow_phrase": "short noun phrase that completes 'there may be an opportunity to automate ___' e.g. 'overdue invoice follow ups and weekly AR summaries for client accounts'",
 "source_url": "best URL supporting the evidence (prefer company's own page)",
 "evidence": "1-2 sentences of what the source shows",
 "evidence_type": "EXACTLY one of: Website | Product page | Pricing page | LinkedIn | Company page | Documentation | Press release | Job posting",
 "research_confidence": "High (company+website+email+evidence verified) | Medium (company+website verified, contact limited) | Low",
 "notes": "anything the reviewer should know (e.g. 'email seen in search result for contact page', acquisitions, uncertainty)"
}

Work until you reach your target row count (or the market genuinely runs out - then say so). Quality over quantity.
Prefer companies where you can find a published professional email. Final message: number of rows written, how many
with email, and any issues. Keep the final message short.

## SEARCH BUDGET (important)
Each agent has a hard cap of ~200 WebSearch calls. Budget about 3 searches per company: reuse list/directory
searches that return many candidates at once, and combine confirmation into one query where possible
(e.g. `"<company>" <city> email contact founder`). Do not spend more than 5 searches on any single company:
if the email is not found by then, write the row with an empty email and move on. Write rows as you go.
