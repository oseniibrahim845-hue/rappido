# FAST author scouting (Author Spotlight) - more leads per run

Goal: 20-30 Ready author rows per session. Spend ~3-4 WebSearch calls per author, not more.
Per author verify ONLY: (1) real author, (2) exact title of a book published in the last ~18 months or announced for 2026-27,
(3) a PUBLICLY DISPLAYED email seen in a search result (website contact page, Linktree/Instagram/Facebook bio, author
newsletter page, publisher/agent page). Never guess or construct emails; obscured "[at]" forms are not usable.
(4) ONE concrete verified detail for the opening (book premise, setting, series, award, launch event, author background).
Skip: Nigerian authors, sanctioned countries (Iran, Russia, Belarus, North Korea, Syria, Cuba), minors, deceased, big-agency-only
contacts, generic org addresses, anyone in authors/intl/SEEN_EMAILS.txt, authors/queue.json or any authors/spotlight/bank_*.json.
Best sources: indie/self-published romance, fantasy, thriller, cozy mystery, YA, sci-fi, Christian, children's, self-help authors.

Write each author as a row with exactly these 26 keys (same as BRIEF.md):
author_name, email, first_name, book_title, book_topic, personalization_detail, personalization_reason, personalized_opening,
subject_line, email_body, research_sources, research_confidence, personalization_status, send_status, date_sent, country,
has_audiobook, audiobook_check_sources, has_author_website, website_url, website_quality, has_book_trailer, book_trailer_url,
has_amazon_a_plus, best_offer, offer_reason
Use "Unclear" for has_audiobook / has_book_trailer / has_amazon_a_plus unless you happened to see the answer;
best_offer = "Book Trailer and Promotional Reels"; offer_reason = "Fast mode: offered as an option, gap not verified".
personalization_status = "Ready" only when items 1-4 are verified; else "Needs Review". send_status and date_sent = "".
subject_line = "An Author Spotlight for <book_title>"

email_body (English authors) - fill <...> exactly, keep every other sentence as written:

Hi <first_name>,

<personalized_opening: 2-3 natural sentences built on the verified detail about the author or <book_title>. No em dashes. Do not claim to have read the book.>

I would love to feature you in an Author Spotlight on The Author Ledger. It is a short feature that tells readers about your book, the story behind it, and your journey as an author.

We also help authors with audiobooks, book trailers, short promo videos, author websites, and Amazon graphics.

Would you like to hear more about the Spotlight?

Warm regards,
Oseni Ibrahim
The Author Ledger

(Spanish-language authors: write the same structure in natural Spanish, tú (vos for Argentina), using the same short structure)
Never mention AI or guarantees. Use simple sixth grade English. No hyphens inside words, no brackets or parentheses, no em dashes or en dashes anywhere. Do not mention that the Spotlight is paid and do not say it is free (user decision 2026-10-08). The finished body must be 80-180 words.

Process: launch 4 parallel general-purpose subagents (model sonnet), one per group, each writing
authors/spotlight/bank_<YYYYMMDDHHMM>_fast_<group>.json and aiming for 6-8 Ready rows within ~45 searches.
Do NOT send email. Only add your own bank files; commit and push them to claude/kind-fermat-wa8eun
(on a rejected push: git pull --rebase origin claude/kind-fermat-wa8eun then push; retry on network errors).
