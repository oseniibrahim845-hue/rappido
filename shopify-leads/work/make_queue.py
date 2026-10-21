"""Build the next outreach queue: python3 make_queue.py <out.json> <count>
Ready, unsent, contactable UK/CA/AU/DE leads, round-robin by country, highest confidence first.
US leads are skipped until a postal address is available (CAN-SPAM)."""
import json, sys, os, openpyxl
out, n = sys.argv[1], int(sys.argv[2])
FOOT_EN = "\n\nIf you'd prefer not to hear from me again, just reply \"no thanks\" and I won't contact you further."
FOOT_DE = "\n\nFalls Sie keine weiteren Nachrichten wünschen, antworten Sie einfach kurz – ich melde mich dann nicht mehr."
here = os.path.dirname(os.path.abspath(__file__))
done = {json.loads(l)["email"].lower() for f in ("send_log.jsonl", "bounces.jsonl") if os.path.exists(os.path.join(here, f))
        for l in open(os.path.join(here, f), encoding="utf-8") if l.strip()}
ws = openpyxl.load_workbook(os.path.join(here, "..", "Shopify_Inventory_Order_Automation_700_Leads.xlsx"), read_only=True)["Shopify_Leads"]
rows = list(ws.values); h = rows[0]
leads = [dict(zip(h, r)) for r in rows[1:]]
pools = {}
for r in leads:
    if (r["automation_action"] == "READY" and r["send_status"] == "NOT_SENT" and r["do_not_contact"] == "FALSE"
            and r["country"] != "United States" and r["email"].lower() not in done):
        pools.setdefault(r["country"], []).append(r)
for p in pools.values():
    p.sort(key=lambda r: -(r["confidence_score"] or 0))
order = [c for c in ("United Kingdom", "Canada", "Australia", "Germany") if c in pools]
q = []
while len(q) < n and any(pools[c] for c in order):
    for c in order:
        if pools[c] and len(q) < n:
            r = pools[c].pop(0)
            foot = FOOT_DE if c == "Germany" and "Viele Grüße" in r["personalized_email_body"] else FOOT_EN
            q.append({"lead_id": r["lead_id"], "store": r["store_name"], "email": r["email"],
                      "subject": r["personalized_subject"], "body": r["personalized_email_body"].rstrip() + foot})
json.dump(q, open(os.path.join(here, out), "w"), ensure_ascii=False, indent=1)
print(len(q), "queued;", {c: len(pools[c]) for c in order}, "left")
