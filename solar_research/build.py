import json, glob, re, sys
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = sys.argv[1] if len(sys.argv) > 1 else "Solar_Automation_Prospects_500.xlsx"
ORDER = ["us_west","us_south","us_ne_mw","us_national","canada","uk","australia","germany","netherlands","ireland","nz","extra*"]
COLS = ["Prospect Name","Company","First Name","Job Title","Email","Country","State","City","Website",
"Solar Business Type","Solar Services","Customer Type","Company Size","Service Area","Locations",
"Quote Request Available","Consultation Available","Appointment Booking Available","Online Lead Form","CRM",
"Customer Support System","Marketing Channels","Sales Team Signal","Lead Volume Signal","Follow Up Signal",
"Automation Signal","Automation Opportunity","Buying Intent","Personalization Detail","Personalization Reason",
"Personalized Opening","Subject Line","Email Body","Source URL","Evidence","Evidence Type","Research Confidence",
"Lead Status","Send Status","Date Sent","Notes"]

FREEMAIL = {"gmail.com","hotmail.com","yahoo.com","outlook.com","aol.com","icloud.com","live.com","hotmail.co.uk","bigpond.com","yahoo.co.uk","btinternet.com","xtra.co.nz","eircom.net","gmx.de","web.de"}

def dom(u):
    u = (u or "").strip().lower()
    if not u: return ""
    if "://" not in u: u = "http://" + u
    d = urlparse(u).netloc.split("@")[-1].split(":")[0]
    return d[4:] if d.startswith("www.") else d

def norm_name(n):
    n = re.sub(r"[^a-z0-9 ]", " ", (n or "").lower())
    stop = {"ltd","limited","llc","inc","pty","gmbh","bv","b","v","co","company","corp","corporation","the","group","and","uk","ireland","nz","australia","canada","kg","ug","ag"}
    return " ".join(w for w in n.split() if w not in stop)

def s(r,k,default=""):
    v = r.get(k, default)
    if v is None: v = default
    return str(v).strip()

def lower_first(t):
    t = t.strip().rstrip(".")
    if not t: return t
    # keep proper nouns/acronyms: only lowercase if second char is lowercase
    if len(t) > 1 and t[0].isupper() and t[1].islower() and not t.split()[0] in ("I",):
        first = t.split()[0]
        if first in ("Your","You","Homeowners","Businesses","Customers","The","Visitors","Clients","Farmers","Every","Each","Both","A","An","Several","Multiple"):
            return t[0].lower() + t[1:]
    return t

