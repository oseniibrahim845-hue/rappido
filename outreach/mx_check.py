"""Mark pending queue entries whose domain has no MX/A record as 'skipped_no_mail_server' (avoids bounces)."""
import json, os, subprocess, sys, dns.resolver
D = os.path.dirname(os.path.abspath(__file__)); q = json.load(open(os.path.join(D, "queue.json")))
bad = []
for e in q:
    if e["status"] != "pending": continue
    dom = e["email"].split("@")[1]
    try:
        dns.resolver.resolve(dom, "MX", lifetime=8)
    except Exception:
        bad.append(e["email"])
print("no MX:", bad)
if bad: subprocess.run([sys.executable, os.path.join(D, "mark.py"), "skipped_no_mail_server", *bad])
