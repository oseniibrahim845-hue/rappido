# Author Ledger — ENGLISH-SPEAKING MARKETS email-lead campaign (research only, no outreach)
Client: Oseni Ibrahim, The Author Ledger (author spotlight & book promotion platform). Goal: 500 NEW unique qualified authors in the USA, Canada, Australia, New Zealand and South Africa, each with a publicly attributable professional email. Do NOT send emails or contact anyone.

## Environment limits (important)
- Web pages CANNOT be opened (WebFetch/curl are blocked). Use **WebSearch only**. Facts and emails must literally appear in search-result text.
- Obey the personal search budget in your task (count your searches). Use `allowed_domains` to restrict a search to one site (or a batch of 5–7 author-website domains) — this makes snippets show contact details far more often.
- Never fill any field (publisher, bio, award, country, date) from your own memory — only from search results.

## Who to find
Authors who live in / are nationals of your assigned country, with a book published in 2025 or 2026, or a confirmed 2027 book. Prefer emerging & mid-list authors in commercial genres (romance, romantasy, thriller/crime, cozy mystery, fantasy/sci-fi, horror, children's/YA, memoir, fiction, nonfiction, business, self-help). Skip megastars, celebrities and major-prize winners.

## Emails (priority) — NEVER guess or construct
1. Direct: author's own published professional/contact email (author website contact/about/media-kit page, newsletter page). Gmail etc. is fine ONLY when the author publishes it on their own site for enquiries.
2. Agent: the literary agent's own email shown on the agency site, for an author the agency site lists as that agent's client.
3. Publisher: a publisher's publicity/press email (publicity@, press@, media@, a named publicist) shown on the publisher site — may be reused for many authors, ALWAYS typed "Publisher", never presented as the author's own.
NOT acceptable: info@, orders@, sales@, submissions@, hello@/contact@ at a company, office@, admin@, emails from old/third-party pages, private personal info. Obfuscated forms on the author's own page ("name at domain dot com") may be written in standard form — note that in workflow2_notes.

## READY requires ALL of
- verified email + email_source_url where it appears;
- a 2025/2026 (or confirmed 2027) original book with book_source_url;
- country/residence/nationality STATED in a search result (not inferred);
- not a megastar/celebrity/major-prize winner; not a reissue/new edition;
- one sourced personalization detail.
Otherwise NEEDS_REVIEW with review_reason saying what is missing.

## Productive tactics
- Publisher publicity pages (allowed_domains = publisher domain, "publicity contact email" / "media enquiries"), then mine that publisher's 2025–2027 lists for local authors.
- Agency staff pages (allowed_domains = agency domain) list agent emails; agent client lists confirm representation.
- Indie/commercial authors: batch 5–7 author-site domains in allowed_domains with "author email address for enquiries" / "contact email".
- Discovery: 2025–2026 debut lists, festival programmes, award longlists, publisher "new releases", NetGalley/Goodreads lists.

## Dedup
Before writing, grep -i the surname in /home/user/rappido/author-ledger/anglo/work/EXISTING_NAMES.txt (previous Author Ledger master + Europe workbook) and all /home/user/rappido/author-ledger/anglo/work/*.jsonl. Skip known authors.

## Output — append ONE JSON object per line to your output file (valid JSON)
{"author_full_name":"","country":"","book_title":"","genre":"","publication_date":"YYYY or YYYY-MM","author_email":"","email_type":"Direct|Agent|Publisher","email_source_url":"","author_website":"","publisher":"","book_source_url":"","recent_activity":"","personalization_detail":"","commercial_fit":"High|Medium|Low + 1 short reason","outreach_language":"English","duplicate_status":"New","qualification_status":"READY|NEEDS_REVIEW","review_reason":"","workflow2_notes":"one line: what Workflow 2 should double-check"}
- country: plain country name only ("United States", "Canada", "Australia", "New Zealand", "South Africa"); put evidence (e.g. "lives in Denver per own site") in workflow2_notes.
Use your own scratchpad subfolder for helper scripts: /tmp/claude-0/-home-user-rappido/85eb8748-a21e-58e5-b6eb-a7dcb5a964d2/scratchpad/an_<tag>/

## Finish with a short report
Authors researched; new READY; Direct emails; Agent/Publisher emails; NEEDS_REVIEW; duplicates rejected; NEW verified press/agent contacts (address + source URL) for the next round.
