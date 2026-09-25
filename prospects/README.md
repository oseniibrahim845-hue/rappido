# Dashboard Development Prospects

**Status: incomplete. 515 qualified leads, not the 700 target.** The file names keep the requested `_700` suffix, but only 515 records passed quality control. Read the Limitations section before using this list for outreach.

## Files

| File | Contents |
|---|---|
| `Dashboard_Development_Prospects_700.xlsx` | Two sheets. **Prospects** has 515 rows and the 23 requested columns, with filters, frozen headers, clickable links and colour-coded Lead Quality. **Summary** has the counts. |
| `Dashboard_Development_Prospects_700.csv` | The same 515 rows (UTF-8 with BOM, so it opens cleanly in Excel). |
| `raw/cat01.json` … `raw/cat15.json` | Raw research output for each category, before quality control. |
| `raw/RESEARCH_INSTRUCTIONS.md` | The rules every research agent followed. |
| `raw/build.py` | Merges, dedupes and validates the raw files, then writes the XLSX and CSV. Run it with `python3 raw/build.py <output_dir>`. |

## Final validation

| Metric | Count |
|---|---|
| Total prospects | **515** |
| Unique companies | 515 |
| Unique domains | 471 (44 leads have no confirmed website) |
| Unique emails | 14 |
| Leads with a public business email | **14** |
| – published on the company's own site (seen via search index) | 11 |
| – seen in search, source page not confirmed | 1 |
| – third-party directory or LinkedIn listing only | 2 |
| Leads without an email | **501** |
| Leads with a named contact | 20 |
| High quality | **25** |
| Medium quality | **295** |
| Low quality | **195** |
| Raw records collected | 532 |
| Removed in quality control | 17 (15 duplicates, 2 outside the target countries: Cyprus, UAE) |

### Leads by category

| # | Category | Leads | High | Medium | Low |
|---|---|---|---|---|---|
| 1 | HubSpot / CRM Partner | 71 | 0 | 51 | 20 |
| 2 | RevOps / CRM Consulting | 41 | 0 | 24 | 17 |
| 3 | Marketing Agency | 24 | 5 | 12 | 7 |
| 4 | SEO / PPC Agency | 14 | 9 | 3 | 2 |
| 5 | Automation Agency | 55 | 3 | 31 | 21 |
| 6 | AI Automation / AI Agents | 44 | 0 | 40 | 4 |
| 7 | B2B SaaS | 10 | 0 | 2 | 8 |
| 8 | Sales Outsourcing / Lead Generation | 19 | 2 | 8 | 9 |
| 9 | Shopify / Ecommerce Agency | 61 | 0 | 28 | 33 |
| 10 | Ecommerce Brand / Operator | 8 | 3 | 1 | 4 |
| 11 | Sales Team / Large CRM Pipeline | 13 | 0 | 0 | 13 |
| 12 | API / Integration Company | 60 | 0 | 30 | 30 |
| 13 | Trading / Fintech | 16 | 3 | 3 | 10 |
| 14 | BI / Reporting Consultancy | 61 | 0 | 61 | 0 |
| 15 | Technology / Operations Company | 18 | 0 | 1 | 17 |

### Leads by country

Germany 58, Australia 51, Netherlands 46, United Kingdom 43, Switzerland 34, Sweden 32, Canada 27, France 24, Norway 23, New Zealand 20, Ireland 19, Denmark 18, Singapore 17, Austria 11, Belgium 9, United States 7, not confirmed 76.

The US is under-represented. Research deliberately spread across the non-US target countries first, and the search budget ran out before the US-focused passes. Many of the 76 leads with no confirmed country are probably US companies.

## Research methodology

1. The work was split across 15 research agents, one per lead category. Each ran in parallel under the same written rules (`raw/RESEARCH_INSTRUCTIONS.md`).
2. Agents used web search with category- and country-specific queries, for example "HubSpot partner Netherlands", "Shopify Plus agency Sydney", "Power BI consultancy Zürich", "Workato partner", "n8n agency", "prop firm trader dashboard", "Salesforce consultancy RevOps" and "SEO agency monitatliches Reporting".
3. Discovery results (partner directories, "top agencies" articles, service pages) produced candidate companies. A company was kept only when a search result on its own domain, or a credible third-party page about it, supported a dashboard, reporting, CRM, automation, integration or monitoring need.
4. For each kept company the agent recorded the exact result URL as the **Evidence URL**. It wrote the **Evidence Summary**, **Likely Business Problem** (from your fixed list), a specific **Potential Dashboard Solution** and a one-sentence **Personalization Angle** starting "I noticed…".

## How evidence was collected

- **The environment's network policy blocked direct website fetching.** Every company website returned an egress block, so pages could not be opened and read in full. All facts come from **search-engine results**: the result URLs and the search tool's summaries of those pages.
- Evidence URLs are real URLs returned by search. Most are the company's own service, partner or case-study pages. Some are job postings (Greenhouse, Lever, Ashby), partner directories (Workato, Shopify Plus agency case studies) or press coverage.
- Nothing came from memory. One exception was caught: the Technology / Operations agent filled countries from general knowledge. QC blanked those countries and wrote the suggested value into Notes.

## Quality rules applied (`raw/build.py`)

