# Test runner. Usage: cd <folder where you ran "npm install n8n">; export N8N_USER_FOLDER=$PWD/home NODE_FUNCTION_ALLOW_BUILTIN=fs N8N_RUNNERS_ENABLED=false; start smtp_sink.py 1025 outbox.jsonl; python3 test_runner.py normal|bad|cap|capfull|dry|mail
import json, subprocess, os, sys, re, collections
sys.path.insert(0,'/home/user/rappido/automation/n8n')
import build_workflows as bw
HERE=os.getcwd(); ST=HERE+'/state.json'; OUT=HERE+'/outbox.jsonl'
env=dict(os.environ)
def install(wfid, **kw):
    w=bw.build(True, state_file=ST, **kw); w['id']=wfid
    w=json.loads(json.dumps(w).replace('"REPLACE"','"smtp1"'))
    json.dump([w],open('wf_%s.json'%wfid,'w'))
    subprocess.run(['node_modules/.bin/n8n','import:workflow','--input=wf_%s.json'%wfid],capture_output=True,env=env,timeout=120)
def run(wfid):
    r=subprocess.run(['node_modules/.bin/n8n','execute','--id='+wfid],capture_output=True,text=True,env=env,timeout=170)
    return r
def data(scn):
    subprocess.run(['python3','/home/user/rappido/automation/n8n/make_test_data.py',ST,scn],check=True)
    open(OUT,'w').close()
def outbox(): return [json.loads(l) for l in open(OUT) if l.strip()]
def counts(): return dict(collections.Counter(x['status'] for x in json.load(open(ST))))
res={}
which=sys.argv[1]
if which=='normal':
    install('t_send',flow='send'); data('normal'); run('t_send'); ob=outbox()
    res['normal sent']=len(ob); res['normal counts']=counts()
    bad=[r for r in ob if re.search(r'n8n|paid|free',r['data'],re.I)]
    import quopri; raw=ob[0]['data'].replace('\r\n','\n'); body=quopri.decodestring(raw.split('\n\n',1)[1].encode()).decode()
    res['no n8n footer / no paid words']=not bad
    res['no brackets or dashes in body']=not re.search(r'[\[\]()—–]',body)
    res['recipients']=[r['to'][0] for r in ob]
elif which=='bad':
    install('t_send',flow='send'); data('bad'); run('t_send'); res['bad rows: recipients']=[r['to'][0] for r in outbox()]; res['bad counts']=counts()
elif which=='cap':
    install('t_send',flow='send'); data('cap'); run('t_send'); res['cap(47 sent in 24h) sent now']=len(outbox())
elif which=='capfull':
    install('t_send',flow='send'); data('capfull'); run('t_send'); res['capfull(50 sent) sent now']=len(outbox())
elif which=='dry':
    install('t_dry',flow='send',dry=True); data('normal'); run('t_dry'); res['dry run sent']=len(outbox()); res['dry counts']=counts()
elif which=='mail':
    install('t_mail',flow='mail'); data('normal')
    # make rows 2,3 'sent' so bounce/reply apply
    rows=json.load(open(ST))
    for r in rows:
        if r['email'] in ('author2@example.test','author3@example.test'): r['status']='sent'
    json.dump(rows,open(ST,'w'))
    run('t_mail'); rows=json.load(open(ST)); res['mail results']={r['email']:r['status'] for r in rows if r['email'] in ('author2@example.test','author3@example.test')}
print(json.dumps(res,indent=1))
