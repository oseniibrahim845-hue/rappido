"""Author Spotlight outreach queue (mirrors outreach/ queue tooling).
  python3 authors/aq.py build            -> add Ready rows from authors/spotlight/bank_*.json (+rows_*.json) not yet queued
  python3 authors/aq.py next N           -> JSON of up to N pending entries (email, subject, body)
  python3 authors/aq.py mark STATUS e1.. -> sent | bounced | error | skipped_already_contacted | replied
  python3 authors/aq.py fu N             -> JSON of up to N due follow-ups (one per lead, 5+ days, in-thread)
  python3 authors/aq.py fudone e1 ..     -> record follow-up sent
  python3 authors/aq.py stats
"""
import json, sys, os, glob, re, datetime
D = os.path.dirname(os.path.abspath(__file__)); Q = os.path.join(D, "queue.json")
SEEN = os.path.join(D, "intl", "SEEN_EMAILS.txt")
FU_DAYS = 5
FOLLOWUPS_ENABLED = False  # user 2026-10-03: "we don't need follow up"
DAILY_CAP = 100  # user rule 2026-10-03: at most 100 outreach emails in any rolling 24 hours (first emails + follow-ups)

def sent_last_24h():
    def recent(ts):
        return ts and now - datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M") <= datetime.timedelta(hours=24)
    return sum(1 for e in q if recent(e.get("sent_at"))) + sum(1 for e in q if recent(e.get("followup_at")))
EXCLUDE_COUNTRIES = ("nigeria",)  # user decision 2026-10-02: no Nigerian leads
BANNED = re.compile(r"\b(AI|artificial intelligence|inteligencia artificial|synthetic|sint[eé]tic|automated|automatizad|"
                    r"voice clon|clonaci[oó]n de voz|text-to-speech|texto a voz|guarantee|garantiz)", re.I)
now = datetime.datetime.utcnow()
q = json.load(open(Q)) if os.path.exists(Q) else []
idx = {e["email"].lower(): e for e in q}

def save():
    json.dump(q, open(Q, "w"), indent=1, ensure_ascii=False)

PAID_EN = "The Author Spotlight is a paid feature, and I would be happy to share the details and pricing if it sounds like a good fit."
PAID_ES = "El Author Spotlight es una publicación paga, y con gusto te comparto los detalles y el precio si te interesa."
PAID_ES_PL = "El Author Spotlight es una publicación paga, y con gusto les comparto los detalles y el precio si les interesa."

def disclose(b):
    """Make sure every first email says the Spotlight is paid (user decision 2026-10-02, price $200)."""
    if re.search(r"paid feature|publicaci[oó]n paga|servicio pago", b, re.I): return b
    ps = b.split("\n\n")
    es = ps[0].lower().startswith("hola")
    line = (PAID_ES_PL if "equipo" in ps[0].lower() else PAID_ES) if es else PAID_EN
    q = next((i for i, p in enumerate(ps) if p.strip().startswith(("Would you", "¿"))), len(ps) - 2)
    ps.insert(q, line)
    return "\n\n".join(ps)

def ok(r):
    b = r["email_body"]; wc = len(re.findall(r"\w+", b))
    b = re.sub(r"(\S)best\?", r"\1 best?", b); r["email_body"] = b  # fix missing space before "best?"
    return (r.get("personalization_status") == "Ready" and 160 <= wc <= 275 and "—" not in b and "–" not in b
            and not BANNED.search(b) and "Oseni Ibrahim" in b and "@" in r["email"])

