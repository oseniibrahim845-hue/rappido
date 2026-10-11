"""Merge lead JSONL batches into the 17-column Author Ledger CSV with QA checks."""
import csv, glob, json, os, re, sys, unicodedata
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
COLS = ["author_name", "email", "first_name", "book_title", "country", "state", "city",
        "subject_line", "email_body", "personalization_status", "automation_action",
        "send_status", "date_sent", "gmail_thread_id", "reply_status", "do_not_contact", "last_error"]
COUNTRIES = {"United States", "United Kingdom", "Canada", "Australia", "New Zealand", "Ireland",
             "Germany", "France", "Spain", "Italy", "Netherlands", "Belgium", "Switzerland", "Austria",
             "Sweden", "Norway", "Denmark", "Finland", "Portugal", "Poland", "South Africa", "Nigeria",
             "Kenya", "India", "Singapore", "United Arab Emirates", "Brazil", "Mexico", "Chile", "Argentina"}
BANNED_SUBJ = ["author spotlight opportunity", "interview opportunity", "collaboration opportunity",
               "feature opportunity", "dear author", "book feature", "author interview"]
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
GENERIC_LOCAL = {"info", "contact", "hello", "office", "sales", "support", "customerservice", "admin",
                 "enquiries", "inquiries", "orders", "mail", "post", "kontakt", "verlag", "editorial",
                 "press", "publicity", "rights", "service", "team", "general"}


def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def body_words(body):
    lines = [l for l in body.strip().split("\n") if l.strip()]
    # drop greeting (first line) and sign-off (last two lines)
    core = lines[1:-2] if len(lines) > 3 else lines
    return len(" ".join(core).split())


def main():
    rows, issues, seen_name, seen_email, seen_subj = [], [], {}, {}, {}
    for path in sorted(glob.glob(os.path.join(BASE, "..", "raw", "*.jsonl"))):
        batch = os.path.basename(path)
        for i, line in enumerate(open(path, encoding="utf-8")):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                issues.append((batch, i, "bad json")); continue
            r = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
            tag = f"{batch}:{i} {r.get('author_name')}"
            n = norm(r.get("author_name", ""))
            if not n:
                issues.append((tag, "no name")); continue
            if n in seen_name:
                issues.append((tag, f"DUP name of {seen_name[n]}")); continue
            email = (r.get("email") or "").strip().lower()
            if email:
                if not EMAIL_RE.match(email):
                    issues.append((tag, f"invalid email {email} -> blanked")); email = ""
                elif email.split("@")[0] in GENERIC_LOCAL and not r.get("email_source"):
                    issues.append((tag, f"generic email w/o source {email} -> blanked")); email = ""
                elif not r.get("email_source"):
                    issues.append((tag, "email without email_source -> blanked")); email = ""
            if email and email in seen_email:
                issues.append((tag, f"DUP email of {seen_email[email]}")); continue
            if r.get("country") not in COUNTRIES:
                issues.append((tag, f"bad country {r.get('country')}")); continue
            subj = r.get("subject_line", "")
            if any(b in subj.lower() for b in BANNED_SUBJ) or not subj:
                issues.append((tag, f"banned/empty subject: {subj}"))
            if subj.lower() in seen_subj:
                issues.append((tag, f"DUP subject of {seen_subj[subj.lower()]}"))
            wc = body_words(r.get("email_body", ""))
            if wc < 70 or wc > 145:
                issues.append((tag, f"word count {wc}"))
            if "Author Ledger" not in r.get("email_body", ""):
                issues.append((tag, "body missing project name"))
            status = r.get("personalization_status")
            if status not in ("DEEP RESEARCHED", "INSUFFICIENT RESEARCH"):
                status = "INSUFFICIENT RESEARCH"
            if status != "DEEP RESEARCHED":
                action = "SKIP_INSUFFICIENT_RESEARCH"
            elif not email:
                action = "SKIP_NO_EMAIL"
            else:
                action = "READY_FOR_INITIAL_OUTREACH"
            # No source page could be opened this run (egress blocked): nothing may go out automatically.
            status, action = "INSUFFICIENT RESEARCH", "SKIP_INSUFFICIENT_RESEARCH"
            err = "UNVERIFIED: facts" + (" and email" if email else "") + " come from web-search snippets only; open " + \
                  (r.get("email_source") or "the sources") + " to confirm before sending"
            out = {c: "" for c in COLS}
            out["last_error"] = err
            out.update(author_name=r["author_name"], email=email, first_name=r.get("first_name", ""),
                       book_title=r.get("book_title", ""), country=r["country"], state=r.get("state", "") or "",
                       city=r.get("city", "") or "", subject_line=subj, email_body=r.get("email_body", ""),
                       personalization_status=status, automation_action=action)
            seen_name[n] = tag; seen_subj[subj.lower()] = tag
            if email:
                seen_email[email] = tag
            rows.append((out, r))
    final = os.path.join(BASE, "author_ledger_leads.csv")
    with open(final, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for out, _ in rows:
            w.writerow(out)
    with open(os.path.join(BASE, "author_ledger_sources.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["author_name", "country", "language", "email_source", "sources"])
        for out, r in rows:
            w.writerow([out["author_name"], out["country"], r.get("language", ""), r.get("email_source", ""),
                        " | ".join(r.get("sources") or [])])
    print("rows", len(rows))
    print("actions", Counter(o["automation_action"] for o, _ in rows))
    print("countries", sorted(Counter(o["country"] for o, _ in rows).items(), key=lambda x: -x[1]))
    us = Counter(o["state"] for o, _ in rows if o["country"] == "United States")
    print("US states", len(us), sorted(us.items()))
    print("issues", len(issues))
    for x in issues:
        print("  ", x)


if __name__ == "__main__":
    main()
