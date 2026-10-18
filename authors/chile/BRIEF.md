# Chile author scouting (Workflow 1) - search-only research brief

Read and follow /home/user/rappido/authors/prompts/WORKFLOW1_lead_generation_chile.txt (the full rules).
Environment limits: you can use the WebSearch tool only. WebFetch/curl to most sites is BLOCKED by the network,
so verify facts from search result titles/snippets/summaries (run several targeted searches per author).

Hard rules (never break):
- Email must be PUBLICLY DISPLAYED in a search result/snippet you actually saw (author site contact page, publisher page,
  festival page, interview, social bio). Never guess or construct an email. If you cannot see it, the lead is not READY.
- Author must be CURRENT (2026 book, forthcoming 2026-27, late-2025 still promoted, or verified reactivation).
- Genuine Chile connection. Not just Spanish-language.
- One row per author; no famous inactive authors.
- Skip anyone whose email is in /home/user/rappido/authors/chile/SEEN_EMAILS.txt (append every email you add there, one per line, so parallel researchers don't duplicate).
- Do not send any email.

Output: write a JSON list to your given output path. Each item has EXACTLY these keys (Workflow 1 canonical columns):
author_name, first_name, email, email_status, email_source, normalized_author_name, normalized_email, duplicate_status,
duplicate_match_reference, country, city, region_or_county, location_relationship, location_evidence, author_type,
publishing_route, official_website, book_title, book_type, publication_date, latest_release_date, publisher, isbn_or_asin,
series, book_topic, book_distinctive_features, current_author_moment, current_marketing_signal, marketing_evidence,
commercial_fit, current_author_need, best_reusable_deliverables, spotlight_angle, curiosity_question, personalization_detail,
personalization_reason, outreach_language, discovery_source, research_sources, research_confidence, personalization_status, audit_notes
Use the exact allowed values from the prompt. email_source = the URL/page where the email was shown.
Include READY and NEEDS REVIEW rows (NEEDS REVIEW for authors that are strong but whose email you could not see displayed - leave email blank).
Do not include EXCLUDED rows. Aim for quality: target ~12-20 rows, at least half READY.
Budget: about 40 web searches. Then stop and report: READY count, NEEDS REVIEW count, notable uncertainties.