cmd = sys.argv[1]
if cmd == "build":
    added = rej = 0
    seen = set(l.strip().lower() for l in open(SEEN)) if os.path.exists(SEEN) else set()
    # never re-contact anyone emailed in earlier campaigns (Sep 30 / Oct 1 author rounds, EA/crypto queue)
    contacted = set()
    for f in glob.glob(os.path.join(D, "round*_search.json")):
        d = json.load(open(f)); d = d if isinstance(d, list) else list(d.values())[0]
        contacted |= {x.get("email", "").lower() for x in d if x.get("email")}
    oq = os.path.join(D, "..", "outreach", "queue.json")
    if os.path.exists(oq):
        contacted |= {e["email"].lower() for e in json.load(open(oq)) if e.get("status") != "pending"}
    for f in sorted(glob.glob(os.path.join(D, "spotlight", "bank_*.json"))):
        for r in json.load(open(f)):
            em = r["email"].strip().lower()
            if em in idx: continue
            if em in contacted: rej += 1; continue
            if any(c in (r.get("country") or "").lower() for c in EXCLUDE_COUNTRIES): rej += 1; continue
            r["email_body"] = disclose(r["email_body"])
            if not ok(r): rej += 1; continue
            e = {"email": em, "author_name": r["author_name"], "country": r.get("country", ""), "subject": r["subject_line"],
                 "body": r["email_body"], "best_offer": r.get("best_offer", ""), "lang": "es" if "Hola" in r["email_body"][:20] else "en",
                 "source": os.path.basename(f), "status": "pending"}
            q.append(e); idx[em] = e; added += 1
            if em not in seen:
                open(SEEN, "a").write(em + "\n"); seen.add(em)
    save(); print(f"added {added}, rejected {rej}, total {len(q)}")
elif cmd == "next":
    n = max(0, min(int(sys.argv[2]), DAILY_CAP - sent_last_24h())); out = [{"email": e["email"], "subject": e["subject"], "body": e["body"]} for e in q if e["status"] == "pending"][:n]
    print(json.dumps(out, indent=1, ensure_ascii=False))
elif cmd == "mark":
    st = sys.argv[2]; stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    for em in sys.argv[3:]:
        e = idx.get(em.lower())
        if not e: print("unknown", em); continue
        e["status"] = st
        if st == "sent": e["sent_at"] = stamp
    save(); print("marked", st, len(sys.argv) - 3)
elif cmd in ("fu", "fudone"):
    def due(e):
        if e["status"] != "sent" or e.get("followup_at") or not e.get("sent_at"): return False
        return now - datetime.datetime.strptime(e["sent_at"][:16], "%Y-%m-%d %H:%M") >= datetime.timedelta(days=FU_DAYS)
    if cmd == "fu" and FOLLOWUPS_ENABLED is False:
        print("[]"); sys.exit(0)
    if cmd == "fu":
        out = []
        sys.argv[2] = str(max(0, min(int(sys.argv[2]), DAILY_CAP - sent_last_24h())))
        for e in q:
            if len(out) >= int(sys.argv[2]): break
            if not due(e): continue
            g = e["body"].split("\n", 1)[0].strip()
            if e["lang"] == "es":
                body = (f"{g}\n\nSolo quería volver a dejar mi mensaje anterior por si se perdió entre otros correos. "
                        "Para ser claro desde el principio: el Author Spotlight es una publicación paga, y los demás servicios son totalmente opcionales.\n\n"
                        "Si te interesa, con una respuesta breve basta y te cuento los detalles y el precio. Si no es buen momento, no hay problema.\n\n"
                        "Un saludo,\nOseni Ibrahim\nThe Author Ledger")
            else:
                body = (f"{g}\n\nI just wanted to bring my earlier note back to the top of your inbox in case it got buried. "
                        "To be upfront, the Author Spotlight is a paid feature, and the other services are completely optional.\n\n"
                        "If you are interested, a short reply is all it takes and I will share the details and pricing. If the timing is not right, no problem at all.\n\n"
                        "Warm regards,\nOseni Ibrahim\nThe Author Ledger")
            out.append({"email": e["email"], "subject": "Re: " + e["subject"], "body": body})
        print(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        for em in sys.argv[2:]:
            if em.lower() in idx: idx[em.lower()]["followup_at"] = now.strftime("%Y-%m-%d %H:%M UTC")
        save(); print("fudone", len(sys.argv) - 2)
elif cmd == "stats":
    from collections import Counter
    print(dict(Counter(e["status"] for e in q)), "followups sent:", sum(1 for e in q if e.get("followup_at")),
          "| sent in last 24h:", sent_last_24h(), "of cap", DAILY_CAP)