# opportunity -> (problem/idea sentence, benefit sentence, subject templates)
OPP = {
 "Lead qualification chatbot": ("a simple AI assistant could answer first questions on the site, check things like roof type, bill size and location, and pass only qualified enquiries to your team with the details already filled in.",
     "Your team would spend less time on enquiries that were never a fit.", ["Qualifying solar enquiries at {c}","A lead qualification idea for {c}"]),
 "Quote request automation": ("each quote request could be checked automatically, sorted by system size and location, logged in your CRM or a sheet, and answered with a first reply within minutes.",
     "It cuts the manual copy and paste between the form, inbox and pipeline.", ["A solar quote workflow idea","Quote requests at {c}"]),
 "Appointment booking automation": ("people who ask for a consultation could get a booking link straight away, with reminders by email or SMS and the booking added to the right calendar.",
     "Fewer calls back and forth to agree a time, and fewer no-shows.", ["Consultation booking at {c}","Solar appointment follow up"]),
 "Site survey scheduling": ("once a lead is qualified, a workflow could offer survey slots, confirm the address and roof details, send reminders and notify the surveyor.",
     "It keeps surveys moving without someone chasing each one by phone.", ["Site survey scheduling idea","Survey bookings at {c}"]),
 "Lead routing": ("new enquiries could be sorted automatically by location or project type and sent to the right office or salesperson with a notification.",
     "Leads reach the right person faster and none sit in a shared inbox.", ["Routing solar enquiries at {c}","A lead routing idea for {c}"]),
 "CRM automation": ("form enquiries, calls and emails could be logged in your CRM automatically, with each lead moved to the next stage and tasks created for the sales team.",
     "Less manual data entry and a clearer view of where every lead stands.", ["CRM updates at {c}","A quick automation idea for {c}"]),
 "CRM data entry": ("details from web forms, emails and survey notes could be pulled into your CRM automatically instead of being typed in by hand.",
     "It saves admin time and keeps customer records complete.", ["Less CRM admin at {c}","A data entry idea for {c}"]),
 "Quote follow up": ("after a quote goes out, a short sequence could check in by email or SMS, answer common questions and alert the salesperson when someone replies or opens it again.",
     "Fewer quotes go quiet just because nobody had time to follow up.", ["Quote follow ups at {c}","A solar quote follow up idea"]),
 "Missed lead recovery": ("enquiries that never booked, or calls that were missed, could get an automatic follow up by SMS or email, with the lead flagged for a callback.",
     "It helps you pick up leads that would otherwise go cold.", ["Missed solar leads at {c}","Solar lead follow up idea"]),
 "SMS follow up": ("new enquiries could get a quick SMS reply, a way to pick a call time, and a few friendly follow ups if they go quiet.",
     "Leads hear back fast even when the team is on site.", ["SMS follow up for {c}","Solar lead follow up idea"]),
 "Email follow up": ("a short email sequence could follow up on each enquiry, share relevant info on panels, batteries or financing, and hand warm replies to your team.",
     "It keeps leads engaged without extra manual emails.", ["Email follow up at {c}","Solar lead follow up idea"]),
 "WhatsApp automation": ("enquiries could be answered on WhatsApp automatically, with basic questions handled and a consultation offered before a person takes over.",
     "Customers get quick answers on the channel they already use.", ["WhatsApp enquiries at {c}","A WhatsApp idea for {c}"]),
 "Sales notifications": ("new leads and key events like a signed quote or a finance approval could trigger instant alerts to the right person by email, SMS or Slack.",
     "The team reacts faster without watching several inboxes.", ["Sales alerts at {c}","A quick automation idea for {c}"]),
 "Customer support automation": ("common customer questions about system performance, monitoring, warranties or service visits could be answered automatically, with anything complex passed to your team.",
     "Support staff spend time on the issues that need them.", ["Customer support at {c}","A support workflow idea for {c}"]),
 "Lead scoring": ("each enquiry could be scored on things like property type, bill size, location and timeline, so the sales team calls the strongest leads first.",
     "Sales time goes to the leads most likely to go ahead.", ["Lead scoring for {c}","Prioritising solar leads at {c}"]),
 "Sales reporting": ("a workflow could pull numbers from your CRM and quote tools into a simple weekly report on leads, quotes, conversions and response times.",
     "You get a clear picture without building reports by hand.", ["Sales reporting at {c}","A reporting idea for {c}"]),
 "Customer onboarding": ("once a customer signs, a workflow could collect documents, send next steps for permits, grid or DNO applications and install dates, and keep them updated.",
     "Fewer status calls and a smoother handover from sales to install.", ["Customer onboarding at {c}","An onboarding idea for {c}"]),
 "Post installation follow up": ("after each install, an automatic follow up could check the customer is happy, share monitoring tips, and ask for a review or referral.",
     "More reviews and referrals without adding admin work.", ["Post install follow up at {c}","An idea for {c} customers"]),
 "Review request automation": ("after each install, customers could get a timed review request by email or SMS, with a reminder if they don't respond.",
     "It builds steady reviews without anyone needing to remember to ask.", ["Review requests at {c}","An idea for {c} reviews"]),
 "Document processing": ("documents like utility bills, finance applications and site survey forms could be read automatically and the key details sent into your system.",
     "It removes a lot of manual checking and retyping.", ["Solar paperwork at {c}","A document workflow idea for {c}"]),
 "Internal AI assistant": ("an internal AI assistant could answer staff questions about products, pricing rules and processes, and draft quotes or replies from your own documents.",
     "The team finds answers faster without interrupting each other.", ["An internal AI idea for {c}","A quick automation idea for {c}"]),
}
DEFAULT_OPP = "Quote request automation"
def canon_opp(o):
    o = (o or "").strip()
    for k in OPP:
        if k.lower() == o.lower(): return k
    for k in OPP:
        if k.lower() in o.lower() or o.lower() in k.lower(): return k
    return DEFAULT_OPP

def yn(v):
    v = (v or "").strip()
    if v.lower().startswith("yes"): return "Yes"
    if v.lower().startswith("no"): return "No"
    return "Unknown"

def level(v, d="Medium"):
    v = (v or "").strip().capitalize()
    return v if v in ("High","Medium","Low") else d

