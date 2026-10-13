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

## Round 2 — KNOWN VERIFIED CONTACTS (reuse them: pair with more of that publisher's/agency's 2025–2027 authors)
Publisher press (type "Publisher"; record the source URL given):
- UK: publicity@walker.co.uk (walker.co.uk/about-us/contact-us/); publicity@littletiger.co.uk (littletiger.co.uk/contact-us); press@profilebooks.com (profilebooks.com/about-profile-books/contact-us/); publicity@usborne.co.uk (usborne.com press page); publicity.enquiries@orionbooks.co.uk for Gollancz (store.gollancz.co.uk/pages/faqs)
- Ireland: publicity@lilliputpress.ie (lilliputpress.ie/pages/contact); publicity@obrien.ie (obrien.ie/contact); fmurphy@gill.ie (Gill Books FAQ); des.doyle@newisland.ie (New Island announcements)
- Germany: presse@droemer-knaur.de (droemer-knaur.de/verlag/presse); press@piper.de (piper.de/presse/pressekontakte); presse@dtv.de (dtv.de/service/presse); presse@carlsen.de (carlsen.de/presse/kontakt)
- Austria/CH: presse@kremayr-scheriau.at; presse@picus.at; blum@literaturbuero.at (Residenz literature PR); jana.steinhoff@schoeffling.de / kaps@jungundjung.at (Kampa)
- France: presse@bragelonne.fr (bragelonne.fr/contact/); presse@editions-observatoire.com (editions-observatoire.com/la-maison)
- Italy: ufficiostampa@giunti.it; ufficiostampa.rizzoli@rizzolilibri.it; skstampa@sperling.it; ufficio.stampa@feltrinelli.it
- Spain/PT: pcordon@planeta.es (Cúpula press kit); comunicacao@leya.com (leya.com/pagina/comunicacao)
- NL/BE: publiciteit@querido.nl (querido.nl/contact/); Atlas Contact publicists mknake@/ycramer@/mmolijn@atlascontact.nl (atlascontact.nl/contact/publiciteit/); anna.buyse@standaarduitgeverij.be (Manteau/Davidsfonds/Tzara) and gloria.vanheyst@standaarduitgeverij.be (Bruna/Lev./Cargo/Signatuur) (standaarduitgeverij.be/pers/)
- Romania: pr@nemira.ro (nemira.ro/contacts); Hungary: krisztian@agavekonyvek.hu (agavekonyvek.hu/oldal/kapcsolat); Greece: pr@psichogios.gr (psichogios.gr)
Agents (type "Agent"; only for authors the agency's own page lists as clients of that agent):
- Darley Anderson (UK): camilla@darleyanderson.com, jade@darleyanderson.com (darleyanderson.com/team/...)
- Sandra Bruna (Spain): sbruna@sandrabruna.com, bbruna@sandrabruna.com (sandrabruna.com/en/agency/)
- Oslo Literary Agency: evy.tillman@osloliteraryagency.no, henrik@osloliteraryagency.no
- Ahlbäck (Finland): satu@ahlbackagency.com, noora@ahlbackagency.com
- Bonnier Rights (Sweden): johanna.lindborg@bonnierrights.se

## Round 3 — ADDITIONAL VERIFIED CONTACTS (from round 2)
- UK: press@bloodhoundbooks.com (bloodhoundbooks.com/submissions); publicity@headofzeus.com (headofzeus.com/about); grace.samuel@fireflypress.co.uk (fireflypress.co.uk/about/contact-details/; Wales, re-check age)
- Germany: presse@rowohlt.de (rowohlt.de/verlag/presse); presse@loewe-verlag.de (loewe-verlag.de/presse/kontakte-service/)
- France: crousseau@jclattes.fr (JC Lattès head of press); solene.deltell@gallimard-jeunesse.fr (gallimard-jeunesse.fr/professionnels/journalistes.html)
- Switzerland: presse@diogenes.ch (diogenes.ch/presse.html); presse@zytglogge.ch (zytglogge.ch/kontakt-c-48); presse@unionsverlag.ch
- Denmark: presse@gyldendal.dk (gyldendal.dk/gyldendal/salg-marketing-og-presse)
- Greece: pressoffice@metaixmio.gr / dora@metaixmio.gr (Metaixmio); Romania: claudia.fitcoschi@polirom.ro (polirom.ro/pag/16-promovare)
- Bulgaria: julia.petkova@colibri.bg (colibri.bg/bg/p/kontakti); Croatia: rights@fraktura.hr (fraktura.hr/copyrights/); Slovenia: pr@mkz.si (Mladinska knjiga, sikstinska.mladinska.com/za-medije/)
- Poland: agnieszka@czarne.com.pl (czarne.com.pl/dla-mediow); promocja@wydawnictwoliterackie.pl; promocja@marginesy.com.pl; Slovakia: carna.lucia@ikar.sk (ikar.sk/kontakty.html)
- Spain: prensaes@sextopiso.com (sextopiso.es contacto); epalacios@siruela.com (Siruela, older catalogue); Planeta press kits list per-title press contacts (e.g. easpas@planeta.es)
- Belgium: evi.vanoverveld@standaarduitgeverij.be (Standaard children's, standaarduitgeverij.be/pers-2/)

## Round 4 — ADDITIONAL VERIFIED CONTACTS (from round 3)
- Germany: meike.blatnik@ullstein.de (Ullstein literature/entertainment press, ullstein.de/service/presse); presse@thienemann-esslinger.de (review copies)
- Switzerland: presse@diogenes.ch; presse@zytglogge.ch; Unionsverlag press now via tanja.warter@beck.de (unionsverlag.com/info/text.asp?text_id=130)
- Netherlands: publiciteit@debezigebij.nl (debezigebij.nl/voor-de-pers/); promotie@lemniscaat.nl / hindele@lemniscaat.nl (children's/YA) (lemniscaat.nl/pers)
- Sweden: sara.dobareh@norstedts.se (norstedts.se/kundservice/medarbetare); ami.moren@nok.se (Natur & Kultur fiction, nok.se/press/Presskontakt/)
- Denmark: sam@lrforlag.dk (Lindhardt og Ringhof, lindhardtogringhof.dk/mod-forlaget); Norway: presse.litteratur@gyldendal.no (gyldendal.no/om-gyldendal/kontakt-oss/gyldendal-litteratur/)
- Ireland: peter@peteroconnellmedia.com (Merrion Press PR agency, irishacademicpress.ie/contact-us/)
- France: presse.ltr@editionslatableronde.fr / al.bonniel@editionslatableronde.fr (La Table Ronde, editionslatableronde.fr/Contacts)
- Italy: ufficiostampa@edizionieo.it (edizionieo.it/contatti)
- Portugal: comunicacao.pt@penguinrandomhouse.com (penguinlivros.pt/contactos/)
- Spain: prensacomics@planeta.es (Planeta Cómic)
- Czechia: zdena.krikavova@argo.cz (argo.cz/kontakty/); frantova.helena@euromedia.cz (Euromedia/Kalibr, euromedia.cz/en/for-media/)
- Good discovery pages: bloodhoundbooks.com/2026-titles ; Profile Autumn 2026 catalogue PDF ; Diogenes Herbst 2026 ; Picus 2026 catalogue

## Round 5 — ADDITIONAL VERIFIED CONTACTS (from round 4)
- Netherlands: publiciteit@amboanthos.nl (Ambo|Anthos)
- Italy: ufficiostampa@sellerio.it (Sellerio)
- Finland: nina.kuusisto@otava.fi, anni.gullichsen@otava.fi (Otava press)
- Greece: press@patakis.gr (Patakis)
- Romania: pr@litera.ro (Litera); emanuela.mihailiuc@humanitas.ro (Humanitas)
- France: cseube@editions-thierry-magnier.com (Thierry Magnier)
- Ireland: PGBooksPublicity@penguinrandomhouse.co.uk (Sandycove/Penguin Ireland)
- Germany: S. Fischer press contacts (fischerverlage.de press page)
ROUND 5 GOAL: ~110 new READY rows. Mine the ENTIRE 2025–2027 lists of the publishers above (one verified press inbox → many READY authors). Skip megastars; prefer debut / 2nd–4th book authors.

## Round 6 — ADDITIONAL VERIFIED CONTACTS (from round 5)
- Germany: julia.giordano@ / milena.kahlcke@ (Belletristik, FISCHER Tor) fischerverlage.de (fischerverlage.de/verlag/presse); iwallraff@kiwi-verlag.de (KiWi press, kiwi-verlag.de/verlag/presse); presse@aufbau-verlage.de; presselit@hanser.de / PresseBerlin@hanser.de (hanser-literaturverlage.de/presse)
- Austria: presse@zsolnay.at; Switzerland: presse@keinundaber.de (keinundaber.ch/kontakt)
- Italy: comunicazione@fazieditore.it (fazieditore.it/chi-siamo/contatti); ufficio.stampa@neripozza.it (2024 PDF — check current)
- Netherlands: publiciteit@pbo.nl (Prometheus, uitgeverijprometheus.nl/boekhandel/)
- Norway: ole.bjerkebakke@cappelendamm.no (presse.cappelendamm.no/contact_people); Finland: tiedotus@wsoy.fi (wsoy.fi/medialle/)
- Spain: afite@edestino.es (Destino Spanish fiction, Planeta press kits); maria.lopezr@planeta.es (Istoría)
- Discovery: piper.de/debuetromane; fischerverlage.de/spezial/highlights-herbst-2026; editions-jclattes.fr/livres/a-paraitre/; Livres Hebdo "68 primo romanciers rentrée 2026"; gyldendal.no hostens-boker-2026; IKAR edicny plan 2026 PDFs; 746books.com Irish fiction 2026

## Round 7 — ADDITIONAL VERIFIED CONTACTS / LEADS (from round 6)
- France: vtaillefer@ / nstraub@ / mrousset@calmann-levy.fr (Calmann-Lévy rentrée pages 2024–2025; check current)
- Spain: maria.lopezr@planeta.es (Istoría, planetadelibros.com/editorial/istoria/635); afite@edestino.es confirmed at planetadelibros.com/prensa/ediciones-destino/7
- Switzerland: presse@keinundaber.de confirmed at keinundaber.ch/de/service/presse/
- Discovery: Prometheus Najaar 2026 catalogue PDF; Kein & Aber Vorschau Frühling 2026 PDF; WSOY syksy 2026 (issuu); Otava releases on sttinfo.fi; Irish Times 2026-01-14 Irish debuts (Tully, Kinsella, Morgan, Cunning); IKAR Oct–Dec 2026 plans; Patakis autumn 2026; Garzanti 2026 debuts (Agnese Messina, Roberta Di Lorenzo – no press email yet); KiWi/Fischer leads Luna Ali, Charlotte Gneuß, Lenz Koppelstätter, Orkun Ertener
