"""Usage: python3 outreach/mark.py <status> email1 email2 ...  -> updates queue.json and the XLSX Status column."""
import json, sys, os, datetime, openpyxl
D = os.path.dirname(os.path.abspath(__file__)); Q = os.path.join(D, "queue.json")
status, emails = sys.argv[1], {e.lower() for e in sys.argv[2:]}
now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
q = json.load(open(Q))
for e in q:
    if e["email"] in emails:
        e["status"] = status; e["sent_at"] = now if status == "sent" else e.get("sent_at", "")
json.dump(q, open(Q, "w"), indent=1)
p = os.path.join(D, "..", "EA_Trading_Bot_Prospects_500.xlsx"); wb = openpyxl.load_workbook(p); ws = wb.active
label = {"sent": f"Sent {now} from oseniibrahim845@gmail.com"}.get(status, status.replace("_", " ").capitalize() + f" ({now})")
for r in range(2, ws.max_row + 1):
    if str(ws.cell(r, 4).value).lower() in emails: ws.cell(r, 7).value = label
wb.save(p)
print("marked", len(emails), status, "| pending left:", sum(x["status"] == "pending" for x in q))
