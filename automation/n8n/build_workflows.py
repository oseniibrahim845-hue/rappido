#!/usr/bin/env python3
"""Builds the n8n workflows (production and test) from one shared set of code snippets.
Run: python3 build_workflows.py   (writes author_spotlight_sender.json and test_author_spotlight_sender.json)"""
import json, uuid

CONFIG_JS = """const CFG = {
  DAILY_CAP: 50,      // never more than this many sends in any rolling 24 hours
  PER_RUN: 5,         // sends per scheduled run (10 runs a day x 5 = 50)
  DRY_RUN: __DRY__,   // true = build the emails but do not send or mark anything
};
"""

PICK_JS = r"""
const rows = $input.all().map(i => i.json);
const now = Date.now();
const DAY = 24 * 3600 * 1000;
const st = r => String(r.status || '').trim().toLowerCase();

const sentLast24h = rows.filter(r => st(r) === 'sent' && r.sent_at && (now - new Date(r.sent_at).getTime()) < DAY).length;
const remaining = Math.max(0, CFG.DAILY_CAP - sentLast24h);
const limit = Math.min(CFG.PER_RUN, remaining);
if (limit === 0) return [];

const emailOk = e => /^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]{2,}$/.test(String(e || '').trim());
const clean = t => String(t || '')
  .replace(/[—–]/g, ', ')
  .replace(/(?<=[a-z])-(?=[a-z])/g, ' ')
  .replace(/\s*\(([^)]*)\)/g, ', $1')
  .replace(/[\[\]]/g, '')
  .replace(/\s+,/g, ',').replace(/,\s*,/g, ',').replace(/  +/g, ' ').trim();

// anyone who already has a status other than pending is never contacted again
const blocked = new Set(rows.filter(r => st(r) && st(r) !== 'pending').map(r => String(r.email).trim().toLowerCase()));

const SUBJECTS = [
  b => `An Author Spotlight for ${b}`,
  b => `A short feature about ${b}`,
];
const hash = s => [...s].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);

const picked = [];
const used = new Set();
for (const r of rows) {
  if (picked.length >= limit) break;
  const status = st(r);
  if (status && status !== 'pending') continue;
  const email = String(r.email || '').trim().toLowerCase();
  if (!emailOk(email) || blocked.has(email) || used.has(email)) continue;
  const first = clean(r.first_name) || 'there';
  const book = clean(r.book_title);
  const opening = clean(r.personalized_opening);
  if (!book || !opening) continue;               // never send without a real personal opening
  used.add(email);
  const subject = SUBJECTS[hash(email) % SUBJECTS.length](book);
  const body = [
    `Hi ${first},`,
    opening,
    `I run The Author Ledger, where we share author stories with readers. I would love to write a short Spotlight about you and ${book}.`,
    `Here is how it works. I send you a few easy questions. You answer them in your own words. Then I turn your answers into a clean article that you can share with your readers. It should take about 10 minutes of your time.`,
    `We also help authors with audiobooks, book trailers, and short promo videos. That is separate, and only if you want it.`,
    `If you would like to be featured, just reply with the word yes and I will send the questions. If this is not for you, tell me and I will not write again.`,
    `Warm regards,\nOseni Ibrahim\nThe Author Ledger`,
  ].join('\n\n');
  picked.push({ json: { email, first_name: first, book_title: book, subject, body, dry_run: CFG.DRY_RUN } });
}
return picked;
"""

CLASSIFY_JS = r"""
// Input: the list of known lead emails. Mails come from the Mail Feed node as { from, subject, text }. Output: { kind: 'bounce'|'reply'|'ignore', email }
const known = ($input.first().json.emails || []).map(e => e.toLowerCase());
const out = [];
for (const it of $('Mail Feed').all()) {
  const m = it.json;
  const from = String(m.from || '').toLowerCase();
  const text = String(m.text || m.textPlain || '');
  const isBounce = /mailer-daemon|postmaster|mail delivery|delivery status/.test(from + ' ' + String(m.subject || '').toLowerCase());
  if (isBounce) {
    const cand = (text.match(/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/g) || []).map(e => e.toLowerCase());
    const hit = cand.find(e => known.includes(e));
    out.push({ json: { kind: hit ? 'bounce' : 'ignore', email: hit || '' } });
    continue;
  }
  const sender = (from.match(/[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}/) || [''])[0];
  out.push({ json: { kind: known.includes(sender) ? 'reply' : 'ignore', email: sender } });
}
return out.filter(o => o.json.kind !== 'ignore');
"""

