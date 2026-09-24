import json, glob, re, sys, os
from collections import Counter, OrderedDict
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SP = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SP, "Shopify_AI_Automation_Prospects_1000.xlsx")

BANNED = ["seamless", "tailored", "stunning", "revolutionize", "revolutionise", "game changer",
          "game-changer", "cutting edge", "cutting-edge", "unlock", "supercharge"]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PLACEHOLDER_RE = re.compile(r"\[[^\]]*\]|\{[^}]*\}|<[^>]*>")

def domain(url):
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    d = urlparse(url).netloc.lower().split(":")[0]
    return d[4:] if d.startswith("www.") else d

def root(d):
    parts = d.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "com", "net", "org") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])

def s(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v if x)
    return str(v).strip()

OPP_CATS = OrderedDict([
    ("AI customer support agent", ["customer support", "support agent", "ticket", "faq", "support inbox", "customer service"]),
    ("Order status / WISMO agent", ["order status", "wismo", "where is my order", "tracking"]),
    ("Inventory monitoring / low stock alerts", ["inventory", "low stock", "low-stock", "stock alert", "restock", "back-in-stock", "stockout"]),
    ("Subscription management workflows", ["subscription", "replenish", "churn"]),
    ("Returns / refund workflow", ["return", "refund", "exchange"]),
    ("Fulfillment / order exception alerts", ["fulfil", "fulfill", "exception", "shipping delay", "3pl", "warehouse"]),
    ("Sales / management reporting", ["report", "dashboard", "sales summary"]),
    ("Wholesale / B2B order workflows", ["wholesale", "b2b", "stockist", "retailer"]),
    ("CRM synchronization", ["crm", "hubspot", "gohighlevel", "zoho", "airtable", "google sheets", "sync"]),
    ("Customer segmentation / reactivation", ["segment", "reactivat", "win-back", "winback", "lapsed", "loyalty"]),
    ("Abandoned cart / post-purchase automation", ["abandoned", "post-purchase", "post purchase", "review request"]),
    ("Product content automation", ["product content", "product description", "catalog content", "product launch", "listing"]),
    ("WhatsApp / multichannel messaging", ["whatsapp", "sms"]),
    ("International / multi-store operations", ["international", "multi-currency", "cross-border", "multi-store", "markets"]),
])

IND_MAP = [("Jewelry", ["jewel"]), ("Beauty & Personal Care", ["beauty", "skin", "cosmetic", "hair", "personal care", "fragrance"]),
           ("Supplements & Health", ["supplement", "nutrition", "health", "wellness"]), ("Food & Beverage", ["food", "beverage", "coffee", "drink", "brew", "tea"]),
           ("Pet Products", ["pet"]), ("Baby Products", ["baby"]), ("Home & Furniture", ["home", "furniture", "kitchen", "bedding", "decor"]),
           ("Electronics", ["electronic", "audio", "gadget"]), ("Automotive", ["auto", "car care"]),
           ("Outdoor & Sports", ["outdoor", "sport", "fitness"]), ("Fashion & Apparel", ["fashion", "apparel", "footwear", "clothing", "underwear", "lingerie", "accessor"])]

def norm_industry(ind, cat):
    t = (ind + " " + cat).lower()
    for name, kws in IND_MAP:
        if any(k in ind.lower() for k in kws):
            return name
    for name, kws in IND_MAP:
        if any(k in t for k in kws):
            return name
    return ind or "Other"

def opp_cats(text):
    t = text.lower()
    out = [c for c, kws in OPP_CATS.items() if any(k in t for k in kws)]
    return out or ["Other"]

HEADERS = ["Prospect Name", "Company", "First Name", "Job Title", "Email", "Country", "State", "City",
           "Website", "Shopify Store URL", "Shopify Verified", "Shopify Plus", "Industry", "Product Category",
           "Company Size", "Product Count Signal", "Shopify Apps", "Operational Signal", "Automation Opportunity",
           "Buying Intent", "Personalization Detail", "Personalization Reason", "Personalized Opening",
           "Subject Line", "Email Body", "Source URL", "Evidence", "Evidence Type", "Research Confidence",
           "Lead Status", "Send Status", "Date Sent", "Notes"]


