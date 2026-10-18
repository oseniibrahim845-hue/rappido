# Multi-country author scouting (Workflow 1, adapted from the Chile prompt) - search-only

Read /home/user/rappido/authors/prompts/WORKFLOW1_lead_generation_chile.txt and apply ALL its rules, replacing "Chile"
with YOUR assigned country/countries (region_or_county = state/province/county; country = the country).
Environment: WebSearch tool only. WebFetch/curl to most sites is BLOCKED, so verify from search results/snippets/summaries
using several targeted searches per author.

Hard rules:
- Email must be PUBLICLY DISPLAYED in a search result/summary you actually saw (author site contact page, newsletter/Linktree
  bio, Instagram/Facebook/X bio, publisher/agent page, festival page, interview). Never guess or construct an email.
  Obscured "[email protected]" = not usable.
- Author must be CURRENT: book in the last ~18 months, forthcoming 2026-27, or late-2025 still promoted, or verified reactivation.
- Genuine connection to the assigned country. One row per author.
- Indie/self-published and small-press authors in genre fiction (romance, fantasy, thriller, horror, cozy mystery, YA, sci-fi)
  often publish a Gmail/business email in social bios and are good prospects for book trailers; include them.
  Traditionally published authors are fine too (agent/publicist email = VERIFIED PROFESSIONAL).
- Skip deceased, minors, sanctioned countries (Iran, Russia, Belarus, North Korea, Syria, Cuba).
- Read /home/user/rappido/authors/intl/SEEN_EMAILS.txt first and skip any author whose email is in it; append every email you
  add (one per line) so parallel researchers don't duplicate.
- Do not send any email.

Output: JSON list at your output path, each item with EXACTLY the 42 Workflow 1 canonical keys (author_name ... audit_notes),
exact allowed values, outreach_language verified (English, Spanish, etc.). Include READY and NEEDS REVIEW only.
Target 15-25 rows with as many READY as possible. Budget ~45 web searches, then stop and report READY / NEEDS REVIEW counts
and notable uncertainties.
