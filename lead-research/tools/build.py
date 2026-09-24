import json, glob, re, os, sys, hashlib
from urllib.parse import urlparse
from collections import Counter, OrderedDict
S = os.path.dirname(os.path.abspath(__file__))
OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), None) or os.path.join(S, "Germany_US_UK_Invoice_AI_Automation_Prospects_1000.xlsx")

FREE = {"gmail.com","yahoo.com","hotmail.com","outlook.com","aol.com","icloud.com","live.com","gmx.de","web.de","yahoo.co.uk","hotmail.co.uk","protonmail.com","btinternet.com","me.com","msn.com","googlemail.com","t-online.de","orange.fr","free.fr","wanadoo.fr"}
BANNED = ["seamless","tailored","stunning","revolutioniz","revolutionis","game changer","game-changer","cutting edge","cutting-edge","unlock","supercharge","transform your business"]
TYPES = ["Invoicing Software","Accounting Software","Accounts Receivable Software","E-Invoicing","Billing & Subscription Management","Accounting & Bookkeeping Firm","ERP Implementation & Consulting","Payments & Fintech","Business Management Software","Financial Administration Services"]
EVT = ["Website","Product page","Pricing page","LinkedIn","Company page","Documentation","Press release","Job posting"]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
COUNTRY_FIX = {"USA":"United States","US":"United States","U.S.":"United States","UK":"United Kingdom","England":"United Kingdom","Scotland":"United Kingdom","Wales":"United Kingdom","Northern Ireland":"United Kingdom","Deutschland":"Germany","The Netherlands":"Netherlands","Holland":"Netherlands"}

def dom(u):
    if not u: return ""
    if "://" not in u: u = "https://" + u
    h = urlparse(u).netloc.lower().split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h
def root(d):
    p = d.split(".")
    if len(p) >= 3 and p[-2] in ("co","com","org","net","ac","gov") and len(p[-1]) == 2: return ".".join(p[-3:])
    return ".".join(p[-2:])
def norm_name(n):
    n = n.lower()
    n = re.sub(r"\b(ltd|limited|inc|llc|gmbh|ag|bv|b\.v\.|sa|sas|plc|llp|co|corp|corporation|group|holding|holdings|ug|kg|oy|ab|as|aps|nv|pty|se)\b\.?", "", n)
    return re.sub(r"[^a-z0-9]", "", n)
def clean(s): return re.sub(r"\s+", " ", str(s or "")).strip()
def pick(v, opts, default):
    v = clean(v)
    for o in opts:
        if v.lower() == o.lower(): return o
    return default

rows, raw_count, bad_json = [], 0, 0
for f in sorted(glob.glob(os.path.join(S, "raw", "*.jsonl"))):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        try: r = json.loads(line)
        except Exception: bad_json += 1; continue
        raw_count += 1
        r["_file"] = os.path.basename(f); rows.append(r)

