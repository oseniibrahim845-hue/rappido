# Research brief: European AI content & social media automation prospects

You are researching real European businesses that could pay for AI social media automation and AI content creation (AI UGC-style videos, AI product images, short-form video, scheduling and repurposing, DM and lead workflows with n8n, Make or Zapier). The sender is **Oseni Ibrahim, AI Automation & Content Creation Developer**.

**Do NOT send any email. Research only.**

## Hard rules (a record that breaks any of these is worthless)
1. **Never invent** a business, person, email, URL, product, campaign, post, date or problem. Everything must come from a search result you actually saw.
2. **Never guess an email pattern.** Don't use first.last@ and the like unless the exact address appears in a source. Contact-data vendor pages don't count as a source: ContactOut, RocketReach, ZoomInfo, Apollo, LeadIQ, Clay, Lusha, SignalHire, Anymailfinder, Hunter, Prospectoo, Snov, Adapt, UpLead, Seamless, Datanyze, Kaspr, GetProspect, emailformat sites, and any "email format" or masked-email page.
3. **An individual email is required for Ready.** It must be a named person's own work address (e.g. `anna@brand.com`, `j.smith@agency.co.uk`). It must be shown next to that person's name or role on the company's own site, or on a legitimate public page: press release, conference bio, association directory, the person's own portfolio, or a published interview. hello@/info@/kontakt@/press@ and similar inboxes are **Generic**. Still record them, with `email_type: "Generic"`.
4. The decision-maker's name and role must come from the company's own site or a credible public source. Allowed roles are founder, co-founder, CEO, owner, managing director/Geschäftsführer/gérant, CMO, marketing director/head of marketing, head of growth, e-commerce director/manager, creative director, content/social media director, or marketing operations. For estate agents, a branch director/owner or marketing manager also counts. For hotels: GM, director of sales & marketing, or marketing manager.
5. **The observation is a specific, checkable fact**, with its URL. Examples: a named product launch or collection, a named campaign, an active job ad for a UGC creator, social media manager or video editor (give the date), a named service, listing videos, an event series, a weekly menu. Don't make claims about their social media that you couldn't see. Never say they lack video or post rarely unless a source shows it. Phrase the opportunity as an idea, not a criticism.
6. **One company = one record.** Before adding a company, check the existing files under `eu-ai-content-leads/work/*.jsonl` (grep the domain) and the exclusion list `eu-ai-content-leads/work/exclude_domains.txt`.
7. Use only active businesses with real commercial operations, so no hobby accounts or solo influencers.

## How to search efficiently
Page fetching is blocked. You only have WebSearch, so the result text is your evidence.
- **Discovery:** niche + city/region searches in the local language. Examples: "Hautpflege Marke Gründerin München", "agence social media Lyon équipe", "makelaar Amsterdam team e-mail", "boutique hotel Copenhagen marketing manager".
- **Individual emails:** use `allowed_domains: ["<company domain>"]` with queries like "email", "team", "contact", "kontakt", "über uns", "équipe", "chi siamo", "ons team", "om oss". Batch 3–6 candidate domains in one search (`allowed_domains` accepts a list).
- **Sectors where named emails are common** (prioritise these): estate agents/makelaars/immobilier/inmobiliarias/immobiliare (agent bios list personal emails); social media, creative and e-commerce agencies (team pages; pitch white-label AI UGC/production capacity only if they offer content/ads services); boutique hotels and restaurant groups (sales & marketing contacts); founder-led DTC brands that publish "write to me: name@"; med spas and clinics with named owners; fitness/yoga studio owners; car dealerships (named sales/marketing managers); event venues.
- **Hiring signals (High intent):** job ads for "UGC creator", "social media manager", "content creator", "video editor", "Reels", "TikTok" in the local language, with the date. Record the exact ad URL. A hiring ad does not prove they want a freelancer, so say "noticed you're hiring for…" and offer extra capacity.

## Lessons from the pilot (follow these)
- **The search budget is small**, about 30 searches per agent per round, so don't waste them on open discovery phrases. They return directories (funda, realadvisor, Treatwell, Semrush) and data vendors.
- **Approach that works:** (1) one discovery search in the local language for "<sector> <city> team director owner", with `blocked_domains` set to directories/LinkedIn; (2) one `allowed_domains` search across the 5–6 candidate domains it found, with a plain query like "director email team" / "Geschäftsführer E-Mail Team" / "directeur email équipe" / "ons team e-mail". That search often returns several named emails at once; (3) a follow-up search on one domain with the person's name + "email address" when the summary hid the address; (4) one `allowed_domains` search for a specific fact (new development, listing, opening, campaign, podcast, award).
- **Sector mix per round:** about 60% from sectors that publish named emails (estate agents, property developers, car dealerships, franchise networks with agent profile pages such as BARNES, John Taylor, Lucas Fox, Engel & Völkers shops) and about 40% from the priority sectors (e-commerce/DTC brands, beauty/med spa/skincare, boutique hotels, social/creative agencies, fitness). The priority-sector records may end up Generic; record them anyway, with the named founder or owner, as they go to Needs Review for the user.
- **Don't record a company until you have a specific fact for the email.** A bare team listing isn't an observation.

## Email writing rules
- Write in the **business's language**: English (UK/IE), Dutch (NL), Swedish, Danish, Norwegian, Finnish, French, Spanish, Italian, German (DE/AT, and CH German-speaking; use French for Swiss Romandie). Use the formal register (Sie/vous/usted/Lei/De, natural "du" in Nordics).
- Follow this order: greeting by name → **specific verified fact** → one opportunity framed as an idea → one practical service (only 1–2 relevant ones) → **one** low-pressure question. **70–120 words** for the body including the greeting. Write the body up to and including the closing question. **Do not write the sign-off, name, or opt-out line**, because the builder adds them.
- No em dashes or en dashes (— –). No hype, no "I came across your website / I hope you're well / I wanted to reach out / cutting-edge / revolutionize", or their equivalents in the local language. No pricing, metrics, guarantees, fake testimonials or claims about their ad performance.
- Subject: short, specific to the business, unique, not misleading.

## Output: append one JSON object per line to your assigned file `eu-ai-content-leads/work/<your file>.jsonl`
Keys (all strings unless noted):
```
prospect_name, first_name, job_title, company, email, email_type ("Individual"|"Generic"),
email_verification_source_url, email_evidence (short quote showing the email with the name/role),
company_website, country (English name), state (region/county/Land), city,
industry_niche, business_product_or_service, social_media_platforms (comma list, only ones seen in a source),
social_profile_urls (only URLs seen), verified_social_media_observation, observation_date (YYYY-MM-DD the fact was posted/seen; use 2026-10-28 if only "seen today"),
problem_or_opportunity, proposed_automation_solution, recommended_services, buying_intent ("High"|"Medium"),
business_fit_reason, personalization_detail, language ("en","nl","sv","da","no","fi","fr","es","it","de"),
email_subject, email_body, research_source_urls (space-separated), evidence, research_confidence ("High"|"Medium"|"Low"),
notes, review_reason (empty, or why this needs human review)
```
Also record good companies where you only found a Generic email. They go to Needs Review and still count as research. Skip anything that fails rule 7.

Run `python3 -c "import json;[json.loads(l) for l in open('<file>')]"` on your file before finishing to make sure every line parses. Then commit and push only your own file to branch `claude/laughing-newton-h4hz9g`. Before pushing, run `git pull --rebase origin claude/laughing-newton-h4hz9g`, and retry on conflict. Finish by reporting a count of Individual-email records and Generic-email records.
