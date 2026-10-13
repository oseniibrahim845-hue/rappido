"""Merge batch JSONL files into the 17-column Author Ledger CSV, dedupe and audit."""
import csv, glob, json, re, sys, unicodedata, collections, os

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["author_name","email","first_name","book_title","country","state","city","subject_line","email_body",
        "personalization_status","automation_action","send_status","date_sent","gmail_thread_id","reply_status",
        "do_not_contact","last_error"]
COUNTRIES = {"United States","United Kingdom","Canada","Australia","New Zealand","Ireland","Germany","France","Spain",
  "Italy","Netherlands","Belgium","Switzerland","Austria","Sweden","Norway","Denmark","Finland","Portugal","Poland",
  "South Africa","Nigeria","Kenya","India","Singapore","United Arab Emirates","Brazil","Mexico","Chile","Argentina"}
BANNED_SUBJ = re.compile(r"^(author spotlight opportunity|interview opportunity|collaboration opportunity|feature opportunity|dear author|book feature|author interview)$", re.I)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)

def words(t):
    t = t or ""
    cjk = len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", t))
    if cjk > 50:  # Chinese/Japanese: approximate words as characters / 2
        return cjk // 2
    return len(re.findall(r"\S+", t))

FOUND = {}
for fp in glob.glob(os.path.join(HERE, "work", "hunt", "found*.jsonl")):
    for line in open(fp, encoding="utf-8"):
        if line.strip():
            try:
                f = json.loads(line)
            except Exception:
                continue
            if f.get("email") and f.get("email_source_url"):
                FOUND[norm(f["author_name"])] = f
rows, issues, seen_name, seen_email, seen_subj = [], collections.Counter(), set(), set(), set()
bad = []
for path in sorted(glob.glob(os.path.join(HERE, "work", "*.jsonl"))):
    for ln, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line: continue
        try: r = json.loads(line)
        except Exception: issues["bad_json"] += 1; continue
        name = (r.get("author_name") or "").strip()
        key = norm(name)
        if not key or key in seen_name: issues["dup_or_noname"] += 1; continue
        email = (r.get("email") or "").strip()
        if not email and key in FOUND:
            email = FOUND[key]["email"].strip(); r["email_source_url"] = FOUND[key]["email_source_url"]
            r["hook_note"] = (r.get("hook_note") or "") + " | email: " + FOUND[key].get("note", "")
        if email and (not EMAIL_RE.match(email) or not r.get("email_source_url")):
            issues["email_dropped_unsourced"] += 1; email = ""
        if email and email.lower() in seen_email: issues["dup_email"] += 1; continue
        if r.get("country") not in COUNTRIES: issues["bad_country"] += 1; bad.append((path, name, r.get("country"))); continue
        subj = (r.get("subject_line") or "").strip()
        body = (r.get("email_body") or "").strip()
        if not subj or BANNED_SUBJ.match(subj) or subj.lower() in seen_subj: issues["bad_subject"] += 1; bad.append((path,name,"subject")); continue
        if not body or "Author Ledger" not in body: issues["bad_body"] += 1; bad.append((path,name,"body")); continue
        wc = words(body)
        if wc < 70 or wc > 150: issues["wordcount_out_of_range"] += 1; bad.append((path,name,f"wc={wc}")); continue
        status = r.get("personalization_status") or "DEEP RESEARCHED"
        if status not in ("DEEP RESEARCHED","INSUFFICIENT RESEARCH"): status = "DEEP RESEARCHED"
        if status == "INSUFFICIENT RESEARCH": action = "SKIP_INSUFFICIENT_RESEARCH"
        elif email: action = "READY_FOR_INITIAL_OUTREACH"
        else: action = "SKIP_NO_EMAIL"
        seen_name.add(key); seen_subj.add(subj.lower())
        if email: seen_email.add(email.lower())
        rows.append({"author_name":name,"email":email,"first_name":(r.get("first_name") or name.split()[0]).strip(),
            "book_title":(r.get("book_title") or "").strip(),"country":r["country"],"state":(r.get("state") or "").strip(),
            "city":(r.get("city") or "").strip(),"subject_line":subj,"email_body":body,"personalization_status":status,
            "automation_action":action,"send_status":"","date_sent":"","gmail_thread_id":"","reply_status":"",
            "do_not_contact":"","last_error":"", "_src": r.get("source_urls") or [], "_hook": r.get("hook_note","")})

limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
if limit and len(rows) > limit:
    # trim proportionally from the largest countries so balance is kept
    by = collections.defaultdict(list)
    for r in rows: by[r["country"]].append(r)
    while sum(len(v) for v in by.values()) > limit:
        c = max(by, key=lambda k: len(by[k])); by[c].pop()
    keep = {id(r) for v in by.values() for r in v}
    rows = [r for r in rows if id(r) in keep]

with open(os.path.join(HERE, "author_ledger_leads.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore", quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)
with open(os.path.join(HERE, "author_ledger_sources.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL); w.writerow(["author_name","country","hook_note","source_urls"])
    for r in rows: w.writerow([r["author_name"], r["country"], r["_hook"], " | ".join(r["_src"])])

print("rows:", len(rows)); print("issues:", dict(issues))
print("with email:", sum(1 for r in rows if r["email"]))
print("by country:", dict(collections.Counter(r["country"] for r in rows).most_common()))
us = collections.Counter(r["state"] for r in rows if r["country"]=="United States")
print("US states covered:", len(us), dict(us))
for b in bad[:40]: print("  rejected:", b)