rows_in = []
for pat in ORDER:
    for f in sorted(glob.glob(f"{pat}.json")):
        try:
            data = json.load(open(f))
        except Exception as e:
            print("BAD JSON", f, e); continue
        for r in data:
            r["_src"] = f
            rows_in.append(r)
print("raw records:", len(rows_in))

RANK = {"confirmed":0, "unconfirmed":1}
rows_in.sort(key=lambda r: (RANK.get(s(r,"email_status").lower(), 2) if s(r,"email") else 2))
seen_dom, seen_name, seen_email = {}, {}, {}
out, dups = [], []
for r in rows_in:
    d = dom(s(r,"website"))
    n = norm_name(s(r,"company"))
    e = s(r,"email").lower()
    key_hits = (d and d in seen_dom) or (n and (n, s(r,"country")) in seen_name) or (e and "@" in e and e.split("@")[1] not in FREEMAIL and e in seen_email)
    if key_hits or not d:
        dups.append((s(r,"company"), d, r["_src"])); continue
    seen_dom[d] = 1; seen_name[(n, s(r,"country"))] = 1
    if e: seen_email[e] = 1
    out.append(r)
order = {id(r):i for i,r in enumerate(sorted(out, key=lambda r: (ORDER.index(r['_src'].split('/')[-1][:-5]) if r['_src'].split('/')[-1][:-5] in ORDER else 99)))}
out.sort(key=lambda r: order[id(r)])
print("unique:", len(out), "dropped (duplicate or no website):", len(dups))
for x in dups: print("  dropped", x)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
def compose(r, opp, idx):
    c = s(r,"company")
    fn = s(r,"first_name")
    detail = s(r,"personalization_detail").rstrip(".")
    obs = lower_first(detail)
    greet = f"Hi {fn}," if fn else f"Hi {c} team,"
    openers = ["I noticed {o}.", "I was looking at your website and saw that {o}.", "I came across {c} and noticed {o}."]
    k = idx % 3
    if k == 1 and obs.lower().startswith(("your site","your website")): k = 0
    op = openers[k].format(o=obs, c=c)
    idea, benefit, subjects = OPP[opp]
    subj = subjects[idx % len(subjects)].format(c=c)
    if len(subj) > 60: subj = subjects[1-(idx % 2)].format(c=c) if len(subjects)>1 else "A quick automation idea"
    if len(subj) > 60: subj = "A solar lead follow up idea"
    body = (f"{greet}\n\n{op}\n\n"
            f"I work with businesses on AI and workflow automation. For a solar company like {c}, {idea}\n\n"
            f"{benefit}\n\n"
            f"Would it be useful if I showed you how this could work with your current setup?\n\n"
            f"Best,\n[Sender Name]\nAI Automation Specialist")
    if len(body.split()) > 120:
        body = body.replace(f"For a solar company like {c}, ", "For a solar business like yours, ")
    if len(body.split()) > 120:
        body = body.replace(f"{benefit}\n\n", "")
    return op, subj, body

wb = Workbook()
ws = wb.active; ws.title = "Solar Automation Prospects"
ws.append(COLS)
hdr_fill = PatternFill("solid", start_color="1F4E78")
for i,_ in enumerate(COLS,1):
    cell = ws.cell(row=1,column=i); cell.font = Font(name="Arial", bold=True, color="FFFFFF"); cell.fill = hdr_fill
    cell.alignment = Alignment(wrap_text=True, vertical="center")

