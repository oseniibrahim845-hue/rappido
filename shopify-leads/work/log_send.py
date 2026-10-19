import json,sys,datetime
lead,email,msg,thread=sys.argv[1:5]
open('/home/user/rappido/shopify-leads/work/send_log.jsonl','a').write(json.dumps({"lead_id":lead,"email":email,"message_id":msg,"thread_id":thread,"date_sent":datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')})+'\n')
print('logged',lead)