STALE_CONTACTS = {
    "cotopaxi.com": "Davis Smith's current role at Cotopaxi not confirmed (source quotes him as Founder/CEO); contact cleared",
    "kettleandfire.com": "Justin Mares now listed as CEO of Truemed; contact cleared",
    "drinkolipop.com": "Ben Goodwin stepped down as CEO; contact cleared",
}
INTENT_OVERRIDES = {
    "nativecos.com": ("Low", "Owned by Procter & Gamble; enterprise buying process, intent lowered to Low"),
}
ASSUMED_RE = re.compile(r"(domain|website|url)[^.|]*(assumed|inferred|not seen|not shown|not confirmed|not captured|not evidenced)", re.I)
CONF_ORDER = {"High": 3, "Medium": 2, "Low": 1}

def qa(r, d):
    """Return a rejection reason, or '' and mutate r in place."""
    notes = s(r.get("notes"))
    assumed = bool(ASSUMED_RE.search(notes)) or d == "chubbiesshorts.com"
    conf = s(r.get("research_confidence"))
    if s(r.get("shopify_verified")) == "Likely" and conf == "Low":
        return "Shopify evidence indirect and research confidence Low (cannot be verified)"
    if assumed and conf == "Low":
        return "Website domain not confirmed by any source and research confidence Low"
    if not s(r.get("country")):
        return "Country/HQ not verified"
    if assumed:
        r["notes"] = "VERIFY DOMAIN: website not shown in any search result, taken from brand name. " + notes
        if CONF_ORDER.get(conf, 0) > 2:
            r["research_confidence"] = "Medium"
    if d in STALE_CONTACTS:
        r["prospect_name"] = r["first_name"] = r["job_title"] = r["contact_source_url"] = ""
        r["notes"] = STALE_CONTACTS[d] + ". " + s(r.get("notes"))
    if d in INTENT_OVERRIDES:
        r["buying_intent"], why = INTENT_OVERRIDES[d]
        r["notes"] = why + ". " + s(r.get("notes"))
    return ""

def load():
    recs = []
    for f in sorted(glob.glob(os.path.join(SP, "batch*", "seg*.json"))):
        with open(f) as fh:
            data = json.load(fh)
        batch = os.path.basename(os.path.dirname(f))
        for r in data:
            r["_file"] = os.path.basename(f)
            r["_batch"] = batch
            if not s(r.get("country")) and r["_file"].startswith("seg4_us"):
                r["country"] = "United States"
                r["notes"] = "Country taken from the US research segment; HQ city not evidenced. " + s(r.get("notes"))
            recs.append(r)
    return recs

def load_copy():
    copy = {}
    for f in glob.glob(os.path.join(SP, "copy", "*.json")):
        with open(f) as fh:
            for r in json.load(fh):
                copy[domain(r["website"])] = r
    return copy

