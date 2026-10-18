# Shopify Lead Research Notes

Prepared for Oseni Ibrahim (Shopify Automation & Integration Specialist). This is research only: no emails have been sent, and every row has `send_status = NOT_SENT`.

## Status
- See `Shopify_Research_Summary.xlsx` → *By_Country* for the current qualified count against the targets (US 250 · UK 150 · CA 100 · AU 100 · DE 100).
- Research runs in batches by country across all five markets. Germany is researched with German and English queries, using each store's Impressum (legal notice) for the email, address and Inhaber/Geschäftsführer.
- The search tool allows about 200 searches per turn across all research agents, so each batch adds roughly 30–80 qualified rows. Yields fell in later rounds as the easiest stores were already taken.
- This file and both workbooks are regenerated after every batch.

## Research approach
1. **Discovery.** Niche + country searches restricted to `shop.app`. The Shop app lists only Shopify merchants, so each hit is already Shopify-proven. These were combined with independent-brand roundups and founder interviews.
2. **Contact and founder lookups.** 4–7 candidate store domains are searched together (`allowed_domains`) with "contact email" / "about founder" queries. This surfaces the brand's contact, about, FAQ, policy and terms pages, which carry the email, the founder name and the business location.
3. **Product detail.** One search covers 2–3 domains and asks for collections, products, sizes, colours and bundles. Each email's observation comes from these results, and the product or collection URL is recorded.
4. **Writing.** One automation opportunity is tied to that specific detail. Each email is written individually: 75–120 words, opening with the observation, offering one workflow idea and ending with one easy question. German-language stores get German emails.

## Verification rules (a lead is qualified only if every rule passes)
| Check | Rule |
|---|---|
| Shopify | `shopify_verified = YES` only with a source URL. Sources, strongest first: shop.app merchant page / Shopify customer story; myshopify.com or "Powered by Shopify"; Shopify-specific URL structure on the store's own domain (`/collections/`, `/products/`, `/pages/`, `/policies/`). The weaker URL-structure proof gets a lower `confidence_score`. |
| Country | The business location (address, "based in", shipping-from) is stated in a source, never assumed. |
| Email | Publicly listed on the store's own site (contact, policy, FAQ or about page). A named person's business address is labelled **Decision-maker**; hello@/info@/support@ etc. are labelled **General inbox**. Gmail/Yahoo-style addresses are held back for review, and nothing is guessed. |
| Decision maker | Founder/owner names come only from the store's own site or a credible public source (interview, press). When no name is verified, the email greets the team and the name fields stay empty. |
| Observation | A named product, collection, variant set, bundle, subscription or launch, with a source URL. |
| Opportunity | Tied to that observation. It never claims the store is losing sales, working manually or failing at fulfilment. |
| Email body | Validated by the builder: 75–120 words, no unresolved placeholders, a closing question, the correct sign-off, and no exact duplicate subjects or openings. |
| Duplicates | Removed by normalised website domain and by email address (see the *Duplicates_Removed* sheet). |

Rows that fail any rule go to the **Needs_Review** sheet with the reason in `last_error`, and they never appear in `Shopify_Leads`. Examples are an approximate contact page, an unconfirmed location, a Gmail-only inbox, and a missing product detail. Several leads were moved to Needs_Review by hand after spot checks, for example when the email page could not be pinned to a specific URL.

## Known limitations
- **No page browsing.** The research environment blocks direct page fetching, so every fact comes from search-result text. The emails, founders and product details shown in the results were real at search time, but a page may have changed since. Re-check an address before sending, especially rows flagged in `last_error`/notes.
- **Shopify evidence varies in strength.** About a third of rows rely on Shopify-style URL structure rather than shop.app proof, and `confidence_score` reflects this (roughly 70–80 vs 80–90).
- **Most emails are general inboxes.** Small brands rarely publish a founder's personal address. Even so, many rows greet a verified founder by first name.
- **Some brands are mid-size rather than small** (noted in the source report). Exclude them if you want only micro-brands.
- **Germany: check UWG §7 before sending.** German unfair-competition law (UWG §7) generally requires prior consent for advertising emails, including to businesses, and German courts apply it strictly. The German rows are researched public business contacts (from the Impressum), but get legal advice or use another first-contact channel before sending cold email to them. The UK (PECR) and Canada (CASL) also have rules on unsolicited commercial email. Include a clear opt-out and honour `do_not_contact`.
- **Holiday timing.** Emails mention the approaching holiday season, so they are best sent soon after research.

## Columns used for later automation
`send_status`, `date_sent`, `gmail_thread_id`, `reply_status`, `do_not_contact` and `last_error` are pre-filled (NOT_SENT / NO_REPLY / FALSE) or left blank, ready for a Google Apps Script sender. Only rows with `automation_action = READY` should be sent.
