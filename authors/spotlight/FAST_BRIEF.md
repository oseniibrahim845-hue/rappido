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

I would love to invite you to be featured in an Author Spotlight on The Author Ledger. The feature is designed to introduce readers to your work, the story behind your book, and the experiences or ideas that have shaped your journey as an author.

Alongside our editorial features, we also support authors with professionally produced audiobook editions, cinematic book trailers, short promotional reels, author websites, press kits, Amazon A+ graphics, and book relaunch materials.

If a short trailer or a few promotional reels for <book_title> is something you have been considering, we can handle the full production. It is entirely optional and separate from the Spotlight.

The Author Spotlight is a paid feature, and I would be happy to share the details and pricing if it sounds like a good fit.

Would you be interested in hearing more about the feature and the option I believe would suit <book_title> best?

Warm regards,
Oseni Ibrahim
The Author Ledger

(Spanish-language authors: write the same structure in natural Spanish, tú (vos for Argentina), including
"El Author Spotlight es una publicación paga, y con gusto te comparto los detalles y el precio si te interesa.")
Never mention AI or guarantees. No em dashes or en dashes anywhere. The finished body must be 180-260 words.

Process: launch 4 parallel general-purpose subagents (model sonnet), one per group, each writing
authors/spotlight/bank_<YYYYMMDDHHMM>_fast_<group>.json and aiming for 6-8 Ready rows within ~45 searches.
Do NOT send email. Only add your own bank files; commit and push them to claude/kind-fermat-wa8eun
(on a rejected push: git pull --rebase origin claude/kind-fermat-wa8eun then push; retry on network errors).
