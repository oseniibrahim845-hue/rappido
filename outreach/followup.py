"""One polite follow-up per cold lead, 4+ days after the first email, only if they never replied.
Usage:
  python3 outreach/followup.py list N          -> JSON of up to N due follow-ups (email, subject, body)
  python3 outreach/followup.py done  e1 e2 ... -> record follow-up sent (followup_at)
  python3 outreach/followup.py replied e1 ...  -> lead replied; never follow up
"""
import json, sys, os, datetime
D = os.path.dirname(os.path.abspath(__file__)); Q = os.path.join(D, "queue.json")
DAYS = 4
q = json.load(open(Q))
now = datetime.datetime.utcnow()
cmd = sys.argv[1]

def due(e):
    if e["status"] != "sent" or e.get("followup_at") or not e.get("sent_at"):
        return False
    sent = datetime.datetime.strptime(e["sent_at"][:16], "%Y-%m-%d %H:%M")
    return now - sent >= datetime.timedelta(days=DAYS)

if cmd == "list":
    n = int(sys.argv[2]); out = []
    for e in q:
        if len(out) >= n: break
        if not due(e): continue
        greeting = e["body"].split("\n", 1)[0].strip() or "Hi there,"
        body = (f"{greeting}\n\nJust bumping my note below in case it got buried. Besides MQL4/MQL5 Expert Advisors, "
                "I also handle Pine Script to MT5 conversions, prop-firm risk guards, trade and Telegram signal copiers, "
                "exchange API bots and trading dashboards, plus ongoing maintenance for existing bots.\n\n"
                "If any of that would be useful, I'm happy to start with a small, well-defined task so you can see how I work. "
                "If the timing isn't right, no problem at all.\n\nBest regards,\nOseni Ibrahim\nTrading Bot Developer")
        out.append({"email": e["email"], "subject": "Re: " + e["subject"], "body": body})
    print(json.dumps(out, indent=1))
    print("due total:", sum(due(e) for e in q), file=sys.stderr)
else:
    emails = {x.lower() for x in sys.argv[2:]}
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    for e in q:
        if e["email"] in emails:
            if cmd == "done": e["followup_at"] = stamp
            elif cmd == "replied": e["status"] = "replied"
    json.dump(q, open(Q, "w"), indent=1)
    print(cmd, len(emails))
