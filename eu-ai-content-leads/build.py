"""Build the EU AI content & social media automation prospect database from work/*.jsonl.

python3 build.py  ->  EU_AI_Social_Media_Automation_Prospects_1000.xlsx / .csv and RESEARCH_REPORT.md
"""
import collections, csv, glob, json, os, re, datetime
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "EU_AI_Social_Media_Automation_Prospects_1000"
TODAY = datetime.date.today().isoformat()

COLUMNS = ["Prospect Name", "Company", "First Name", "Job Title", "Email", "Email Verification Source URL",
           "Company Website", "Country", "State", "City", "Industry / Niche", "Business Product or Service",
           "Social Media Platforms", "Social Profile URLs", "Verified Social Media Observation", "Observation Date",
           "Problem or Opportunity", "Proposed Automation Solution", "Recommended Services", "Buying Intent",
           "Business Fit Reason", "Personalization Detail", "Email Subject", "Email Body", "Research Source URLs",
           "Evidence", "Research Confidence", "Lead Status", "Send Status", "Date Sent", "Notes"]
KEYS = ["prospect_name", "company", "first_name", "job_title", "email", "email_verification_source_url",
        "company_website", "country", "state", "city", "industry_niche", "business_product_or_service",
        "social_media_platforms", "social_profile_urls", "verified_social_media_observation", "observation_date",
        "problem_or_opportunity", "proposed_automation_solution", "recommended_services", "buying_intent",
        "business_fit_reason", "personalization_detail", "email_subject", "email_body", "research_source_urls",
        "evidence", "research_confidence", "lead_status", "send_status", "date_sent", "notes"]

TARGETS = {"United Kingdom": 200, "Ireland": 50, "Netherlands": 100, "Sweden": 60, "Denmark": 50, "Norway": 40,
           "Finland": 30, "France": 120, "Spain": 100, "Italy": 100, "Germany": 100, "Austria": 25, "Switzerland": 25}

SIGNOFF = {"en": "Best regards", "nl": "Met vriendelijke groet", "sv": "Vänliga hälsningar", "da": "Venlig hilsen",
           "no": "Vennlig hilsen", "fi": "Ystävällisin terveisin", "fr": "Cordialement", "es": "Un saludo cordial",
           "it": "Cordiali saluti", "de": "Viele Grüße"}
OPTOUT = {
    "en": "If you'd prefer not to hear from me again, just reply \"no thanks\" and I won't contact you further.",
    "nl": "Liever geen berichten meer van mij? Antwoord dan kort met \"nee, bedankt\" en ik neem geen contact meer op.",
    "sv": "Vill du inte få fler mejl från mig räcker det att svara \"nej tack\", så hör jag inte av mig igen.",
    "da": "Hvis du ikke ønsker flere mails fra mig, så svar blot \"nej tak\", så kontakter jeg dig ikke igen.",
    "no": "Hvis du ikke ønsker flere e-poster fra meg, svar bare \"nei takk\", så tar jeg ikke kontakt igjen.",
    "fi": "Jos et halua minulta enää viestejä, vastaa vain \"ei kiitos\", niin en ota enää yhteyttä.",
    "fr": "Si vous préférez ne plus recevoir de messages de ma part, répondez simplement \"non merci\" et je ne vous recontacterai pas.",
    "es": "Si prefiere no recibir más mensajes míos, responda simplemente \"no, gracias\" y no volveré a contactarle.",
    "it": "Se preferisce non ricevere altri messaggi, risponda semplicemente \"no grazie\" e non la contatterò più.",
    "de": "Falls Sie keine weiteren Nachrichten wünschen, antworten Sie einfach kurz mit \"nein danke\", dann melde ich mich nicht mehr.",
}
GENERIC = set("""info hello hallo hej hei hola ciao bonjour contact contacto contatti contatto kontakt kontakte support
sales office team shop mail press presse prensa stampa pr media service services admin enquiries enquiry inquiries care
orders order help studio booking bookings reservations reservas prenotazioni events jobs careers karriere accounts
wholesale partnerships partner collabs collab marketing hr post postmaster webmaster general reception
customerservice kundenservice klantenservice servicio assistenza commercial vente ventes verkauf vendite ventas
lettings sales.team concierge welcome hi hey ask aloha business""".split())
FREEMAIL = {"gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com", "hotmail.co.uk", "outlook.com",
            "live.com", "icloud.com", "me.com", "aol.com", "gmx.de", "gmx.net", "web.de", "t-online.de", "orange.fr",
            "free.fr", "wanadoo.fr", "libero.it", "virgilio.it", "hotmail.fr", "hotmail.es", "hotmail.it", "yahoo.fr",
            "yahoo.es", "yahoo.it", "proton.me", "protonmail.com", "live.nl", "ziggo.nl", "kpnmail.nl", "telia.com"}