def main():
    recs = load()
    copy = load_copy()
    seen, keep = {}, []
    dups, invalid = [], []
    for r in recs:
        d = domain(s(r.get("website")))
        name_key = re.sub(r"[^a-z0-9]", "", s(r.get("company")).lower())
        problems = []
        if not d or "." not in d:
            problems.append("no valid website")
        if s(r.get("shopify_verified")) not in ("Yes", "Likely"):
            problems.append("Shopify not verified")
        if not s(r.get("personalization_detail")):
            problems.append("no personalization detail")
        if not r.get("source_urls") and not s(r.get("shopify_evidence_url")):
            problems.append("no source URL")
        if not problems:
            reason = qa(r, d)
            if reason:
                problems.append(reason)
        if problems:
            invalid.append((s(r.get("company")), d, "; ".join(problems)))
            continue
        key = root(d)
        if key in seen or name_key in seen:
            dups.append((s(r.get("company")), d, r["_file"]))
            continue
        seen[key] = seen[name_key] = True
        r["_domain"] = d
        keep.append(r)

    if os.environ.get("DUMP"):
        out = [{"website": r["website"], "company": s(r.get("company")), "first_name": s(r.get("first_name")) if s(r.get("contact_source_url")) else "",
                "country": s(r.get("country")), "product_category": s(r.get("product_category")),
                "operational_signal": s(r.get("operational_signal")), "automation_opportunity": s(r.get("automation_opportunity")),
                "personalization_detail": s(r.get("personalization_detail"))} for r in keep]
        half = (len(out) + 1) // 2
        os.makedirs(os.path.join(SP, "copy_in"), exist_ok=True)
        json.dump(out[:half], open(os.path.join(SP, "copy_in", "part1.json"), "w"), indent=1)
        json.dump(out[half:], open(os.path.join(SP, "copy_in", "part2.json"), "w"), indent=1)
        print("dumped", len(out)); return
    rows, issues = [], []
    for r in keep:
        email = s(r.get("email"))
        notes = [s(r.get("notes"))] if s(r.get("notes")) else []
        if email:
            if not EMAIL_RE.match(email):
                notes.append(f"Removed malformed email '{email}'")
                email = ""
            elif not s(r.get("email_source_url")):
                notes.append(f"Removed email '{email}' with no source URL")
                email = ""
        if email:
            ed = email.split("@")[1].lower()
            if root(ed) != root(r["_domain"]):
                notes.append(f"Email domain ({ed}) differs from website domain; published by the brand per source")
            notes.append(f"Email source: {s(r.get('email_source_url'))}")
        else:
            notes.append("No verified email")
        first = s(r.get("first_name"))
        if first and s(r.get("contact_source_url")):
            notes.append(f"Contact source: {s(r.get('contact_source_url'))}")
        elif first:
            notes.append("Contact name had no source URL; name removed")
            first = ""
            r["prospect_name"] = ""
            r["job_title"] = ""
        c = copy.get(r["_domain"], {})
        opening, subject, body = s(c.get("opening")), s(c.get("subject")), s(c.get("body"))
        if not (opening and subject and body):
            issues.append((s(r.get("company")), "missing email copy"))
        for field, txt in (("subject", subject), ("opening", opening), ("body", body)):
            if PLACEHOLDER_RE.search(txt):
                issues.append((s(r.get("company")), f"placeholder in {field}"))
            low = txt.lower()
            for b in BANNED:
                if b in low:
                    issues.append((s(r.get("company")), f"banned word '{b}' in {field}"))
        srcs = r.get("source_urls") or []
        if isinstance(srcs, str):
            srcs = [srcs]
        srcs = [u for u in srcs if u]
        if s(r.get("shopify_evidence_url")) and s(r.get("shopify_evidence_url")) not in srcs:
            srcs.insert(0, s(r.get("shopify_evidence_url")))
        evidence = s(r.get("shopify_evidence"))
        if s(r.get("shopify_plus_evidence")):
            evidence += " | Plus: " + s(r.get("shopify_plus_evidence"))
        plus = s(r.get("shopify_plus")) or "Not verified"
        rows.append({
            "Prospect Name": s(r.get("prospect_name")) or f"{s(r.get('company'))} team (general inbox)",
            "Company": s(r.get("company")),
            "First Name": first,
            "Job Title": s(r.get("job_title")),
            "Email": email,
            "Country": s(r.get("country")),
            "State": s(r.get("state")),
            "City": s(r.get("city")),
            "Website": s(r.get("website")),
            "Shopify Store URL": s(r.get("shopify_store_url")) or s(r.get("website")),
            "Shopify Verified": s(r.get("shopify_verified")),
            "Shopify Plus": plus,
            "Industry": norm_industry(s(r.get("industry")), s(r.get("product_category"))),
            "Product Category": s(r.get("product_category")),
            "Company Size": s(r.get("company_size")) or "Not verified",
            "Product Count Signal": s(r.get("product_count_signal")) or "Not verified",
            "Shopify Apps": s(r.get("shopify_apps")) or "Not verified",
            "Operational Signal": s(r.get("operational_signal")),
            "Automation Opportunity": s(r.get("automation_opportunity")),
            "Buying Intent": s(r.get("buying_intent")),
            "Personalization Detail": s(r.get("personalization_detail")),
            "Personalization Reason": s(r.get("personalization_reason")),
            "Personalized Opening": opening,
            "Subject Line": subject,
            "Email Body": body,
            "Source URL": "\n".join(srcs),
            "Evidence": evidence,
            "Evidence Type": s(r.get("evidence_type")),
            "Research Confidence": s(r.get("research_confidence")),
            "Lead Status": "New - Researched",
            "Send Status": "Not sent" if email else "Not sent - needs contact",
            "Date Sent": "",
            "Notes": " | ".join(n for n in notes if n),
            "_batch": r["_batch"],
        })

    subj_counts = Counter(r["Subject Line"] for r in rows)
    for sub, n in subj_counts.items():
        if n > 1 and sub:
            issues.append((sub, f"subject used {n} times"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Shopify Automation Prospects"
    ws.append(HEADERS)
    for r in rows:
        ws.append([r[h] for h in HEADERS])
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = hdr_fill
        c.alignment = Alignment(wrap_text=True, vertical="center")
    widths = {"Email Body": 70, "Personalized Opening": 50, "Source URL": 55, "Evidence": 50,
              "Operational Signal": 45, "Automation Opportunity": 45, "Personalization Detail": 45,
              "Personalization Reason": 45, "Notes": 45, "Subject Line": 35}
    for i, h in enumerate(HEADERS, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(h, 18)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions

    sm = wb.create_sheet("Research Summary")
    def sec(title):
        sm.append([])
        sm.append([title])
        sm.cell(sm.max_row, 1).font = Font(bold=True, size=12)
    sm.append(["Shopify AI Automation Prospects - Research Summary"])
    sm.cell(1, 1).font = Font(bold=True, size=14)
    sm.append(["Scope note", "Batch 1 pilot (search-only research; 138 candidates researched, 107 passed QA). Direct store website access was blocked by the session network policy, so all verification comes from public search results (Shopify case studies, tech profiles, press, agency case studies)."])
    tot = len(rows)
    metrics = [
        ("Total candidate records researched", len(recs)),
        ("Total prospects (final)", tot),
        ("Unique prospects", len({r['Website'] for r in rows})),
        ("Verified Shopify stores (Yes)", sum(r["Shopify Verified"] == "Yes" for r in rows)),
        ("Likely Shopify stores (indirect evidence)", sum(r["Shopify Verified"] == "Likely" for r in rows)),
        ("Shopify Plus stores (evidenced)", sum(r["Shopify Plus"].startswith("Yes") for r in rows)),
        ("Verified emails", sum(bool(r["Email"]) for r in rows)),
        ("No verified email", sum(not r["Email"] for r in rows)),
        ("Named contacts (sourced)", sum(bool(r["First Name"]) for r in rows)),
        ("High buying intent", sum(r["Buying Intent"] == "High" for r in rows)),
        ("Medium buying intent", sum(r["Buying Intent"] == "Medium" for r in rows)),
        ("Low buying intent", sum(r["Buying Intent"] == "Low" for r in rows)),
        ("High confidence", sum(r["Research Confidence"] == "High" for r in rows)),
        ("Medium confidence", sum(r["Research Confidence"] == "Medium" for r in rows)),
        ("Low confidence", sum(r["Research Confidence"] == "Low" for r in rows)),
        ("Duplicates removed", len(dups)),
        ("Invalid prospects removed", len(invalid)),
    ]
    sec("Key metrics")
    for m in metrics:
        sm.append(list(m))
    for title, key in (("Prospects by country", "Country"), ("Prospects by industry", "Industry")):
        sec(title)
        for k, v in Counter(r[key] or "Unknown" for r in rows).most_common():
            sm.append([k, v])
    sec("Prospects by automation opportunity (a prospect can count in several)")
    oc = Counter()
    for r in rows:
        oc.update(opp_cats(r["Automation Opportunity"]))
    for k, v in oc.most_common():
        sm.append([k, v])
    sec("Prospects by batch")
    for k, v in sorted(Counter(r["_batch"] for r in rows).items()):
        sm.append([k, v])
    if dups:
        sec("Duplicates removed (company, domain, source file)")
        for d in dups:
            sm.append(list(d))
    if invalid:
        sec("Invalid prospects removed (company, domain, reason)")
        for d in invalid:
            sm.append(list(d))
    sm.column_dimensions["A"].width = 55
    sm.column_dimensions["B"].width = 40
    sm.column_dimensions["C"].width = 40
    wb.save(OUT)

    print(f"records={len(recs)} kept={tot} dups={len(dups)} invalid={len(invalid)} emails={sum(bool(r['Email']) for r in rows)}")
    print("intent", Counter(r["Buying Intent"] for r in rows), "conf", Counter(r["Research Confidence"] for r in rows))
    for i in issues:
        print("ISSUE", i)
    for d in dups:
        print("DUP", d)
    for d in invalid:
        print("INVALID", d)

if __name__ == "__main__":
    main()
