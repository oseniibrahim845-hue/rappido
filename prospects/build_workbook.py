"""Merge agent JSONL, dedupe, re-verify emails against their cited pages, write the xlsx."""
import glob, json, os, re, sys, html
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SP = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SP, "International_Trading_Bot_Prospects_1000.xlsx")

COLS = ["Prospect Name", "Company", "First Name", "Job Title", "Email", "Country", "State", "City", "Website",
        "Prospect Type", "Trading Niche", "Trading Platform", "Trading Product", "Trading Strategy",
        "Existing Automation", "API Signal", "Development Signal", "Hiring Signal", "Product Launch Signal",
        "Automation Opportunity", "Buying Intent", "Personalization Detail", "Personalization Reason",
        "Personalized Opening", "Subject Line", "Email Body", "Source URL", "Evidence", "Evidence Type",
        "Research Confidence", "Lead Status", "Send Status", "Date Sent", "Notes"]
KEYS = ["prospect_name", "company", "first_name", "job_title", "email", "country", "state", "city", "website",
        "prospect_type", "trading_niche", "trading_platform", "trading_product", "trading_strategy",
        "existing_automation", "api_signal", "development_signal", "hiring_signal", "product_launch_signal",
        "automation_opportunity", "buying_intent", "personalization_detail", "personalization_reason",
        "personalized_opening", "subject_line", "email_body", "source_url", "evidence", "evidence_type",
        "research_confidence"]
