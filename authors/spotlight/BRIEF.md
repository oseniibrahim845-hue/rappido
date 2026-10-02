# Author Spotlight research + outreach (user prompt 2026-10-02)

Goal: for each assigned author, verify facts, check service gaps, and write ONE Author Spotlight invitation email.
Tools: WebSearch works. WebFetch/curl to most sites is blocked; verify from search results. Budget about 8 searches per author.
Prior research for each author is in /home/user/rappido/authors/Author_Ledger_Chile_Qualified_Leads.csv and
/home/user/rappido/authors/Author_Ledger_International_Qualified_Leads.csv (use it, but re-verify the key facts).

## Research per author
- Real person, exact book title, public email (never guessed; keep the email already on file unless you find it is wrong).
- has_audiobook (Yes/No/Unclear): search Amazon, Audible, Spotify, Apple Books, author site, publisher. "No" only after several
  reliable sources checked. Record platforms + links in audiobook_check_sources.
- has_author_website (Yes/No/Poor/Unclear) + website_url + website_quality (short).
- has_book_trailer (Yes/No/Unclear) + book_trailer_url (search YouTube/Instagram/publisher).
- has_amazon_a_plus (Yes/No/Unclear). Amazon pages usually cannot be opened here, so Unclear unless a source shows it.
- best_offer: ONE of Audiobook Production / Author Website and Press Kit / Book Trailer and Promotional Reels /
  Book Relaunch Package / Amazon A+ Graphics, tied to the clearest VERIFIED gap. offer_reason explains the evidence.
  Never pick a service for a gap you could not verify (e.g. do not pick Audiobook if has_audiobook is Unclear).

## Email (Author Spotlight is the main reason)
- Language: English for English-language authors. For Spanish-language authors write natural Spanish (Chile: tú; Argentina: vos)
  with the same structure and rules, since they are being contacted in Spanish.
- 170-230 words. No em dashes or en dashes. Never mention AI, synthetic/automated narration, voice cloning, text-to-speech,
  generative tools or internal tools. Do not claim narration is human. No guarantees of sales/royalties/coverage/rankings/ROI.
  No criticism. No "Congratulations" in subject. Do not claim to have read the book.
- Structure:
  Hi [first_name],
  [Personal opening from a verified detail; different for every author.]
  I would love to invite you to be featured in an Author Spotlight on The Author Ledger. The feature is designed to introduce
  readers to your work, the story behind your book, and the experiences or ideas that have shaped your journey as an author.
  Alongside our editorial features, we also support authors with professionally produced audiobook editions, cinematic book
  trailers, short promotional reels, author websites, press kits, Amazon A+ graphics, and book relaunch materials.
  [2-3 sentences on best_offer, explaining the verified gap gently, and that it is optional and separate from the Spotlight.]
  Would you be interested in hearing more about the feature and the option I believe would suit [book_title] best?
  Warm regards,
  Oseni Ibrahim
  The Author Ledger
  (Sender is ALWAYS Oseni Ibrahim, never any other name.)
  For agency/publisher addresses (info@indentagency.com, editorial@nasspapier.com) greet the team and refer to the author
  in the third person.
- subject_line: e.g. "An Author Spotlight for [book_title]", "Featuring the story behind [book_title]",
  "[book_title] and your author journey", "A feature invitation for [first_name]".

## Output
JSON list at your output path, one object per author with EXACTLY these keys in this order:
author_name, email, first_name, book_title, book_topic, personalization_detail, personalization_reason, personalized_opening,
subject_line, email_body, research_sources, research_confidence, personalization_status, send_status, date_sent, country,
has_audiobook, audiobook_check_sources, has_author_website, website_url, website_quality, has_book_trailer, book_trailer_url,
has_amazon_a_plus, best_offer, offer_reason
- research_sources: all links separated by "; ". research_confidence: High/Medium/Low.
- personalization_status: Ready / Needs Review / Excluded (Ready only if author, book, email and personal details verified).
- send_status and date_sent: empty strings.
- Check word count (170-230) and no dashes before writing. Do not send email. Do not commit to git.
Report: per author status, best_offer, and anything uncertain.
