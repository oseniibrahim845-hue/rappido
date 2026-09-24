# Solar prospect research spec (read fully before starting)

Goal: find REAL solar companies (installers, residential/commercial solar, EPC, solar+battery, solar roofing, solar financing, solar maintenance, solar consultation/lead-gen that sells to end customers) in your assigned region, with a PUBLICLY PUBLISHED business email.

## Tools
Direct website fetching is BLOCKED by network policy. Use only the WebSearch tool.
WebSearch returns a list of real links plus a model-written summary. The summary can be wrong.
Treat the "Links" list (titles + URLs) as the strongest evidence. Treat facts from the summary as weaker.

## Hard rules (accuracy beats volume)
- NEVER invent or guess an email, name, city, or fact. No pattern-built emails (e.g. firstname@domain) unless that exact address appears in a search result.
- Only use business emails (info@, sales@, hello@, contact@, enquiries@, office@, named work emails at the company domain). No gmail/hotmail/yahoo etc unless it's clearly the company's only published business address (then mark email_status "unconfirmed").
- Email must be on the company's own domain or clearly the company's published address.
- EMAIL VERIFICATION: for each email, run one exact-match search like `"info@example.com"` (or `"info@example.com" solar`). If results show a page on the company's site or a reputable listing containing that address, set email_status = "confirmed" and record email_source_url. If you only saw it in a summary and it could not be corroborated, set email_status = "unconfirmed". If none found, email = "" and email_status = "none".
- Contact person: only include first_name/full_name/job_title if a search result clearly states that person is the founder/owner/CEO/MD/GM/sales or ops manager of THIS company. Otherwise leave blank.
- Skip: manufacturers not selling direct, wholesalers/distributors, directories/marketplaces (EnergySage, Solar Reviews, Checkatrade...), news sites, government, universities, closed companies.
- Skip companies that are obviously the same business as another you already have (same domain).
- Yes/No/Unknown fields: say "Yes" only if a search result title/URL/snippet supports it (e.g. a URL like /get-a-quote, /book-consultation, /free-solar-quote, title "Request a Quote"). Otherwise "Unknown". Do not say "No" unless evidence shows it.
- crm: "Unknown" unless evidence (e.g. a job ad mentioning Salesforce/HubSpot, customer portal URL). Do not guess.
- company_size: only from evidence (e.g. "50+ employees per LinkedIn snippet", "installed 10,000 systems"); otherwise "Unknown".

## Search approach
Use many varied queries, e.g.:
- `solar installer <city> "get a quote"`, `solar panels <region> free consultation`, `solar company <state> contact email info@`
- `commercial solar installer <region>`, `solar battery installer <city>`, `roofing and solar <city>`
- `<company name> solar contact email`, `site:<domain> contact` (site: may work)
- Cover many different cities/regions in your area so companies are diverse. Include both big multi-location firms and small local installers.

## Output
Write ONE JSON file (array of objects) to the path you were given, using the Write tool. Update/overwrite it as you go (e.g. every ~15 companies) so progress is saved. Each object has EXACTLY these keys (strings; use "" or "Unknown" when not known):

{
 "company": "Official company name",
 "website": "https://domain.tld/",
 "country": "United States|Canada|United Kingdom|Australia|Germany|Netherlands|Ireland|New Zealand",
 "state": "state/province/county/region or ''",
 "city": "HQ city or ''",
 "first_name": "", "full_name": "", "job_title": "",
 "email": "",
 "email_status": "confirmed|unconfirmed|none",
 "email_source_url": "URL where the email was seen",
 "business_type": "e.g. Residential solar installer | Residential & commercial solar installer | Commercial solar EPC | Solar & battery installer | Roofing + solar contractor | Solar financing | Solar maintenance | Solar consultancy",
 "services": "short list, e.g. Solar PV, battery storage, EV chargers, heat pumps",
 "customer_type": "Residential | Commercial | Residential & Commercial | Agricultural... ",
 "company_size": "Unknown or evidence-based",
 "service_area": "e.g. Greater Phoenix; Northern California; UK-wide; Victoria",
 "locations": "e.g. '1 (Austin, TX)' or '5 offices: ...' or 'Unknown'",
 "quote_request": "Yes|Unknown",
 "consultation": "Yes|Unknown",
 "appointment_booking": "Yes|Unknown",
 "online_lead_form": "Yes|Unknown",
 "crm": "Unknown or evidence",
 "support_system": "e.g. 'Phone + email', 'Customer portal', 'Service/maintenance team', 'Unknown'",
 "marketing_channels": "e.g. 'Website quote form; phone' (only what you saw)",
 "sales_signal": "evidence of sales team/process or 'None found'",
 "lead_volume_signal": "evidence (multiple offices, many installs, large area) or 'None found'",
 "follow_up_signal": "evidence (multi-step quote -> survey -> proposal, financing application, etc.) or 'None found'",
 "automation_signal": "the manual process you infer from evidence, e.g. 'Quote form + phone-based consultation booking'",
 "automation_opportunity": "ONE primary pick based on evidence from: Lead qualification chatbot | Quote request automation | Appointment booking automation | Site survey scheduling | Lead routing | CRM automation | Quote follow up | Missed lead recovery | SMS follow up | Email follow up | WhatsApp automation | Sales notifications | Customer support automation | Lead scoring | CRM data entry | Sales reporting | Customer onboarding | Post installation follow up | Document processing | Internal AI assistant | Review request automation",
 "personalization_detail": "ONE concrete verifiable fact written in second person, e.g. 'Your site lets homeowners request a free solar quote online.'",
 "source_url": "most relevant real URL from search links (company page preferred)",
 "evidence": "concise factual evidence, e.g. 'Site has /get-a-quote page; offers solar + battery; offices in Sydney and Melbourne.'",
 "evidence_type": "e.g. Company website (quote page) | Company website (contact page) | Careers page | LinkedIn",
 "buying_intent": "High|Medium|Low (High = strong lead gen + multi-location/sales team/complex quote process; Medium = some lead gen; Low = little visible sales activity). Be discriminating; not all High.",
 "research_confidence": "High|Medium|Low",
 "notes": "anything uncertain"
}

Target: the number given to you, but accuracy is more important. If you can't verify enough, return fewer.
When done, reply with just: file path, count, count with confirmed email, and any issues.
