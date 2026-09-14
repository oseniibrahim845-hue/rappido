# Australia — Prospecting Worklist

Discovery targets for the NSW-first run. Every URL below is a real search result,
not a generated guess. Open them in a browser, harvest, then feed rows through
`tools/merge_leads.py`.

---

## The strategy change

The original brief leaned on `site:amazon.com "author" "@gmail.com"`. That pattern is
weak, and it's worth knowing why before burning a run on it: **Amazon Author Central
bios rarely display an email address.** Author Central is not built as a contact
directory, so the query is fishing in the wrong pond — which is consistent with 254
rows in the existing 775-row sheet having no Amazon source URL at all.

For Australia, invert the order. Find the author where contact details are *published
to be used*, then verify the Amazon listing second:

```
find author + published contact email  ->  verify Amazon book/author page  ->  personalize
```

This is also the stronger compliance position. Spam Act 2003 inferred consent rests on
an address conspicuously published in a professional capacity, relevant to the message.
A directory listing where an author publishes contact details *specifically to be
approached about their writing* satisfies that far more cleanly than an address
scraped from a book's front matter.

---

## Tier 1 — directories where authors publish contact details to be approached

Highest yield, strongest consent basis. Work these first.

| Source | URL | Notes |
|---|---|---|
| ASA — Find a Creator | https://www.asauthors.org.au/find-a-creator/ | Searchable directory of Australian authors and illustrators. Members list themselves for speaking, teaching, ghostwriting, judging — i.e. they published contact details *to be contacted professionally*. Filter by state. |
| ASA — Directory search | https://www.asauthors.org/searchDirectory | Alternate search entry point. |
| ASA — Book Industry Directory | https://www.asauthors.org.au/resources/industry-directory/ | Industry players; useful for cross-referencing publishers and imprints. |
| Small Press Network members | https://independentpublishers.org.au/members/indiemosh/ | Member listings lead to small presses and their author rosters. |

**State writers' centres** — member directories and event/programme pages. Same logic:

- Writing NSW — https://writingnsw.org.au/getsupport/information-for-writers/self-publishing/
- Australian Writers' Centre — https://www.writerscentre.com.au/blog/indie-author-success-stories-to-inspire-you/
- Also check: Writers Victoria, Queensland Writers Centre, Writers SA, Writing WA,
  Tasmanian Writers Centre, ACT Writers, NT Writers Centre.

## Tier 2 — self-publishing services and their author showcases

Australian indie authors cluster around these. Client showcases, testimonial pages and
"our authors" listings are dense with named authors who have Amazon listings.

| Source | URL |
|---|---|
| IndieMosh (NSW, since 2009; joined Tellwell 2023) | https://indiemosh.com.au/ |
| Jennifer Mosher (IndieMosh founder) | https://jennifermosher.com.au/ |
| Author Services Australia | https://www.authorservicesaustralia.com.au/ |
| Greenhill Publishing | https://greenhillpublishing.com.au/ |
| Australian Authors directory | https://australianauthors.com.au/ |
| Australian Authors store | https://australianauthorsstore.com/ |
| Australian Independent Booksellers — new releases | https://www.indies.com.au/latest |

## Tier 3 — named starting candidates

Surfaced by search as Australian indie authors. **None are verified yet** — no email
has been confirmed and no Amazon page checked. These are Stage A inputs, not leads.

| Author | Lead |
|---|---|
| Jodi Gibson | Self-published debut *The Memories We Hide* (2019) |
| Shane W. Smith | Graphic novelist, *Undad* series, Kickstarter-funded |
| Dianne Blacklock | Moved from traditional publishing to indie |
| Aaron Dryden | Brisbane, historical fiction, stocked by indie bookstores |
| Jennifer Mosher | IndieMosh founder, own titles on Amazon |

## Genre and community veins

- Australian Romance Readers Association — https://australianromancereaders.wordpress.com/
- Petrichor and Pages (Brisbane indie bookshop, est. 2025, indie-author focused)

---

## Harvest procedure

For each author found:

1. **Email** — copy the address exactly as displayed. If it's obfuscated, skip it.
   Never reconstruct or guess a pattern.
2. **Amazon** — find their author page or a book listing. Record the URL.
   No Amazon presence, no row.
3. **Hook** — one specific fact for `personalized_opening`: the book's actual premise,
   who it's for, the author's relevant background, the real-world origin.
4. **Record** — all 15 columns per `PROMPT.md`. `send_status` = `Not Sent`,
   `date_sent` blank.
5. **Location** — state the real relationship (current residence vs. birthplace vs.
   setting). Don't upgrade a book's setting into a residence.

Then:

```bash
python3 tools/merge_leads.py --batch batch.json --run-id 2026-09-14-nsw-01 --dry-run
python3 tools/merge_leads.py --batch batch.json --run-id 2026-09-14-nsw-01
python3 tools/validate_leads.py --strict
```

## Exclusions to apply while harvesting

Minors · deceased authors · company/imprint addresses rather than a person ·
"Summary of <Popular Book>" content-mill names · pages stating no unsolicited
enquiries · anyone previously opted out.