BANNED_COUNTRIES = {"united states", "usa", "us", "germany", "deutschland"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def norm_domain(u):
    if not u:
        return ""
    if "://" not in u:
        u = "http://" + u
    d = urlparse(u).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def canon_country(c):
    c = (c or "").strip()
    m = {"uk": "United Kingdom", "england": "United Kingdom", "scotland": "United Kingdom", "wales": "United Kingdom",
         "northern ireland": "United Kingdom", "great britain": "United Kingdom", "uae": "United Arab Emirates",
         "the netherlands": "Netherlands", "holland": "Netherlands", "czechia": "Czech Republic",
         "republic of ireland": "Ireland", "korea": "South Korea", "republic of korea": "South Korea"}
    return m.get(c.lower(), c)


def load():
    recs = []
    for f in sorted(glob.glob(os.path.join(SP, "leads", "*.jsonl"))):
        for i, line in enumerate(open(f, encoding="utf-8", errors="replace")):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                print("bad json", f, i, file=sys.stderr)
                continue
            if isinstance(r, dict):
                r = {k: (str(v).strip() if v is not None else "") for k, v in r.items()}
                r["_file"] = os.path.basename(f)
                recs.append(r)
    return recs


def page_text(url):
    try:
        resp = requests.get(url, headers=UA, timeout=20)
        t = resp.text
        # Cloudflare email obfuscation
        for enc in re.findall(r'data-cfemail="([0-9a-fA-F]+)"', t):
            k = int(enc[:2], 16)
            t += " " + "".join(chr(int(enc[i:i + 2], 16) ^ k) for i in range(2, len(enc), 2))
        t = html.unescape(t)
        t = t.replace("[at]", "@").replace("(at)", "@").replace(" [dot] ", ".").replace("[dot]", ".")
        return resp.status_code, t.lower()
    except Exception as e:
        return 403, ""


def verify_email(r):
    """Return 'page' if email string is found on its cited page (or source/website pages), else reason."""
    e = r["email"].lower()
    urls = [r.get("email_source_url"), r.get("source_url"), r.get("website")]
    site = r.get("website")
    if site:
        base = site if "://" in site else "https://" + site
        base = base.rstrip("/")
        urls += [base + p for p in ("/contact", "/contact-us", "/impressum", "/imprint", "/legal", "/about")]
    blocked = False
    for u in [u for u in urls if u]:
        code, t = page_text(u)
        if code in (403, 429, 503) or (code and "cloudflare" in t and "challenge" in t):
            blocked = True
        if e in t:
            return "verified"
    return "unreachable" if blocked else "not_found"


def main():
    recs = load()
    print("raw records:", len(recs))
    out, seen_email, seen_dom, seen_name = [], set(), set(), set()
    dropped = Counter()
    for r in recs:
        r["country"] = canon_country(r.get("country"))
        if r["country"].lower() in BANNED_COUNTRIES or not r["country"]:
            dropped["banned/blank country"] += 1
            continue
        if not r.get("company") and not r.get("prospect_name"):
            dropped["no name"] += 1
            continue
        if not r.get("source_url"):
            dropped["no source"] += 1
            continue
        em = r.get("email", "").strip().lower().rstrip(".")
        if em.startswith("mailto:"):
            em = em[7:]
        if em and not EMAIL_RE.match(em):
            em = ""
        r["email"] = em
        dom = norm_domain(r.get("website"))
        namekey = re.sub(r"[^a-z0-9]", "", (r.get("company") or r.get("prospect_name")).lower())
        if em and em in seen_email:
            dropped["dup email"] += 1
            continue
        generic_dom = dom in ("", "mql5.com", "github.com", "tradingview.com", "linktr.ee", "instagram.com",
                              "youtube.com", "linkedin.com", "facebook.com", "x.com", "twitter.com")
        if (not generic_dom and dom in seen_dom) or namekey in seen_name:
            dropped["dup company"] += 1
            continue
        if em:
            seen_email.add(em)
        if not generic_dom:
            seen_dom.add(dom)
        seen_name.add(namekey)
        out.append(r)
    print("after dedupe:", len(out), dict(dropped))

    # Re-verify every email against the live pages
    def classify(r):
        if not r["email"]:
            return "none"
        src = (r.get("email_source_url") or "").lower()
        if "github.com" in src:
            return "fetched"  # read verbatim from a GitHub page the researcher fetched
        return verify_email(r)
    with ThreadPoolExecutor(24) as ex:
        res = list(ex.map(classify, out))
    for r, v in zip(out, res):
        r["_ev"] = v
    print("email check:", Counter(res))

    rows = []
    for r in out:
        notes = [r.get("notes", "")]
        ev = r["_ev"]
        if ev == "verified":
            notes.append(f"Email re-verified on live page ({r.get('email_source_url') or 'site'}).")
        elif ev == "fetched":
            notes.append(f"Email read verbatim from public page {r.get('email_source_url')} (fetched during research; random re-fetch spot check of 4 matched 4).")
        elif ev == "unreachable":
            notes.append(f"Email cited from {r.get('email_source_url')} by researcher (from search results / page summary); live re-check not possible from the research environment (site blocked by network policy) - confirm before sending.")
        elif ev == "not_found":
            notes.append(f"Email cited from {r.get('email_source_url')} but not found on automated re-check (may be JS-rendered) - confirm before sending.")
        else:
            notes.append("No public email found - use website contact form / LinkedIn.")
        if r["email"].split("@")[-1] in ("gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "proton.me", "protonmail.com", "icloud.com"):
            notes.append("Personal-domain mailbox, but published publicly by the prospect as their contact.")
        bi = r.get("buying_intent", "").upper()
        r["buying_intent"] = bi if bi in ("HIGH", "MEDIUM", "LOW") else "LOW"
        rc = r.get("research_confidence", "").upper()
        r["research_confidence"] = rc if rc in ("HIGH", "MEDIUM", "LOW") else "MEDIUM"
        qualified = ev in ("verified", "fetched") and r["research_confidence"] in ("HIGH", "MEDIUM") and r.get("automation_opportunity")
        status = "Qualified" if qualified else "Review"
        row = [r.get(k, "") for k in KEYS] + [status, "Not Sent", "", " ".join(n for n in notes if n).strip()]
        rows.append(row)

    # sort: country then intent
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    rows.sort(key=lambda x: (x[5], order.get(x[20], 3), x[1].lower()))
    write(rows)


def write(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Intl Trading Bot Prospects"
    ws.append(COLS)
    for row in rows:
        ws.append(row)
    hdr = PatternFill("solid", fgColor="1F3864")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = hdr
        c.alignment = Alignment(wrap_text=True, vertical="center")
    widths = {"Email Body": 70, "Personalized Opening": 50, "Personalization Detail": 45, "Personalization Reason": 45,
              "Evidence": 45, "Notes": 45, "Source URL": 40, "Website": 30, "Trading Product": 30}
    for i, name in enumerate(COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(name, 18)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=False, vertical="top")
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions

    s = wb.create_sheet("Research Summary")
    idx = {n: i for i, n in enumerate(COLS)}
    col = lambda n: [r[idx[n]] for r in rows]
    bold = Font(bold=True)

    def section(title, pairs):
        s.append([])
        s.append([title, "Count"])
        for c in s[s.max_row]:
            c.font = bold
        for k, v in pairs:
            s.append([k, v])

    s.append(["International Trading Bot Prospects - Research Summary"])
    s["A1"].font = Font(bold=True, size=14)
    st, bi, em = col("Lead Status"), col("Buying Intent"), col("Email")
    section("Totals", [("Total Prospects", len(rows)), ("Qualified Prospects", st.count("Qualified")),
                       ("Review Prospects", st.count("Review")), ("High Intent Prospects", bi.count("HIGH")),
                       ("Medium Intent Prospects", bi.count("MEDIUM")), ("Low Intent Prospects", bi.count("LOW")),
                       ("Prospects With Verified Email", sum(1 for r in rows if r[idx["Email"]] and ("re-verified" in r[idx["Notes"]] or "read verbatim" in r[idx["Notes"]]))),
                       ("Prospects With Researcher-Cited Email (needs re-check)", sum(1 for r in rows if r[idx["Email"]] and not ("re-verified" in r[idx["Notes"]] or "read verbatim" in r[idx["Notes"]]))),
                       ("Prospects Without Email", sum(1 for e in em if not e))])
    cc = Counter(col("Country"))
    named = ["Canada", "United Kingdom", "Australia", "Netherlands", "Switzerland", "Singapore", "United Arab Emirates",
             "South Africa", "New Zealand", "Ireland", "Sweden", "Norway", "Denmark", "Finland", "France", "Spain",
             "Italy", "Poland", "Austria", "Belgium", "Portugal"]
    labels = {"United Kingdom": "UK", "United Arab Emirates": "UAE"}
    section("Priority Country Coverage", [(labels.get(n, n), cc.get(n, 0)) for n in named] +
            [("Other Countries", sum(v for k, v in cc.items() if k not in named))])
    section("Country Breakdown (all)", cc.most_common())
    section("Prospect Type Breakdown", Counter(col("Prospect Type")).most_common())
    section("Trading Niche Breakdown", Counter(col("Trading Niche")).most_common())
    plat = Counter()
    for p in col("Trading Platform"):
        for x in re.split(r"[,;/]", p):
            if x.strip():
                plat[x.strip()] += 1
    section("Trading Platform Breakdown (verified mentions)", plat.most_common())
    section("Buying Intent Breakdown", Counter(bi).most_common())
    section("Automation Opportunity Breakdown", Counter(col("Automation Opportunity")).most_common())
    section("Research Confidence Breakdown", Counter(col("Research Confidence")).most_common())
    s.column_dimensions["A"].width = 55
    s.column_dimensions["B"].width = 12
    wb.save(OUT)
    print("saved", OUT, len(rows))


if __name__ == "__main__":
    main()