VENDORS = ("contactout", "rocketreach", "zoominfo", "apollo.io", "leadiq", "clay.com", "lusha", "signalhire",
           "anymailfinder", "hunter.io", "prospectoo", "snov.io", "adapt.io", "uplead", "seamless.ai", "datanyze",
           "kaspr", "getprospect", "emailformat", "email-format", "voilanorbert", "skrapp", "findymail", "aeroleads")
BANNED = ("i came across", "hope you are", "hope you're", "hope this finds", "i wanted to reach out", "reaching out",
          "cutting-edge", "cutting edge", "revolutioni", "best ai", "guarantee", "garantie", "garanti", "garantiz",
          "ich bin auf ihre", "ich hoffe, es geht", "je suis tombé", "j'espère que vous allez", "spero stia bene",
          "espero que esté", "espero que se encuentre", "me encontré con", "ik kwam uw", "ik hoop dat het goed")


def dom(u):
    u = (u or "").strip().lower()
    if not u:
        return ""
    if "//" not in u:
        u = "//" + u
    d = urlparse(u).netloc
    return d[4:] if d.startswith("www.") else d


def words(t):
    return len(re.findall(r"\w+(?:['’.-]\w+)*", t or ""))


def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "work", "*.jsonl"))):
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:
                print("bad json", os.path.basename(f), n)
                continue
            d["_file"] = os.path.basename(f)
            rows.append(d)
    return rows


def check(r):
    probs = []
    em = r["email"].lower()
    local, _, edom = em.partition("@")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", em):
        probs.append("Email missing or malformed")
    elif r.get("email_type") != "Individual" or local in GENERIC or re.sub(r"[\d._-]+$", "", local) in GENERIC:
        probs.append("Only a generic inbox found; individual email not verified")
    elif edom in FREEMAIL:
        probs.append("Email is a free webmail address, not a company domain")
    src = r["email_verification_source_url"].lower()
    if not src.startswith("http"):
        probs.append("No email verification source URL")
    elif any(v in src for v in VENDORS):
        probs.append("Email source is a contact-data vendor (not acceptable)")
    for k, label in (("prospect_name", "decision-maker name"), ("job_title", "job title"),
                     ("verified_social_media_observation", "observation"), ("research_source_urls", "research sources"),
                     ("proposed_automation_solution", "proposed solution"), ("company_website", "website")):
        if not r[k].strip():
            probs.append(f"Missing {label}")
    if r["country"] not in TARGETS:
        probs.append(f"Country not in campaign: {r['country']}")
    body = r["email_body"]
    wc = words(body)
    if not 70 <= wc <= 120:
        probs.append(f"Email body is {wc} words (needs 70-120)")
    if "—" in body or "–" in body or "—" in r["email_subject"] or "–" in r["email_subject"]:
        probs.append("Email contains an em/en dash")
    low = body.lower()
    hit = [b for b in BANNED if b in low]
    if hit:
        probs.append("Generic phrase: " + hit[0])
    if "?" not in body.strip().split("\n")[-1]:
        probs.append("Email does not end with a question")
    if body.count("?") > 1:
        probs.append("Email asks more than one question")
    if r["first_name"] and r["first_name"].split()[0].lower() not in body.split("\n")[0].lower() \
            and r["prospect_name"].split()[-1].lower() not in body.split("\n")[0].lower():
        probs.append("Greeting does not use the prospect's name")
    if re.search(r"\[|\{|<|TODO|XXX", body):
        probs.append("Unresolved placeholder in email")
    if r["language"] not in SIGNOFF:
        probs.append("Unknown email language")
    if r["research_confidence"] not in ("High", "Medium"):
        probs.append(f"Research confidence {r['research_confidence'] or 'missing'}")
    if r["buying_intent"] not in ("High", "Medium"):
        probs.append("Buying intent not supported")
    if not r["email_subject"].strip():
        probs.append("Missing subject")
    return probs


def full_body(r):
    so = SIGNOFF.get(r["language"], "Best regards")
    if r["language"] == "de" and r["country"] == "Switzerland":
        so = "Freundliche Grüsse"
    return (f"{r['email_body'].rstrip()}\n\n{so},\nOseni Ibrahim\nAI Automation & Content Creation Developer\n\n"
            f"{OPTOUT.get(r['language'], OPTOUT['en'])}")