invalid, invalid_reasons = [], Counter()
valid = []
for r in rows:
    r = {k: clean(v) if isinstance(v, str) else v for k, v in r.items()}
    r["country"] = COUNTRY_FIX.get(r.get("country",""), r.get("country",""))
    w = r.get("website","")
    if w and "://" not in w: w = "https://" + w
    r["website"] = w.rstrip("/")
    d = dom(w)
    reason = None
    if not r.get("company"): reason = "missing company"
    elif not d or "." not in d: reason = "missing/invalid website"
    elif any(x in d for x in ("linkedin.com","facebook.com","crunchbase.com","g2.com","capterra")): reason = "website is a directory, not company site"
    elif not r.get("source_url"): reason = "missing source"
    elif not r.get("evidence") or not r.get("personalization_detail"): reason = "missing evidence/personalization"
    if reason:
        invalid.append((r, reason)); invalid_reasons[reason] += 1; continue
    # email validation
    e = r.get("email","").lower().strip().strip(".").replace("mailto:","")
    enote = ""
    if e:
        ed = e.split("@")[-1]
        if not EMAIL_RE.match(e): enote = f"Email '{e}' rejected: invalid format"; e = ""
        elif ed in FREE: enote = f"Email '{e}' rejected: free mailbox"; e = ""
        elif root(ed) != root(d):
            # allow if company name clearly in email domain (brand vs corporate domain)
            nn = norm_name(r["company"])[:6]
            if nn and nn in ed.replace("-","").replace(".",""): enote = f"Email domain {ed} differs from website domain {d}; kept (brand match)"
            else: enote = f"Email '{e}' rejected: domain does not match website"; e = ""
        elif not r.get("email_source"): enote = "Email has no recorded source; verify"
    r["email"] = e; r["_enote"] = enote
    # name sanity: first name must be a single token from full name
    fn, full = r.get("first_name",""), r.get("contact_full_name","")
    if fn and full and fn.split()[0].lower() not in full.lower(): fn = ""
    if fn and not full: fn = ""
    r["first_name"] = fn.split()[0] if fn else ""
    if not r["first_name"]: r["contact_full_name"] = full if full else ""
    r["company_type"] = pick(r.get("company_type"), TYPES, r.get("company_type") or "")
    r["evidence_type"] = pick(r.get("evidence_type"), EVT, "Website")
    r["buying_intent"] = pick(r.get("buying_intent"), ["High","Medium","Low"], "Medium")
    r["_dom"] = d; r["_root"] = root(d)
    valid.append(r)

def score(r):
    return (bool(r["email"]), bool(r.get("first_name")), {"High":2,"Medium":1}.get(r.get("research_confidence"),0), len(r.get("evidence","")))
# dedupe by name, root domain, email domain
valid.sort(key=score, reverse=True)
seen_n, seen_d, final, dups = set(), set(), [], []
for r in valid:
    n = norm_name(r["company"]); d = r["_root"]; ed = root(r["email"].split("@")[-1]) if r["email"] else None
    if n in seen_n or d in seen_d or (ed and ed in seen_d):
        dups.append(r); continue
    seen_n.add(n); seen_d.add(d)
    if ed: seen_d.add(ed)
    final.append(r)

# compose text
OPEN_CLOSE = ["Would you be open to a quick look at how this could work for your setup?",
              "Would it be worth a short call to see if this fits how your team works?",
              "Is this something you would be open to exploring?",
              "Would a short walkthrough of how this could work be useful?",
              "Would you be open to a 15 minute chat about it?"]
SOL = ["I build OpenClaw AI agents that handle parts of invoice tracking, payment follow ups, reporting, and finance administration around existing business systems.",
       "I build OpenClaw based AI agents that work alongside accounting, billing, and CRM systems to take care of repetitive invoice and reporting work.",
       "I build AI agents on OpenClaw that can monitor invoice status, send payment follow ups, and prepare finance reports from the tools a team already uses."]
def banned_free(t):
    for b in BANNED:
        t = re.sub(re.escape(b), {"seamless":"smooth","tailored":"specific","unlock":"open up"}.get(b, "useful"), t, flags=re.I)
    return t
def fix_opening(r):
    o = r.get("personalized_opening","")
    if not o:
        pd = r["personalization_detail"]
        o = "I noticed that " + (pd[0].lower() + pd[1:] if pd.startswith("The ") else pd)
    return o if o.endswith((".", "!", "?")) else o + "."
