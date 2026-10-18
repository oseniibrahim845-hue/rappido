# Author Ledger — ENGLISH-SPEAKING MARKETS email-lead campaign (research only, no outreach)
Client: Oseni Ibrahim, The Author Ledger (author spotlight & book promotion platform). Goal: 500 NEW unique qualified authors in the USA, Canada, Australia and New Zealand (client EXCLUDED Africa — do not research South African authors), each with a publicly attributable professional email. Do NOT send emails or contact anyone.

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
- country: plain country name only ("United States", "Canada", "Australia", "New Zealand"); put evidence (e.g. "lives in Denver per own site") in workflow2_notes.
Use your own scratchpad subfolder for helper scripts: /tmp/claude-0/-home-user-rappido/85eb8748-a21e-58e5-b6eb-a7dcb5a964d2/scratchpad/an_<tag>/

## Finish with a short report
Authors researched; new READY; Direct emails; Agent/Publisher emails; NEEDS_REVIEW; duplicates rejected; NEW verified press/agent contacts (address + source URL) for the next round.

## Round 2 — KNOWN VERIFIED CONTACTS (reuse: pair with more of their 2025–2027 local authors)
- Berrett-Koehler (US): ckirk@bkpub.com (Christy Kirk, media contact; ideas.bkconnection.com/berrett-koehler-publishers-announces-new-leadership-structure)
- BenBella / Matt Holt (US): jennifer@benbellabooks.com (media enquiries; benbellabooks.com/contact/)
- Andrea Brown Literary Agency (US, kids/YA; Agent type only for listed clients): saritza@, caryn@ (reps-wiseman.html), jennifer@ (reps-rofe.html), jamie@, kelly@ (Team/kelly-sonnack), jmatt@ (reps-mattson.html) andreabrownlit.com
- BookEnds (US): jmcgowan@bookendsliterary.com (bookendsliterary.com/james-mcgowan; clients Tasneem Amiruddin, Marusha Belle, Nicole Wong, Jenny Liao, Kris Coronado, Pamela Courtney)
- Canada: publicity@ecwpress.com (ecwpress.com/pages/media-press); publicity@dundurn.com (dundurn.com/contact); publicity@houseofanansi.com (houseofanansi.com/pages/contact-us); cynara@arsenalpulp.com (arsenalpulp.com/Media-Review-Copies); promotion@invisiblepublishing.com (confirm source page)
- US crime: publicity@crookedlanebooks.com (crookedlanebooks.com/contact/)
- Residence stated as a city/state/province (e.g. "lives in Winnipeg", "Northern Virginia") counts as country stated.
- Australia: PublicityWBA@walkerbooks.com.au (walkerbooks.com.au/faqs/ and every Walker AI sheet); melissa.luckman@walkerbooks.com.au (walkerbooks.com.au/resources/media/)
- Australia DIRECT-email goldmine: Walker Books Australia author database https://www.walkerbooks.com.au/wp-content/uploads/resource/Author-database-2026.pdf lists each author's email + state — query it name by name (allowed_domains walkerbooks.com.au, "<author name> email"). Unmined: Sarah Anthony, Robyn Bavati, Jodi Toering, Judy Watson, Anita Thomas, Dianne Wolfer, Sue-Ellen Pashley, Pamela Rushby, Skye Melki-Wegner.
- Canada kids/nonfiction: publicity@kidscan.com (kidscanpress.com/contact-us/); publicity@greystonebooks.com (greystonebooks.com/pages/contact-us)
- US kids: dspurlock@charlesbridge.com (charlesbridge.com/pages/press-room); publicity@peachtreebooks.com (peachtreebooks.com/contact-us/); publicity@leeandlow.com (leeandlow.com/contact/). Tip: product pages on peachtreebooks.com / charlesbridge.com show date + "lives in" in snippets; search "author bio" rather than "where does X live".
- US SFF: kasey@tachyonpublications.com (tachyonpublications.com/company-information/); katelyn@jillgrinbergliterary.com (agent, per jenniferthorne.com/contact — use only for her listed clients)
- Australia: publicity@textpublishing.com.au (textpublishing.com.au/contact); publicity@hachette.com.au (hachette.com.au/contact); publicity@echopublishing.com.au (echo has paused acquisitions — check inbox); discovery: rocket.hachette.com.au "Emerging Literary Voices of 2026"
- New Zealand: publicity@penguinrandomhouse.co.nz (penguin.co.nz/contact; list: penguin.co.nz/books/lists/665-latest-new-zealand); sarah.thornton@prcomms.com (Massey UP media, masseypress.ac.nz/pages/contact); pressmarketing@auckland.ac.nz (aucklanduniversitypress.co.nz/contact-us/)
- South Africa: jeanmarie.korff@jonathanball.co.za (JBP publicity manager) and johan.hugo@nb.co.za (NB Publishers & JBP Local: Kwela, Tafelberg, Human & Rousseau) — both jonathanball.co.za/contact-us/; discovery: JBP Local Catalogue 2026 PDF (jonathanball.co.za/wp-content/uploads/2025/12/JBP-Local-Catalogue-2026_update.pdf)
- US fiction: media@redhen.org (redhen.org/contact/); publicity@counterpointpress.com (counterpointpress.com/faqs/); morgan_larocca@milkweed.org (milkweed.org/faqs-contact-requests)
- US romance: siena.koncsol@sourcebooks.com (Bloom & Casablanca publicity, sourcebooks.com/media.html). Tip: mid-list romance authors' contact/media-kit pages name their PRH/Putnam/Berkley publicist (e.g. yhassan@, kcipolla@penguinrandomhouse.com, Kmckee@prh.com) — record the author's page as email_source_url; type Publisher. Batch 5–7 author domains with "contact email media kit".
- Canada: promotion@invisiblepublishing.com now confirmed at invisiblepublishing.com/contact/. Tip: on ecwpress.com search '"Published: <Month> 2026" "lives in"' to get date + residence together (untried months: Jan, Jun, Jul, Nov, Dec 2026 and most of 2025).
- Tips: crookedlanebooks.com/<author-slug>/ pages carry a residence line; leeandlow.com/contributor/<name>/ pages carry residence; Lee & Low Spring 2027 debuts page.
- US romance publicists (seen on author contact pages): sophia.lauriello@stmartins.com; kayla.janas@stmartins.com (Minotaur); bblack@penguinrandomhouse.com; yhassan@penguinrandomhouse.com; kcipolla@penguinrandomhouse.com; kdwyer@leoprny.com (LEO PR). BEST TACTIC: search the publicist address IN QUOTES with no domain limit — results list every author contact page that names it (e.g. "kcipolla@penguinrandomhouse.com" → kateharris.ca, kryslee.com, lauriegwenshapiro.com, claire-cameron.com). email_source_url = that author's contact page; type Publisher.
- Australia: jean.smith@uqp.com.au (UQP marketing & publicity; uqp.com.au/blog/2026-uqp-mentorship-prize-for-under-represented-writers)
- US crime publicists: kayla.janas@stmartins.com (also on gigipandian.com, vivienchien.com); alexis.saarela@tor.com (Forge; rachelhowzell.com/contact-us); megan@meganbeatie.com (MB Communications; kairarouda.com/contact/); katelynn@kaypublicity.com (Kay Publicity; edithmaxwell.com/contact/) — search each IN QUOTES to find more author pages. Discovery: escapewithdollycas.com tag crooked-lane-books (bios with residence; unmined: Mollie Ann Cox, Victoria Houston, Kit Gray).
- CORRECTION: searching a publicist email IN QUOTES does NOT work (search engine doesn't index email strings). Instead: allowed_domains = 5–7 author domains + "publicity contact"; or "<publicist name>" "publicity" author contact. New: sarah.melnyk@stmartins.com (St. Martin's/Minotaur publicity; jenniferhillierbooks.com/contact/).
- US crime agents (author contact pages): fblack@literarycounsel.com (victoriagilbertmysteries.com/contact); srostan@lgrliterary.com (hannahmorrissey.com/contact); marisa@ / ciara@corvisieroagency.com (elise-scott.com/contact-me). Crooked Lane author pages w/ residence but no date yet: Kira Peikoff, Bailee Abbott, Heather Blake.