stats_words = []
for i, r in enumerate(out):
    opp = canon_opp(s(r,"automation_opportunity"))
    email = s(r,"email")
    est = s(r,"email_status").lower()
    if email and not EMAIL_RE.match(email): email, est = "", "none"
    conf = level(s(r,"research_confidence"))
    intent = level(s(r,"buying_intent"))
    notes = [f"Batch {i//100+1}"]
    if s(r,"notes"): notes.append(s(r,"notes"))
    edom = email.split("@")[1].lower() if "@" in email else ""
    wdom = dom(s(r,"website"))
    if not email or est == "none":
        status = "Reject"; notes.append("No publicly verified business email found.")
    elif edom in FREEMAIL:
        status = "Review"; notes.append("Email is on a free webmail domain; confirm it is the business's published address.")
    elif est != "confirmed":
        status = "Review"; notes.append("Email seen in search results but not independently corroborated; verify on website before sending.")
    elif conf == "Low" or not s(r,"personalization_detail") or not s(r,"source_url"):
        status = "Review"
    else:
        status = "Ready"
    if edom and wdom and edom != wdom and not edom.endswith(wdom) and not wdom.endswith(edom) and status == "Ready":
        status = "Review"; notes.append(f"Email domain ({edom}) differs from website domain ({wdom}).")
    if s(r,"email_source_url") and s(r,"email_source_url") != s(r,"source_url"):
        notes.append("Email source: " + s(r,"email_source_url"))
    if s(r,"personalization_detail"):
        op, subj, body = compose(r, opp, i)
        wc = len(body.split())
        if wc > 120: print("LONG", wc, s(r,"company"))
    else:
        op = subj = body = ""
    reason = f"Supports the {opp.lower()} idea: " + (s(r,"automation_signal") or s(r,"evidence"))
    full = s(r,"full_name") or (s(r,"first_name"))
    row = [full, s(r,"company"), s(r,"first_name"), s(r,"job_title"), email, s(r,"country"), s(r,"state"), s(r,"city"),
           s(r,"website"), s(r,"business_type"), s(r,"services"), s(r,"customer_type"), s(r,"company_size","Unknown") or "Unknown",
           s(r,"service_area"), s(r,"locations","Unknown") or "Unknown",
           yn(s(r,"quote_request")), yn(s(r,"consultation")), yn(s(r,"appointment_booking")), yn(s(r,"online_lead_form")),
           s(r,"crm","Unknown") or "Unknown", s(r,"support_system","Unknown") or "Unknown", s(r,"marketing_channels"),
           s(r,"sales_signal"), s(r,"lead_volume_signal"), s(r,"follow_up_signal"), s(r,"automation_signal"),
           opp, intent, s(r,"personalization_detail"), reason, op, subj, body, s(r,"source_url"), s(r,"evidence"),
           s(r,"evidence_type"), conf, status, "Not Sent", None, " | ".join(notes)]
    ws.append(row)

N = ws.max_row
for row in ws.iter_rows(min_row=2, max_row=N):
    for c in row:
        c.font = Font(name="Arial", size=10); c.alignment = Alignment(wrap_text=False, vertical="top")
widths = {"Company":28,"Email":30,"Website":30,"Evidence":60,"Email Body":70,"Personalization Detail":50,"Personalized Opening":50,"Notes":50,"Source URL":40}
for i,h in enumerate(COLS,1):
    ws.column_dimensions[get_column_letter(i)].width = widths.get(h, 18)
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{N}"

# Summary sheet with formulas
S = wb.create_sheet("Research Summary")
P = "'Solar Automation Prospects'"
def col(h): return get_column_letter(COLS.index(h)+1)
def rng(h): return f"{P}!${col(h)}$2:${col(h)}${N}"
bold = Font(name="Arial", bold=True); norm = Font(name="Arial")
r0 = [("Metric","Count")]
metrics = [
 ("Total Prospects", f"=COUNTA({rng('Company')})"),
 ("Ready Prospects", f'=COUNTIF({rng("Lead Status")},"Ready")'),
 ("Review Prospects", f'=COUNTIF({rng("Lead Status")},"Review")'),
 ("Rejected Prospects", f'=COUNTIF({rng("Lead Status")},"Reject")'),
 ("High Buying Intent", f'=COUNTIF({rng("Buying Intent")},"High")'),
 ("Medium Buying Intent", f'=COUNTIF({rng("Buying Intent")},"Medium")'),
 ("Low Buying Intent", f'=COUNTIF({rng("Buying Intent")},"Low")'),
 ("High Research Confidence", f'=COUNTIF({rng("Research Confidence")},"High")'),
 ("Medium Research Confidence", f'=COUNTIF({rng("Research Confidence")},"Medium")'),
 ("Low Research Confidence", f'=COUNTIF({rng("Research Confidence")},"Low")'),
 ("Quote Request Companies", f'=COUNTIF({rng("Quote Request Available")},"Yes")'),
 ("Appointment Booking Companies", f'=COUNTIF({rng("Appointment Booking Available")},"Yes")'),
 ("Online Lead Form Companies", f'=COUNTIF({rng("Online Lead Form")},"Yes")'),
 ("Companies With Multiple Locations", None),
 ("Companies With Strong Sales Signals", None),
 ("Companies With Strong Follow Up Signals", None),
 ("Companies With Strong Automation Signals", None),
]
S.append(["Metric","Count","How counted"]); 
for c in S[1]: c.font = Font(name="Arial", bold=True, color="FFFFFF"); c.fill = hdr_fill
# helper counts computed in python for text-signal metrics (documented)
def strong(v): 
    v=(v or "").strip().lower(); return bool(v) and not v.startswith("none") and v != "unknown"