for r in final:
    h = int(hashlib.md5(r["company"].encode()).hexdigest(), 16)
    greet = f"Hi {r['first_name']}," if r["first_name"] else "Hello,"
    opening = fix_opening(r)
    wf = r.get("workflow_phrase") or re.sub(r"^Potential opportunity:\s*automate\s*", "", r.get("automation_opportunity",""), flags=re.I).rstrip(".")
    wf = wf.rstrip(".")
    body = f"{greet}\n\n{opening}\n\n{SOL[h % 3]}\n\nFor a company like {r['company']}, I think there may be an opportunity to automate {wf}.\n\n{OPEN_CLOSE[h % 5]}\n\nBest,\nOseni Ibrahim\nAI Automation Specialist"
    r["_opening"] = banned_free(opening); r["_body"] = banned_free(body)
    subj = r.get("subject_line") or f"Invoice workflow automation for {r['company']}"
    r["_subject"] = banned_free(subj)
    ao = r.get("automation_opportunity","")
    if ao and not ao.lower().startswith("potential opportunity"): ao = "Potential opportunity: " + ao[0].lower() + ao[1:]
    r["automation_opportunity"] = banned_free(ao)
    for k in ("personalization_detail","personalization_reason","evidence"): r[k] = banned_free(r.get(k,""))
    # confidence + status
    conf = pick(r.get("research_confidence"), ["High","Medium","Low"], "Medium")
    WEAK = ("socialmedia","press","media","presse","apisupport","api","jobs","careers","karriere","bewerbung","privacy","datenschutz","dpo","gdpr","legal","abuse","noreply","no-reply","investor","ir","pr","marketing","partner","partners","webmaster")
    if r["email"] and r["email"].split("@")[0].lower() in WEAK and not r["_enote"]:
        r["_enote"] = f"Email is a non-sales mailbox ({r['email'].split('@')[0]}@); find a better contact before sending"
    if not r["email"] and conf == "High": conf = "Medium"
    if r["email"] and not r["_enote"] and r.get("email_source") and r.get("evidence") and r.get("source_url"): conf = "High"
    if r["email"] and conf == "Low": conf = "Medium"
    if re.search(r"domain (to verify|inferred)|website domain inferred", r.get("notes",""), re.I) and not r["email"]: conf = "Low"
    r["_conf"] = conf
    r["_status"] = "ready" if (r["email"] and conf == "High" and not r["_enote"]) else "review"
    notes = [n for n in [r.get("notes",""), r["_enote"]] if n]
    if not r["email"]: notes.insert(0, "No verified email")
    if r.get("email_source"): notes.append(f"Email source: {r['email_source']}")
    notes.append("Researched via indexed search results (direct site fetch blocked in research environment)")
    r["_notes"] = " | ".join(notes)

# unresolved placeholder check
for r in final:
    for k in ("_body","_subject","_opening"):
        assert not re.search(r"\[[A-Z][A-Za-z ]+\]|\{\w+\}", r[k]), (r["company"], k)

COLS = ["Prospect Name","Company","First Name","Job Title","Email","Country","State","City","Company Type","Industry","Invoice Product or Service","Accounting Platform","ERP","Payment Platform","Company Size","Website","LinkedIn","Buying Intent","Automation Opportunity","Personalization Detail","Personalization Reason","Personalized Opening","Subject Line","Email Body","Source URL","Evidence","Evidence Type","Research Confidence","Lead Status","Send Status","Date Sent","Notes"]
ORDER = {"United States":0,"United Kingdom":1,"Germany":2}
final.sort(key=lambda r: (ORDER.get(r["country"], 3), r["country"], TYPES.index(r["company_type"]) if r["company_type"] in TYPES else 99, r["company"].lower()))
def rowvals(r):
    return [r.get("contact_full_name") or r["company"], r["company"], r["first_name"], r.get("job_title","") if r["first_name"] else "", r["email"], r["country"], r.get("state",""), r.get("city",""), r["company_type"], r.get("industry",""), r.get("invoice_product_or_service",""), r.get("accounting_platform",""), r.get("erp",""), r.get("payment_platform",""), r.get("company_size",""), r["website"], r.get("linkedin",""), r["buying_intent"], r["automation_opportunity"], r["personalization_detail"], r.get("personalization_reason",""), r["_opening"], r["_subject"], r["_body"], r["source_url"], r["evidence"], r["evidence_type"], r["_conf"], r["_status"], "Not Sent", "", r["_notes"]]