## Round 4 — BIG-PUBLISHER IMPRINT PUBLICITY INBOXES (all from hachettebookgroup.com/press-publicity/ unless noted; type Publisher)
- Grand Central / Balance / Legacy Lit / Twelve: grandcentralpublishing@hbgusa.com
- Forever (romance): readforever@hbgusa.com (Forever Winter/Summer 2026 preview pages list authors; unmined: Gabriella Gamez, Lucy Smoke, Karelia Stetz-Waters, Summer N. England)
- Little, Brown / Back Bay / Mulholland / Voracious: publicity@littlebrown.com
- Orbit / Redhook (SFF): orbit.generic@hbgusa.com
- Hachette Books / Da Capo / Hachette Go: hachette.books@hbgusa.com
- Basic Books: basic.publicity@hbgusa.com
- Little, Brown Books for Young Readers: publicity@lbchildrens.com
- HarperCollins Australia: publicity@harpercollins.com.au (harpercollins.com.au/pages/media-publicity)
- HarperCollins publicists on author pages: Heather.Drucker@harpercollins.com (Harper Perennial); sonya.cheuse@harpercollins.com (Ecco); laura.gianino@harpercollins.com (MIRA)
Pair these with the imprint's 2025–2027 debut/mid-list authors whose hachettebookgroup.com contributor page states residence (search allowed_domains=hachettebookgroup.com "<imprint> 2026 debut lives in").
- US SFF: martin@erewhonbooks.com confirmed current (erewhonbooks.com/erewhon-kensington-press-release; Erewhon now a Kensington imprint); jocelyn.bright@tor.com (Tor publicist, imakeupworlds.com/press-kit/ — may be old). Tip: don't combine 'lives in' with email in one query; use Book Riot monthly SFF lists for discovery.
- NZ: publicity@hachette.co.nz (Hachette Aotearoa / Moa Press; hachette.co.uk/landing-page/hachette/press-contacts/). Moa Press to mine: Shana Chandra (Banjara, Apr 2026), Olivia Spooner, Zoe Rankin, Ellis Blake (Ben Sanders).
- Forever Fall 2026 preview (unmined): https://www.hachettebookgroup.com/listicle/forevers-fall-2026-preview/ — hachettebookgroup.com contributor pages reliably state residence; best yield source so far (15 READY from 15 searches).
- US crime: marketing@oceanviewpub.com is Oceanview's named publicity-department address (oceanviewpub.com/contact) — usable; oceanviewpub.com author profiles state residence. Crooked Lane seam nearly exhausted.
- More publicist inboxes (from author contact pages): Atriapublicity@simonandschuster.com (alisoncochrun.com/contact); cpascoe@penguinrandomhouse.com (Berkley; libbyhubscher.com/get-in-touch); lackerman@kensingtonbooks.com (Kensington comms; cherylhollon.com/contact/ — confirm current); Sarah.Melnyk@stmartins.com (also ellecosimano.com/contact/). Tip: after a batch "publicity contact" search finds the pages, a 2nd query naming the publicist on just those 2–3 domains reveals the address.
- Orbit leads: acquisition/cover-launch posts on hachettebookgroup.com carry residence; unmined Ash Huang, Hazel Mack/Anna Fury, Juliet Brooks, Alla Zaykova, AM Kvita, Bitter Karella, Eman Quotah, Beatrice Winifred Iker.
- NZ: angela.radford@hachette.co.nz (Hachette Aotearoa publicist; oliviaspooner.com/contact-8); cora.roberts@textpublishing.com.au (Text publicist; rosecarlyle.com/contact-us). NZ discovery: ketebooks.co.nz "Sizzling hot fiction arriving in 2026" (KJ Holdom, Nic Sceats, Adam Perry, Megan Nicol Reed, Lauren Keenan) and Kete "New Voices of Aotearoa 2026".
- HBG: GCP Fall 2026 catalog hachettebookgroup.com/articles/grand-central-publishing-fall-2026-catalog/; query format "<name> author lives; <name2> author lives" checks 2–3 per search. Dundurn: quoted "Published <Month> 2026" returns date + residence. Invisible forthcoming: invisiblepublishing.com/product-category/forthcoming/. AU leads: Walker Author-Database-4.pdf (QLD creators), Mark Brandi, Jenny Knightsby, Claire Thomas, Toni Jordan, Vanessa Turnbull-Roberts.
- AU HarperCollins tip: on harpercollins.com.au batch 3–4 titles as '<title> author biography' (avoid 'lives in' — misread). Unmined: Mandy Magro, Kirstyn McDermott, Shannon Kelly-White, Tricia Stringer, 'Biggest books of 2026 sneak peek' blog post.
- AU Walker: search tool no longer reveals emails from the author-database PDFs; use PublicityWBA@walkerbooks.com.au. Walker 2026 AI sheets with bios+residence: walkerbooks.com.au/wp-content/uploads/page/{May-2026-AIs,June-2026-AIs,July-AIs-3,August-2026-AIs-4,2026-September-AIs,October-2026-AIs,November-2026-AIs}.pdf. Names to check for 2025–26 books: Megan Daley, Michelle Macwhirter, Caroline Magerl, Kylie Howarth, Cindy Lane, Sally Murphy, Janeen Brian, Raewyn Caisley, Katrina Germein, Mark Greenwood, Meg McKinlay, James Foley, Sally Barton.
- Kensington: LAckerman@kensingtonbooks.com confirmed at kensingtonbooks.com/libraries/home/who/ (cozy/historical mystery/suspense/crime). 2026 Kensington Cozies booklet (kensingtonbooks.com/wp-content/uploads/2026/04/KensingtonCozies_Booklet_2026_web.pdf) unmined: Karen Rose Smith, Allie Pleiter, Ann Claire, Lee Hollis, Isis Crawford, Christin Brecher, Mary McHugh (skip megastars Victoria Laurie/Krista Davis/Leslie Meier/Ellery Adams/Cleo Coyle). kensingtonbooks.com/authors/ pages state residence.
- GCP: Summer 2026 catalog ("Big Baby" author), Winter 2026 catalog, Legacy Lit imprint page, HBG "Most Anticipated Winter 2027" article — unmined.
