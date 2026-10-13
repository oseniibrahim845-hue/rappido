# Author Ledger — EUROPE email-lead campaign (research only, no outreach)
Client: Oseni Ibrahim, The Author Ledger (author spotlight & book promotion platform). Goal: 500 unique qualified European authors with a publicly attributable professional email.

## Environment limits (important)
- Web pages CANNOT be opened (WebFetch/curl are blocked). Use **WebSearch only**. Facts and emails must literally appear in search-result text.
- Search budget is shared: obey the personal budget in your task (count your searches). Use `allowed_domains` to restrict a search to one site — this makes snippets show contact details far more often.

## Who to find
Authors in your assigned country (national, resident, or clear professional connection) with a book published in 2025 or 2026, or a confirmed 2026/2027 book. Prefer emerging & mid-list, commercially suitable genres (romance, thriller/crime, fantasy/sci-fi, children's/YA, memoir, fiction, nonfiction, business, self-help). Skip megastars.

## Emails (priority) — NEVER guess or construct
1. Direct: author's own professional/contact email (author website, media kit, newsletter page, official profile).
2. Agent: the literary agent's professional email shown on the agency page for that author/agent.
3. Publisher: a publisher's publicity/press email (e.g. press@, publicity@, presse@) shown on the publisher site — may be reused for several authors, ALWAYS typed "Publisher", never presented as the author's own.
Generic info@/orders@/submissions@ addresses are NOT acceptable. Private personal info is not acceptable. The address must appear in a search result whose URL you record as email_source_url.

## Productive tactics
- Agency sites: search with allowed_domains = the agency domain for "<author> agent email" or "rights contact" — agency staff pages list agent emails; the agent's client list confirms representation.
- Publisher press pages: allowed_domains = publisher domain, query "press contact publicity email" — then pair with that publisher's 2025/2026 authors.
- Author sites: "<author name> author contact email" for indie/commercial authors who publish contact emails.
- Festival/prize lists (2025/2026) for discovery.

## Dedup
Before writing, check /home/user/rappido/author-ledger/europe/work/EXISTING_MASTER_NAMES.txt and all /home/user/rappido/author-ledger/europe/work/*.jsonl author names. If an author is already there, write the row with status "DUPLICATE" (fill what you have) instead of a new lead — or skip if you have nothing new.

## Output — append ONE JSON object per line to your output file (valid JSON, escape newlines)
{"author_full_name":"","country":"","book_title":"","genre":"","publication_date":"YYYY or YYYY-MM","author_email":"","email_type":"Direct|Agent|Publisher","email_source_url":"","author_website":"","publisher":"","book_source_url":"","recent_activity":"","personalization_detail":"","commercial_fit":"High|Medium|Low + 1 short reason","outreach_language":"","duplicate_status":"New|DUPLICATE (of …)","qualification_status":"READY|NEEDS_REVIEW|DUPLICATE","review_reason":"(if NEEDS_REVIEW: what is missing)","workflow2_notes":"one line for the Author Spotlight Workflow 2 audit: what to double-check"}
- READY only if: verified email with source URL + 2025/2026(/2027 confirmed) book with source + identity/country clear + personalization detail sourced.
- NEEDS_REVIEW: good author but missing/uncertain email, date or source — say what's missing.
- outreach_language: the author's working language from evidence (e.g. German for a German-language novelist); English if they publish in English or unclear.
- personalization_detail: one specific sourced fact (premise, setting, award, interview point) useful for a future intro. No invented quotes.
Use your own scratchpad subfolder for helper scripts: /tmp/claude-0/-home-user-rappido/85eb8748-a21e-58e5-b6eb-a7dcb5a964d2/scratchpad/eu_<country-code>/

## Finish with a short report
Authors researched; new READY; Direct emails; Agent/Publisher emails; NEEDS_REVIEW; duplicates rejected.