data_rows = list(ws.iter_rows(min_row=2, values_only=True))
ix = {h:i for i,h in enumerate(COLS)}
def multi(loc):
    loc=(loc or "").lower()
    m = re.match(r"\s*(\d+)", loc)
    return (m and int(m.group(1))>1) or any(w in loc for w in ("offices","locations","branches","showrooms","depots"))
pycounts = {
 "Companies With Multiple Locations": (sum(1 for r in data_rows if multi(r[ix["Locations"]])), "Locations field shows 2+ offices/branches (counted at build time)"),
 "Companies With Strong Sales Signals": (sum(1 for r in data_rows if strong(r[ix["Sales Team Signal"]])), "Sales Team Signal has evidence (not 'None found')"),
 "Companies With Strong Follow Up Signals": (sum(1 for r in data_rows if strong(r[ix["Follow Up Signal"]])), "Follow Up Signal has evidence (not 'None found')"),
 "Companies With Strong Automation Signals": (sum(1 for r in data_rows if r[ix["Buying Intent"]]=="High" and strong(r[ix["Automation Signal"]])), "High buying intent and a documented automation signal"),
}
for name, f in metrics:
    if f: S.append([name, f, "Live formula over prospects sheet"])
    else: S.append([name, pycounts[name][0], pycounts[name][1]])
S.append([])
def section(title, header, items):
    S.append([title]); S.cell(row=S.max_row, column=1).font = bold
    for it in items: S.append(it)
    S.append([])
countries = sorted({r[ix["Country"]] for r in data_rows})
section("Countries", None, [[c, f'=COUNTIF({rng("Country")},"{c}")'] for c in countries])
from collections import Counter
bt = Counter(r[ix["Solar Business Type"]] for r in data_rows)
section("Solar Business Types", None, [[k, f'=COUNTIF({rng("Solar Business Type")},"{k.replace(chr(34),"")}")'] for k,_ in bt.most_common()])
oc = Counter(r[ix["Automation Opportunity"]] for r in data_rows)
section("Top Automation Opportunities", None, [[k, f'=COUNTIF({rng("Automation Opportunity")},"{k}")'] for k,_ in oc.most_common()])
top = [k for k,_ in oc.most_common(5)]
summary = (f"Across {len(data_rows)} verified solar prospects, the most common automation opportunities were "
  + ", ".join(f"{k.lower()} ({oc[k]})" for k in top) + ". "
  "Most installers publish a quote or free-consultation form and then rely on phone calls and email to qualify, book a site survey and chase the quote. "
  "That points first to instant qualification of form enquiries, automated booking of consultations or surveys, and structured follow up on quotes that go quiet. "
  "Multi-location and commercial firms show extra need for lead routing and CRM updates, while companies with large installed bases show post-install follow up and support automation needs. "
  f"Final verified count: {sum(1 for r in data_rows if r[ix['Lead Status']]=='Ready')} Ready prospects with a corroborated business email, plus {sum(1 for r in data_rows if r[ix['Lead Status']]=='Review')} Review prospects, out of {len(data_rows)} unique companies researched. The 500 target was not reached because the research session's web search allowance (200 searches) ran out; no records were invented to fill the gap. "
  "All research was done through public web search results because direct website access was blocked in the research environment; rows marked Review need their email checked on the company website before sending.")
S.append(["Summary"]); S.cell(row=S.max_row, column=1).font = bold
S.append([summary]); S.merge_cells(start_row=S.max_row, start_column=1, end_row=S.max_row, end_column=3)
S.cell(row=S.max_row, column=1).alignment = Alignment(wrap_text=True, vertical="top"); S.row_dimensions[S.max_row].height = 150
for row in S.iter_rows():
    for c in row:
        if c.font != bold and not (c.row == 1): c.font = norm
S.column_dimensions["A"].width = 45; S.column_dimensions["B"].width = 12; S.column_dimensions["C"].width = 60
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("saved", OUT, "rows", N-1, Counter(r[ix["Lead Status"]] for r in data_rows), Counter(r[ix["Country"]] for r in data_rows))
