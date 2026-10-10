"""Merge lead-bank files into outreach/queue.json (pending sends). Skips anything already queued/sent."""
import json, sys, os, re
Q = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.json")
queue = json.load(open(Q)) if os.path.exists(Q) else []
seen = {q["email"].lower() for q in queue}
BANNED = ["seamless","tailored","stunning","revolutionary","game changing","game-changing","cutting edge",
          "cutting-edge","optimized solution","unlock","transform your business","leverage","synergy"]
added = 0
for f in sys.argv[1:]:
    for r in json.load(open(f)):
        e = (r.get("email") or "").strip().lower()
        if not e or e in seen or not r.get("email_source"):
            continue
        b, s = r.get("body", ""), r.get("subject", "")
        wc = len(b.split())
        if not s or wc < 90 or wc > 175 or "Oseni Ibrahim" not in b or any(re.search(r"\b"+w, (b+s).lower()) for w in BANNED):
            print("SKIP copy issue:", r.get("company"), wc); continue
        seen.add(e); added += 1
        queue.append({"company": r.get("company"), "email": e, "subject": s, "body": b,
                      "status": "pending", "sent_at": "", "lead": r})
json.dump(queue, open(Q, "w"), indent=1)
print("added", added, "total", len(queue), "pending", sum(q["status"] == "pending" for q in queue))
