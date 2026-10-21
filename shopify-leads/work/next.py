import json
q=json.load(open('send_queue_day4.json'))
sent={json.loads(l)['email'] for l in open('send_log.jsonl') if l.strip()}
for d in q:
    if d['email'] not in sent:
        print(d['lead_id'],d['email'],'|',d['subject']); print(d['body']); break
else: print('QUEUE DONE')
