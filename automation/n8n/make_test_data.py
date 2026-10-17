#!/usr/bin/env python3
"""Creates test lead state + fake inbox for the n8n test run. Usage: make_test_data.py <state.json> <scenario>"""
import json, sys, datetime as dt
state, scenario = sys.argv[1], sys.argv[2]
now = dt.datetime.now(dt.timezone.utc)
def iso(h): return (now - dt.timedelta(hours=h)).isoformat()
rows = []
def add(i, **kw):
    r = {"email": f"author{i}@example.test", "first_name": f"Name{i}", "book_title": f"Book {i}",
         "personalized_opening": f"I enjoyed the setting of Book {i}. It feels fresh and warm.", "country": "Test",
         "status": "", "sent_at": "", "error": ""}
    r.update(kw); rows.append(r)
if scenario == "normal":
    for i in range(1, 41): add(i)                       # 40 pending
    add(41, status="bounced"); add(42, status="replied")
    add(43, email="not-an-email"); add(44, personalized_opening="")  # invalid + no opening
    add(45, email="author1@example.test")                              # duplicate of row 1
    for i in range(46, 50): add(i, status="sent", sent_at=iso(30))   # sent 30h ago, does not count
if scenario == "cap":
    for i in range(1, 11): add(i)
    for i in range(11, 58): add(i, status="sent", sent_at=iso(2))    # 47 sent in last 24h
if scenario == "capfull":
    for i in range(1, 11): add(i)
    for i in range(11, 61): add(i, status="sent", sent_at=iso(2))    # 50 sent in last 24h
if scenario == "bad":
    add(1, email="not-an-email"); add(2, personalized_opening=""); add(3, status="bounced"); add(4, status="replied")
    add(5, status="failed"); add(6); add(7, email="Author6@Example.test"); add(8); add(9, email="author8@example.test")
json.dump(rows, open(state, "w"), indent=1)
inbox = [
  {"from": "Mail Delivery Subsystem <mailer-daemon@googlemail.com>", "subject": "Delivery Status Notification (Failure)",
   "text": "Your message wasn't delivered to author2@example.test because the address couldn't be found."},
  {"from": "Name3 <author3@example.test>", "subject": "Re: A short feature about Book 3", "text": "Yes please, send the questions."},
  {"from": "Stranger <stranger@elsewhere.test>", "subject": "Hello", "text": "Buy my thing"},
  {"from": "Mail Delivery Subsystem <mailer-daemon@googlemail.com>", "subject": "Delivery Status Notification (Failure)",
   "text": "Your message wasn't delivered to unknown@nowhere.test"},
]
json.dump(inbox, open(state + ".inbox", "w"), indent=1)
