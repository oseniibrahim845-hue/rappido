# usage: python3 enrich.py <<'X'  company ;; email ;; source ;; [person ;; title]
import sys, json
out = open('enrich.jsonl','a'); n=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    f=[x.strip() for x in line.split(';;')]+['','','','','']
    json.dump(dict(company=f[0],email=f[1],email_source=f[2],contact_full_name=f[3],job_title=f[4]),out); out.write('\n'); n+=1
print('enriched',n)