def nid(): return str(uuid.uuid4())
def node(name, type_, ver, pos, params, **kw):
    n = {"id": nid(), "name": name, "type": type_, "typeVersion": ver, "position": pos, "parameters": params}
    n.update(kw); return n

SHEET_ID = "1IzG0xy2eDRlW33EEQID-JGdfzsVys5Khl8VJ0oIMMWk"  # replace with the ID of YOUR copy of the sheet
def sheet_ref(): return {"__rl": True, "value": SHEET_ID, "mode": "id"}
def tab_ref(): return {"__rl": True, "value": "gid=0", "mode": "id"}  # first tab of the sheet

def build(test=False, state_file="/tmp/leads_state.json", dry=False, flow="both"):
    dry = "true" if dry else "false"
    cfg = CONFIG_JS.replace("__DRY__", dry)
    nodes, conn = [], {}
    def link(a, b, out=0, inp=0):
        conn.setdefault(a, {"main": []})
        while len(conn[a]["main"]) <= out: conn[a]["main"].append([])
        conn[a]["main"][out].append({"node": b, "type": "main", "index": inp})

    # ---------- Flow 1: send ----------
    if test:
        nodes.append(node("Trigger", "n8n-nodes-base.manualTrigger", 1, [0, 0], {}))
        read = node("Read Leads", "n8n-nodes-base.code", 2, [240, 0], {"jsCode":
            "const fs=require('fs');const rows=JSON.parse(fs.readFileSync('%s','utf8'));return rows.map(r=>({json:r}));" % state_file})
    else:
        nodes.append(node("Every Hour 8 to 5", "n8n-nodes-base.scheduleTrigger", 1.2, [0, 0],
            {"rule": {"interval": [{"field": "cronExpression", "expression": "0 8-17 * * *"}]}}))
        read = node("Read Leads", "n8n-nodes-base.googleSheets", 4.5, [240, 0],
            {"operation": "getAll", "documentId": sheet_ref(), "sheetName": tab_ref(), "returnAll": True},
            credentials={"googleSheetsOAuth2Api": {"id": "REPLACE", "name": "Google Sheets account"}})
    nodes.append(read)
    pick = node("Pick Batch", "n8n-nodes-base.code", 2, [480, 0], {"jsCode": cfg + PICK_JS})
    loop = node("Loop Over Leads", "n8n-nodes-base.splitInBatches", 3, [720, 0], {"batchSize": 1, "options": {}})
    dry_if = node("Dry Run?", "n8n-nodes-base.if", 2, [960, 100], {"conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
        "conditions": [{"id": nid(), "leftValue": "={{ $json.dry_run }}", "rightValue": True,
                        "operator": {"type": "boolean", "operation": "true", "singleValue": True}}], "combinator": "and"}})
    send_params = {"fromEmail": "=Oseni Ibrahim <YOUR_SENDING_ADDRESS@yourdomain.com>", "toEmail": "={{ $json.email }}",
                   "subject": "={{ $json.subject }}", "emailFormat": "text", "text": "={{ $json.body }}", "options": {"appendAttribution": False}}
    if test:
        send_params["fromEmail"] = "Oseni Ibrahim <test@example.com>"
    send = node("Send Email", "n8n-nodes-base.emailSend", 2.1, [1200, 200], send_params,
                credentials={"smtp": {"id": "REPLACE", "name": "SMTP account"}}, onError="continueErrorOutput")
    now_expr = "={{ $now.toISO() }}"
    key = "={{ $('Loop Over Leads').item.json.email }}"
    if test:
        mark_sent = node("Mark Sent", "n8n-nodes-base.code", 2, [1440, 120], {"jsCode":
            "const fs=require('fs');const f='%s';const rows=JSON.parse(fs.readFileSync(f,'utf8'));"
            "const e=$('Loop Over Leads').item.json.email;const r=rows.find(x=>String(x.email).toLowerCase()===e);"
            "r.status='sent';r.sent_at=new Date().toISOString();fs.writeFileSync(f,JSON.stringify(rows,null,1));return [{json:{email:e,status:'sent'}}];" % state_file})
        mark_fail = node("Mark Failed", "n8n-nodes-base.code", 2, [1440, 300], {"jsCode":
            "const fs=require('fs');const f='%s';const rows=JSON.parse(fs.readFileSync(f,'utf8'));"
            "const e=$('Loop Over Leads').item.json.email;const r=rows.find(x=>String(x.email).toLowerCase()===e);"
            "r.status='failed';r.error=String($json.error||'send failed').slice(0,200);fs.writeFileSync(f,JSON.stringify(rows,null,1));return [{json:{email:e,status:'failed'}}];" % state_file})
    else:
        mark_sent = node("Mark Sent", "n8n-nodes-base.googleSheets", 4.5, [1440, 120], {
            "operation": "update", "documentId": sheet_ref(), "sheetName": tab_ref(),
            "columns": {"mappingMode": "defineBelow", "value": {"email": key, "status": "sent", "sent_at": now_expr},
                        "matchingColumns": ["email"], "schema": []}, "options": {}},
            credentials={"googleSheetsOAuth2Api": {"id": "REPLACE", "name": "Google Sheets account"}})
        mark_fail = node("Mark Failed", "n8n-nodes-base.googleSheets", 4.5, [1440, 300], {
            "operation": "update", "documentId": sheet_ref(), "sheetName": tab_ref(),
            "columns": {"mappingMode": "defineBelow", "value": {"email": key, "status": "failed", "error": "={{ String($json.error || 'send failed').slice(0, 200) }}"},
                        "matchingColumns": ["email"], "schema": []}, "options": {}},
            credentials={"googleSheetsOAuth2Api": {"id": "REPLACE", "name": "Google Sheets account"}})
    wait = node("Wait Between Sends", "n8n-nodes-base.wait", 1.1, [1680, 200], {
        "resume": "timeInterval", "amount": 1 if test else "={{ Math.floor(Math.random() * 150) + 90 }}", "unit": "seconds"})
    nodes += [pick, loop, dry_if, send, mark_sent, mark_fail, wait]
    link(nodes[0]["name"], "Read Leads"); link("Read Leads", "Pick Batch"); link("Pick Batch", "Loop Over Leads")
    link("Loop Over Leads", "Dry Run?", out=1)
    link("Dry Run?", "Wait Between Sends", out=0)      # dry run: skip sending
    link("Dry Run?", "Send Email", out=1)
    link("Send Email", "Mark Sent", out=0); link("Send Email", "Mark Failed", out=1)
    link("Mark Sent", "Wait Between Sends"); link("Mark Failed", "Wait Between Sends")
    link("Wait Between Sends", "Loop Over Leads")

    # ---------- Flow 2: bounces and replies ----------
    y = 600
    if test:
        trig2 = node("Test Mail Feed", "n8n-nodes-base.manualTrigger", 1, [0, y], {})
        feed = node("Mail Feed", "n8n-nodes-base.code", 2, [240, y], {"jsCode":
            "const fs=require('fs');return JSON.parse(fs.readFileSync('%s','utf8')).map(m=>({json:m}));" % (state_file + ".inbox")})
        known = node("Known Emails List", "n8n-nodes-base.code", 2, [480, y], {"jsCode":
            "const fs=require('fs');const rows=JSON.parse(fs.readFileSync('%s','utf8'));return [{json:{emails:rows.map(r=>String(r.email).toLowerCase())}}];" % state_file})
    else:
        trig2 = node("New Mail (IMAP)", "n8n-nodes-base.emailReadImap", 2, [0, y],
            {"mailbox": "INBOX", "postProcessAction": "nothing", "format": "simple", "options": {}},
            credentials={"imap": {"id": "REPLACE", "name": "IMAP account"}})
        feed = node("Mail Feed", "n8n-nodes-base.code", 2, [240, y], {"jsCode":
            "return $input.all().map(i=>({json:{from:i.json.from||'',subject:i.json.subject||'',text:i.json.textPlain||i.json.text||''}}));"})
        sheet2 = node("Read Leads For Mail", "n8n-nodes-base.googleSheets", 4.5, [480, y],
            {"operation": "getAll", "documentId": sheet_ref(), "sheetName": tab_ref(), "returnAll": True},
            credentials={"googleSheetsOAuth2Api": {"id": "REPLACE", "name": "Google Sheets account"}})
        nodes.append(sheet2)
        known = node("Known Emails List", "n8n-nodes-base.code", 2, [720, y], {"jsCode":
            "return [{json:{emails:$input.all().map(i=>String(i.json.email||'').toLowerCase()).filter(Boolean)}}];"})
    classify = node("Classify Mail", "n8n-nodes-base.code", 2, [960, y], {"jsCode": CLASSIFY_JS})
    nodes += [trig2, feed, known, classify]
    if test:
        upd2 = node("Mark Bounced or Replied", "n8n-nodes-base.code", 2, [1200, y], {"jsCode":
            "const fs=require('fs');const f='%s';const rows=JSON.parse(fs.readFileSync(f,'utf8'));"
            "for(const i of $input.all()){const r=rows.find(x=>String(x.email).toLowerCase()===i.json.email);"
            "if(r&&(!r.status||r.status==='pending'||r.status==='sent')){r.status=i.json.kind==='bounce'?'bounced':'replied';}}"
            "fs.writeFileSync(f,JSON.stringify(rows,null,1));return $input.all();" % state_file})
    else:
        upd2 = node("Mark Bounced or Replied", "n8n-nodes-base.googleSheets", 4.5, [1200, y], {
            "operation": "update", "documentId": sheet_ref(), "sheetName": tab_ref(),
            "columns": {"mappingMode": "defineBelow", "value": {"email": "={{ $json.email }}",
                        "status": "={{ $json.kind === 'bounce' ? 'bounced' : 'replied' }}"},
                        "matchingColumns": ["email"], "schema": []}, "options": {}},
            credentials={"googleSheetsOAuth2Api": {"id": "REPLACE", "name": "Google Sheets account"}})
    nodes.append(upd2)
    link(trig2["name"], "Mail Feed")
    if test:
        link("Mail Feed", "Known Emails List")
    else:
        link("Mail Feed", "Read Leads For Mail"); link("Read Leads For Mail", "Known Emails List")
    link("Known Emails List", "Classify Mail"); link("Classify Mail", "Mark Bounced or Replied")
    FLOW2 = {"Test Mail Feed", "Mail Feed", "Known Emails List", "Classify Mail", "Mark Bounced or Replied"}
    if flow == "mail":
        nodes = [n for n in nodes if n["name"] in FLOW2]; conn = {k: v for k, v in conn.items() if k in FLOW2}
    if flow == "send":
        nodes = [n for n in nodes if n["name"] not in FLOW2]; conn = {k: v for k, v in conn.items() if k not in FLOW2}
    return {"name": ("TEST " if test else "") + "Author Spotlight Sender 50 per day", "nodes": nodes, "connections": conn,
            "settings": {"executionOrder": "v1", "timezone": "UTC"}, "active": False}

if __name__ == "__main__":
    json.dump(build(False), open("author_spotlight_sender.json", "w"), indent=1)
    json.dump(build(True), open("test_author_spotlight_sender.json", "w"), indent=1)
    print("written")