def main():
    excl = {l.strip().lower() for l in open(os.path.join(HERE, "work", "exclude_domains.txt")) if l.strip() and not l.startswith("#")}
    raw = load()
    out, seen_dom, seen_mail, seen_person, subjects = [], {}, {}, {}, collections.Counter()
    dup_count = 0
    for d in raw:
        r = {k: str(d.get(k, "") or "").strip() for k in KEYS + ["email_type", "language", "review_reason", "email_evidence"]}
        r["_file"] = d["_file"]
        r["email"] = r["email"].lower().strip(" .;,<>")
        r["send_status"], r["date_sent"] = "Not Sent", ""
        dm = dom(r["company_website"])
        person = (r["prospect_name"].lower(), dm)
        dup_of = None
        if dm and dm in excl:
            dup_of = "already emailed in the Shopify outreach"
        elif dm and dm in seen_dom:
            dup_of = seen_dom[dm]
        elif r["email"] and r["email"] in seen_mail:
            dup_of = seen_mail[r["email"]]
        if dup_of:
            dup_count += 1
            r["lead_status"] = "Excluded"
            r["notes"] = f"Duplicate of {dup_of}. " + r["notes"]
            out.append(r)
            continue
        key = f"{r['company']} ({dm})"
        if dm:
            seen_dom[dm] = key
        if r["email"]:
            seen_mail[r["email"]] = key
        probs = check(r)
        if r["review_reason"]:
            probs.append(r["review_reason"])
        subjects[r["email_subject"].lower()] += 1
        r["_probs"] = probs
        out.append(r)
    for r in out:
        if r.get("lead_status") == "Excluded":
            continue
        if subjects[r["email_subject"].lower()] > 1:
            r["_probs"].append("Subject line duplicates another prospect")
        r["lead_status"] = "Ready" if not r["_probs"] else "Needs Review"
        if r["_probs"]:
            r["notes"] = ("Review: " + "; ".join(r["_probs"]) + ". " + r["notes"]).strip()
        if r["email_type"] == "Generic" and r["email"]:
            r["notes"] = f"Generic inbox on file: {r['email']}. " + r["notes"]
        if r["email_evidence"]:
            r["notes"] += f" Email evidence: {r['email_evidence']}"
        if r["email_body"]:
            r["email_body"] = full_body(r)
    order = {"Ready": 0, "Needs Review": 1, "Excluded": 2}
    out.sort(key=lambda r: (order[r["lead_status"]], list(TARGETS).index(r["country"]) if r["country"] in TARGETS else 99, r["company"].lower()))

    wb = Workbook()
    ws = wb.active
    ws.title = "Prospects"
    ws.append(COLUMNS)
    for r in out:
        ws.append([r[k] for k in KEYS])
    head = PatternFill("solid", fgColor="1F3A5F")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = head
        c.alignment = Alignment(wrap_text=True, vertical="center")
    widths = {"Email Body": 70, "Verified Social Media Observation": 45, "Problem or Opportunity": 45,
              "Proposed Automation Solution": 45, "Evidence": 40, "Notes": 50, "Email Subject": 34,
              "Research Source URLs": 40, "Business Fit Reason": 40, "Personalization Detail": 40}
    for i, col in enumerate(COLUMNS, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(col, 20)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

    ready = [r for r in out if r["lead_status"] == "Ready"]
    review = [r for r in out if r["lead_status"] == "Needs Review"]
    excluded = [r for r in out if r["lead_status"] == "Excluded"]
    cnt_ready = collections.Counter(r["country"] for r in ready)
    sm = wb.create_sheet("By_Country")
    sm.append(["Country", "Target", "Ready", "Needs Review", "Remaining to target"])
    for c, t in TARGETS.items():
        sm.append([c, t, cnt_ready[c], sum(1 for r in review if r["country"] == c), max(0, t - cnt_ready[c])])
    sm.append(["Total", sum(TARGETS.values()), len(ready), len(review), max(0, 1000 - len(ready))])
    for c in sm[1]:
        c.font = Font(bold=True)
    wb.save(os.path.join(HERE, BASE + ".xlsx"))
    with open(os.path.join(HERE, BASE + ".csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for r in out:
            w.writerow([r[k] for k in KEYS])

    live = ready + review
    svc = lambda *ks: sum(1 for r in live if any(k in (r["recommended_services"] + " " + r["proposed_automation_solution"]).lower() for k in ks))
    niche = lambda *ks: sum(1 for r in live if any(k in r["industry_niche"].lower() for k in ks))
    files = sorted({r["_file"] for r in out})
    reasons = collections.Counter(p.split(":")[0] for r in review for p in r["_probs"])
    rep = f"""# Research report: European AI content & social media automation prospects

Generated {TODAY} by `build.py` from {len(files)} research batch files. No emails have been sent: every row is `Send Status = Not Sent`.

| # | Measure | Count |
|---|---|---|
| 1 | Businesses researched (all records) | {len(out)} |
| 2 | Qualified prospects (Ready + Needs Review) | {len(live)} |
| 3 | **Ready** prospects | **{len(ready)}** of 1,000 target |
| 4 | Needs Review | {len(review)} |
| 5 | Excluded (duplicates / already emailed) | {len(excluded)} |
| 6 | Verified individual emails | {sum(1 for r in live if r['email_type'] == 'Individual' and not any('generic' in p.lower() for p in r['_probs']))} |
| 7 | Generic inbox only | {sum(1 for r in live if r['email_type'] == 'Generic')} |
| 8 | High intent | {sum(1 for r in live if r['buying_intent'] == 'High')} |
| 9 | Medium intent | {sum(1 for r in live if r['buying_intent'] == 'Medium')} |
| 10 | E-commerce / DTC brands | {niche('e-commerce', 'ecommerce', 'dtc', 'brand', 'shop')} |
| 11 | Beauty, skincare & wellness | {niche('beauty', 'skin', 'cosmetic', 'spa', 'salon', 'wellness', 'aesthetic')} |
| 12 | Fashion & lifestyle | {niche('fashion', 'apparel', 'jewel', 'lifestyle', 'clothing', 'accessor')} |
| 13 | Real estate | {niche('real estate', 'estate agen', 'property', 'makelaar', 'immobili', 'inmobili', 'letting')} |
| 14 | Other industries | {len(live) - niche('e-commerce', 'ecommerce', 'dtc', 'brand', 'shop', 'beauty', 'skin', 'cosmetic', 'spa', 'salon', 'wellness', 'aesthetic', 'fashion', 'apparel', 'jewel', 'lifestyle', 'clothing', 'accessor', 'real estate', 'estate agen', 'property', 'makelaar', 'immobili', 'inmobili', 'letting')} |
| 15 | Suited to AI UGC videos | {svc('ugc')} |
| 16 | Suited to AI image creation | {svc('image', 'photo', 'visual')} |
| 17 | Suited to social media automation | {svc('schedul', 'calendar', 'automat', 'publishing', 'repurpos')} |
| 18 | Suited to AI video generation | {svc('video', 'reel', 'shorts', 'tiktok')} |
| 19 | Suited to marketing workflow automation | {svc('n8n', 'make', 'zapier', 'crm', 'dm ', 'chatbot', 'lead capture', 'workflow')} |
| 20 | Personalised outreach emails written | {sum(1 for r in live if r['email_body'])} |
| 21 | Duplicates removed | {dup_count} |
| 22 | Research batches completed | {len(files)} |
| 23 | Excel file | `{BASE}.xlsx` |
| 24 | CSV file | `{BASE}.csv` |

## Ready by country
| Country | Target | Ready | Needs Review |
|---|---|---|---|
""" + "\n".join(f"| {c} | {t} | {cnt_ready[c]} | {sum(1 for r in review if r['country'] == c)} |" for c, t in TARGETS.items()) + f"""

## Why records are in Needs Review
""" + "\n".join(f"- {k}: {v}" for k, v in reasons.most_common()) + """

## 25. Research limitations and open verification issues
- **Search results only.** This environment blocks direct page fetching, so every fact comes from search-result text from the company's own site or another public source. Pages may have changed since. Re-check each address and observation before sending.
- **Social media was checked through search, not by browsing profiles.** Observations cite a named product, campaign, job ad or page. They avoid claims about posting frequency or missing video unless a source states it.
- **Strict email rule.** A record is Ready only when a named decision-maker's own work address appears next to their name on a legitimate public page. Contact-data vendor sites and guessed patterns are never used. Companies that publish only a generic inbox stay in Needs Review, with that inbox noted.
- **EU/UK email law.** These are researched business contacts, not consent. The UK and Ireland (PECR) allow B2B email to corporate addresses with an opt-out. France, Spain, Italy, the Netherlands and the Nordics generally allow relevant B2B email under legitimate interest, with clear identification and an opt-out. Germany and Austria (UWG §7, TKG) and Switzerland (UWG Art. 3) are strict, so get advice before cold-emailing those rows. Named work emails are personal data under the GDPR: send only relevant messages, honour opt-outs immediately, and be ready to say where the address came from. Every draft includes an opt-out line in the recipient's language.
- **AI UGC.** Proposals use approved product material and truthful claims only. No fake testimonials or real people's likenesses, with disclosure where platforms or laws require it.
"""
    open(os.path.join(HERE, "RESEARCH_REPORT.md"), "w", encoding="utf-8").write(rep)
    print(f"READY {len(ready)} | NEEDS_REVIEW {len(review)} | EXCLUDED {len(excluded)}")
    print(dict(cnt_ready))
    print("review reasons", dict(reasons.most_common(8)))


if __name__ == "__main__":
    main()