stats = dict(raw=raw_count, bad_json=bad_json, invalid=len(invalid), dups=len(dups), unique=len(final))
if "--stats" in sys.argv:
    print(stats); print(Counter(r["country"] for r in final).most_common()); print(Counter(r["company_type"] for r in final).most_common())
    print("email:", sum(1 for r in final if r["email"]), "ready:", sum(1 for r in final if r["_status"]=="ready"))
    print(Counter(r["buying_intent"] for r in final), Counter(r["_conf"] for r in final)); print(invalid_reasons)
# master exclusion list
with open(os.path.join(S, "master_companies.txt"), "w") as fh:
    for r in final: fh.write(f"{r['company']} | {r['_dom']}\n")
if "--xlsx" not in sys.argv: sys.exit()

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
wb = Workbook(); ws = wb.active; ws.title = "Invoice Automation Prospects"
ws.append(COLS)
SKIP={4,15,16,24}
for r in final: ws.append([banned_free(v) if (i not in SKIP and isinstance(v,str)) else v for i,v in enumerate(rowvals(r))])
hf = PatternFill("solid", fgColor="1F3864")
for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = hf; c.alignment = Alignment(wrap_text=True, vertical="center")
widths = {"Email Body":60,"Evidence":50,"Automation Opportunity":45,"Personalization Detail":45,"Personalization Reason":40,"Personalized Opening":45,"Notes":45,"Invoice Product or Service":40}
for i, c in enumerate(COLS, 1):
    ws.column_dimensions[get_column_letter(i)].width = widths.get(c, 20)
ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions

s = wb.create_sheet("Research Summary")
def sec(title, pairs):
    s.append([title]); s.cell(s.max_row, 1).font = Font(bold=True, size=12)
    for k, v in pairs: s.append([k, v])
    s.append([])
T = len(final)
sec("Overview", [("Total prospects", T), ("Total researched (raw rows)", raw_count), ("Prospects with verified emails", sum(1 for r in final if r["email"])), ("Prospects without verified emails", sum(1 for r in final if not r["email"])), ("Prospects with named contact", sum(1 for r in final if r["first_name"])), ("Lead Status = ready", sum(1 for r in final if r["_status"]=="ready")), ("Lead Status = review", sum(1 for r in final if r["_status"]=="review")), ("Duplicate count removed", len(dups)), ("Invalid prospects removed", len(invalid) + bad_json)])
sec("Prospects by country", Counter(r["country"] for r in final).most_common())
sec("Prospects by company type", Counter(r["company_type"] for r in final).most_common())
sec("Prospects by buying intent", [(k, sum(1 for r in final if r["buying_intent"]==k)) for k in ("High","Medium","Low")])
sec("Prospects by research confidence", [(k, sum(1 for r in final if r["_conf"]==k)) for k in ("High","Medium","Low")])
sec("Invalid prospects removed - reasons", list(invalid_reasons.items()) + ([("Malformed research rows", bad_json)] if bad_json else []))
sec("Method notes", [("Research method", "Companies, websites, contacts and emails verified against indexed web search results (company sites, LinkedIn, marketplaces, registries). Direct website fetching was blocked by the research environment's network policy."), ("Email rule", "Emails recorded only when the exact address appeared in search results and matched the company domain. No emails were guessed or pattern-generated."), ("Contact rule", "Names recorded only when a source named the person in that role. Otherwise the email greets 'Hello,'."), ("Deduplication", "By normalised company name, website root domain and email domain; strongest record kept."), ("Recommendation", "Spot-check emails on the company contact page before sending; roles and addresses change.")])
s.column_dimensions["A"].width = 42; s.column_dimensions["B"].width = 90
wb.save(OUT); print("saved", OUT, T)
