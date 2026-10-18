# Shopify inventory/order-automation lead research (research only — DO NOT send anything)
Client: Oseni Ibrahim, Shopify Automation & Integration Specialist. Goal: 700 unique qualified Shopify stores selling physical products — US 250, UK 150, Canada 100, Australia 100, Germany 100.

## Environment limits
- Web pages CANNOT be opened (fetch blocked). Use WebSearch only; every fact must appear in search-result text. Use `allowed_domains` to restrict a search to one store domain (or a batch of 4–7 store domains) — snippets then show contact pages, collections, policies.
- Never fill any field from memory. Never guess or construct an email. Never invent names, products, observations or problems.

## Who qualifies (all required for READY)
1. Real, active store selling PHYSICAL products, based in your assigned country (stated on the site: shipping-from/about/contact address/"based in").
2. Credible Shopify evidence (record the source URL in shopify_verification_source), strongest first:
   - shop.app/m/... merchant page for the brand (Shop app lists only Shopify merchants), or a shopify.com customer story / Shopify blog naming the brand;
   - a *.myshopify.com address or "Powered by Shopify" text seen in a result;
   - Shopify-specific URL structure on the store's own domain seen in results, e.g. /collections/<x>, /products/<x>, /pages/<x>, /policies/refund-policy — record one such URL (weaker; lower confidence_score).
3. A publicly listed business email on the store's own site (contact/about/FAQ/policies/imprint page) or another credible public source. Decision-maker address (e.g. founder name@brand) preferred; otherwise a general inbox (hello@, info@, support@, contact@, orders@) is ALLOWED here — set email_type "General inbox". Marketplace/agency/platform addresses not allowed.
4. One specific verified product/collection detail (named collection, product with sizes/colours/variants, bundle/kit, subscription, launch, multiple locations/channels if stated).
5. One relevant automation opportunity tied to that detail — never claim they lose sales, process orders manually or have fulfillment problems. If they visibly already offer something (e.g. back-in-stock alerts), suggest an integration/improvement instead.
- Exclude: dropshipping directories, marketplaces (Amazon/Etsy-only), digital-only, inactive stores, big public companies / household-name brands (prefer small & mid-size independent brands).
- Decision maker: founder/co-founder/owner/ecommerce/operations lead, named on the store's About/team page or a credible public source (press interview, LinkedIn snippet). If not verified leave owner_name/first_name empty and greet "Hi [Store] team," (German: "Hallo [Store]-Team,").

## Email (you write it)
- 75–120 words body (excluding subject), simple natural professional English (German stores whose site is in German: natural professional German, "Sie" form).
- Open with the verified observation; one inventory/order consideration (holiday season is approaching — OK to mention); "I build Shopify automation systems that help stores simplify inventory updates, order processing, and supplier notifications" (vary wording); one specific workflow idea; end with ONE easy question. No prices, no meeting/call request, no hype, no unsupported claims, no placeholders.
- Sign-off exactly: "Best regards,\nOseni Ibrahim\nShopify Automation & Integration Specialist" (German: "Viele Grüße,\nOseni Ibrahim\nShopify Automation & Integration Specialist").
- Subject: short, specific, varied (e.g. "Quick inventory idea for <Store>", "<Collection> stock alerts", German "Kurze Idee zu Ihrem Lagerbestand").
- Each email must be unique in wording, not a template with names swapped.

## Dedup
Before writing, grep -i the store domain in /home/user/rappido/shopify-leads/work/*.jsonl. Skip known domains.

## Output — append ONE JSON object per line (valid JSON; use \n inside strings)
{"store_name":"","website":"https://domain","country":"United States|United Kingdom|Canada|Australia|Germany","product_niche":"","owner_name":"","first_name":"","owner_role":"","email":"","email_type":"Decision-maker|General inbox","shopify_verified":"YES|NO","shopify_verification_source":"URL","product_or_collection":"","personalized_store_observation":"","inventory_order_automation_opportunity":"","opportunity_reasoning":"","personalized_subject":"","personalized_email_body":"","research_source_url":"URL (product/collection page)","contact_source_url":"URL where the email appears","email_verification_status":"PUBLICLY_LISTED","personalization_status":"READY|NEEDS_REVIEW","confidence_score":0-100,"review_reason":""}
- personalization_status READY only if rules 1–5 are all met with source URLs; else NEEDS_REVIEW + review_reason.
- confidence_score: e.g. 85–95 = shop.app/myshopify proof + email on own contact page + named decision maker; 70–84 = Shopify URL-structure proof + general inbox; <70 = something weak.
Use a scratchpad subfolder for helper scripts: /tmp/claude-0/-home-user-rappido/85eb8748-a21e-58e5-b6eb-a7dcb5a964d2/scratchpad/sh_<tag>/

## Finish with a short report
Stores researched; READY; NEEDS_REVIEW; decision-maker vs general emails; duplicates skipped; tactics that worked.
