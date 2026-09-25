# Prospect research instructions (shared by all research agents)

Client: a freelance Dashboard Development Specialist (React/Next.js/Node/Python/FastAPI, Supabase/Postgres,
HubSpot, Salesforce, Shopify, WooCommerce, Stripe, n8n/Make/Zapier, OpenAI/AI agents, webhooks, custom APIs).
Builds: trading, sales, CRM, client-reporting, ecommerce/order, automation-monitoring, AI-agent-monitoring,
business-reporting, API-connected internal and multi-platform reporting dashboards.

## Tools / environment constraints
- ONLY the WebSearch tool works. WebFetch and curl to company websites are BLOCKED by network policy – do not try them.
- Every fact must come from WebSearch results (the result URLs + the result summary). Do NOT use memory to invent facts.

## Your job
Find the requested number of REAL companies for your category. For each company, run searches until you have:
1. Company website domain (from a result URL on that domain).
2. Evidence URL: an actual URL returned by WebSearch (company service page, case study, job post, blog, partner
   directory listing, Clutch/partner profile, etc.) that supports the dashboard/reporting/CRM/automation/integration need.
3. Contact (optional): a named person + title only if a search result shows it (e.g. team page, LinkedIn result title,
   press). Prioritise Founder/CEO/MD/COO/CTO/CRO/Head of Sales/RevOps/Ops/Data/Automation.
4. Business email (optional, but highly valuable): ONLY if the literal address appears in search results
   (e.g. search `"@domain.com"` or `companyname contact email`). Generic addresses (info@, hello@, contact@) are OK
   ONLY if the result shows that exact address as published. NEVER construct or guess an email from a pattern
   ("{first}@domain" formats do NOT count). Masked addresses (c**@) do NOT count.
   Record where it was seen in email_source (the result URL). Set email_status:
   - "Published on company site (via search index)" if the source URL is on the company's own domain
   - "Listed in third-party directory (verify before sending)" if seen on a directory/aggregator
   - "" if no email.
5. LinkedIn URLs only if a search result actually returned them; else "".

Spread geographically across: US, Canada, UK, Australia, Germany, Netherlands, Switzerland, Sweden, Norway,
Denmark, France, Ireland, Belgium, Austria, Singapore, New Zealand. Aim for no more than ~35% US.
Use country-specific queries (e.g. "HubSpot partner Netherlands", "Shopify Plus agency Sydney").

Efficiency: a single search often yields several companies (partner lists, "top agencies in X" articles) – use
those to discover names, then run 1–2 targeted searches per company for evidence and email
(e.g. `"companyname" reporting dashboard`, `"@companydomain" email`). Keep going until you reach the target.

## Output
Write a JSON array (UTF-8) to the output path you are given, with objects having EXACTLY these keys:
company_name, website (https://domain), country, city, industry, lead_category, company_description,
contact_name, job_title, business_email, email_source, email_status, linkedin, company_linkedin,
evidence_url, evidence_type (one of: Services page, Case study, Job posting, LinkedIn company page, Company blog,
Technology page, Public documentation, GitHub repository, Partner directory listing, Third-party profile, Press/News),
evidence_summary (1–2 sentences, factual, no exaggeration), likely_business_problem (exactly one of:
Client reporting, CRM visibility, Sales pipeline visibility, Data integration, Manual reporting, Automation monitoring,
AI agent monitoring, Ecommerce operations, Order monitoring, Business reporting, API monitoring, Multi client reporting,
Data quality, Internal operations, Trading analytics, Other), potential_dashboard_solution (specific, e.g.
"Multi Client HubSpot Dashboard", "Automation Monitoring Dashboard", "Shopify Order Dashboard"),
personalization_angle (one sentence starting "I noticed ..."), lead_quality (High/Medium/Low), notes.

Lead quality:
- High = strong direct evidence (relevant service/tech/business model) AND (an email found per rules above OR a named
  decision-maker contact).
- Medium = reasonable fit, less direct evidence, or strong evidence but no contact route.
- Low = relevant but little evidence of immediate need.
Leave any unverified field as "". Do not fabricate. Unknown city → "".
Write the file incrementally (rewrite the full array every ~10 companies) so progress is not lost.
Final message: just the count written and how many have emails.