- **Deduplication:** by root domain (so `www.` and subdomains collapse), by normalised company name (legal suffixes like GmbH, Ltd and B.V. ignored) and by email. The earlier record wins.
- **Emails:**
  - Only addresses that literally appeared in search results are kept.
  - No address was guessed or built from a naming pattern. `{first}@domain` formats and masked addresses (`c**@…`) were rejected.
  - Consumer domains (gmail, outlook and similar), no-reply, privacy and legal addresses, malformed and duplicate emails are removed automatically.
  - Every email carries an **Email Source** URL and an **Email Status**:
    - *Published on company site (via search index)*: the address was seen for a page on the company's own domain.
    - *Seen in search index, source page unconfirmed*: the page it came from could not be pinned down.
    - *Listed in third-party directory (verify before sending)*: seen on LeadIQ or LinkedIn, not on the company's site.
    - *Not found*: no email was found.
  - All 14 emails are generic inboxes (info@, contact@, kontakt@, hello@, enquiries@, wholesale@) published by the company. None is a personal address.
- **Lead Quality:**
  - **High** requires strong direct evidence **and** a published email or a named decision-maker. The build downgrades any "High" that lacks both.
  - **Medium** means a clear service or technology fit but no contact route, or less direct evidence.
  - **Low** means relevant but thin evidence (for example only a page title), a very large company, or an unconfirmed website. Every lead without a confirmed website is capped at Low.
- **Unverified fields are left blank.** That covers contact, job title, LinkedIn, city and country when search results did not confirm them. Notes explain each gap.
- The evidence URL must be a real `http(s)` result URL, and the country must be blank or one of the 16 target countries.

## Limitations (please read)

1. **Only 515 of the 700 leads were collected.** The session has a hard limit of **200 web searches**, shared by all research agents, and it ran out partway through research. Categories that searched company by company ended up small: B2B SaaS (10), Ecommerce Brands (8), Sales Teams (13), SEO/PPC (14), Trading/Fintech (16) and Technology/Operations (18). Categories that found companies through list pages went over 55. No filler records were added to reach 700.
2. **Emails are scarce: 14 of 515.** Most agents used their searches on discovery and evidence, and the budget ran out before the per-company `"@domain"` email searches. The Business Email column is empty for 501 leads rather than guessed.
3. **Named contacts are scarce: 20 of 515.** Some came from search summaries (for example the Kit & Kin founder and the prop-firm founders) and should be checked on LinkedIn before outreach.
4. **Pages were not opened.** Because websites could not be fetched, each Evidence Summary rests on a search-result summary of the page, not a full read. Open the Evidence URL before sending. Rows marked "only page title seen" in Notes are the weakest.
5. **Locations are sometimes approximate.** A few companies are listed under a city landing page rather than a confirmed head office; Notes flags these. 76 leads have no confirmed country and 44 no confirmed website.
6. **Some "companies" are large.** Reed, Penske Logistics, Viessmann, SoundCloud and a few others are big organisations where a freelance dashboard offer is a long shot. They are marked Low or noted.

## How to finish the list to 700 and add emails

The quickest route is a second research run in an environment with:

- **A higher search limit.** The setting is `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, configured in the environment settings.
- **Network access that allows fetching company websites.** Set the environment's Network access to a broader level, so contact and imprint pages can be read directly and emails confirmed on the page.

With both in place, the next pass would:

- **Top up the weak categories:** B2B SaaS, Ecommerce Brands, Sales Teams, SEO/PPC, Trading/Fintech, Technology/Ops, Marketing and Sales Outsourcing, plus more US leads.
- **Enrich the existing 515 leads:** named decision-makers and published emails, especially the 295 Medium leads, which mostly lack only a contact route.

---

## Apps Script sender file (`Dashboard_Outreach_Sender.xlsx`)

This is built by `python3 raw/export_outreach.py` from the prospect CSV plus the email-enrichment results in `raw/enrichment/`. Both sheets have exactly these headers in row 1:
`Name, Company, Website, Email, Subject, Body, Status, Country, Industry, Source, Notes`.

- **Send Ready** (first sheet): 110 prospects that have a public business email, ready for the Apps Script.
- **Needs Email**: 405 prospects with no verified email yet. The Email cell is blank, and each row already has its Subject and Body. They sit on a separate sheet so the sender does not try to email blank addresses.
- **Status** is blank on every row.
- **Subject and Body** are complete, personalised emails with no placeholders, signed by Oseni Ibrahim, Trading Bot Developer, ibrahimoseni063@gmail.com.
- **Source** is the URL where the email was seen. For rows without an email, it is the evidence URL.
- **Notes** has the lead ID, category, quality, evidence URL and email status. 17 emails come only from a third-party profile and are marked "verify before sending".
- **Email enrichment** used one targeted web search per lead for 184 High/Medium leads, and found 97 new emails. Only literal addresses from search results were accepted: no pattern guessing, no masked addresses, and no consumer, no-reply, privacy, legal or careers inboxes. An email's domain must match the company website, unless the company's own page shows it as an alias.
- **QC result:** 515 prospects, 110 with an email, 405 without, 0 duplicate emails removed, 1 invalid email removed (Passion Digital: the domain did not match the site and the source page was unconfirmed).
