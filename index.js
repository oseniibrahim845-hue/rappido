const express = require('express');
const { Pool } = require('pg');
const axios = require('axios');
const app = express();
app.use(express.json());
const pool = new Pool({host:'rappido-production-exoscale-b5b2e600-3aa0-4338-b298-edf80db1c67.i.aivencloud.com',port:21699,user:'avnadmin',password:'AVNS_VCOFB8HL1BIvPMjeujx',database:'defaultdb',ssl:{rejectUnauthorized:false}});
const EVO='https://evolution-api-production-7dd2.up.railway.app';
const KEY='fedb12db6d9c8de55e1c075a97c430ad38ba706fd19b7f62063ee7bb5dc96a90';
const INST='rappido';
async function send(num,txt){try{const n=num.replace('@s.whatsapp.net','').replace(/[^0-9]/g,'');await axios.post(EVO+'/message/sendText/'+INST,{number:n,text:txt},{headers:{apikey:KEY}});console.log('Sent to',n);}catch(e){console.error('Send error:',e.message,e.response&&e.response.data);}}
async function getsess(phone){try{const r=await pool.query('SELECT step,data FROM sessions WHERE phone=$1',[phone]);if(r.rows.length>0){const row=r.rows[0];return{step:row.step||'idle',data:typeof row.data==='string'?JSON.parse(row.data||'{}'):(row.data||{})};}}catch(e){console.error('getsess:',e.message);}return{step:'idle',data:{}};}
async function savesess(phone,step,data){try{await pool.query('INSERT INTO sessions(phone,step,data,updated_at)VALUES($1,$2,$3,NOW())ON CONFLICT(phone)DO UPDATE SET step=$2,data=$3,updated_at=NOW()',[phone,step,JSON.stringify(data)]);}catch(e){console.error('savesess:',e.message);}}
async function saveTS(phone,name,data,sup){const kw=Math.ceil((new Date()-new Date(new Date().getFullYear(),0,1))/604800000);try{await pool.query('INSERT INTO timesheets(phone,employee_name,datum,stunden_total,overtime,einsatzort,spesen_betrag,spesen_kategorie,nachricht_original,status,eintragstyp,konfidenz,sprache,kalenderwoche,vorgesetzter_telefon,created_at)VALUES($1,$2,CURRENT_DATE,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,NOW())',[phone,name,parseFloat(data.stunden_total)||0,parseFloat(data.overtime)||0,data.einsatzort||null,parseFloat(data.spesen_betrag)||0,data.spesen_kategorie||null,'Interaktives Formular','pending','report','high','de',kw,sup||null]);console.log('TS saved');}catch(e){console.error('saveTS:',e.message);}}
async function saveAbs(phone,name,reason){const kw=Math.ceil((new Date()-new Date(new Date().getFullYear(),0,1))/604800000);try{await pool.query('INSERT INTO timesheets(phone,employee_name,datum,stunden_total,nachricht_original,status,eintragstyp,abwesenheitsgrund,sprache,konfidenz,kalenderwoche,created_at)VALUES($1,$2,CURRENT_DATE,0,$3,$4,$5,$6,$7,$8,$9,NOW())',[phone,name,'Abwesenheit: '+reason,'pending','absence',reason,'de','high',kw]);}catch(e){console.error('saveAbs:',e.message);}}
async function saveCorr(phone,date,hours){try{await pool.query("UPDATE timesheets SET stunden_total=$1 WHERE phone=$2 AND datum=$3 AND status!='approved'",[hours,phone,date]);}catch(e){console.error('saveCorr:',e.message);}}
async function getWeek(phone){try{const r=await pool.query("SELECT datum,stunden_total,overtime,einsatzort,spesen_betrag,status FROM timesheets WHERE phone=$1 AND datum>=CURRENT_DATE-INTERVAL '7 days' ORDER BY datum DESC LIMIT 7",[phone]);return r.rows;}catch(e){console.error('getWeek:',e.message);return[];}}
function menuText(n){return'Hallo '+n+'!\n\nWas moechtest du tun?\n\n1 - Zeit erfassen\n2 - Korrektur\n3 - Woche pruefen\n4 - Abwesenheit\n\nBitte Nummer tippen.';}
app.post('/webhook',async function(req,res){
res.sendStatus(200);
try{
const body=req.body;
if(!body||!body.data||!body.data.key)return;
if(body.data.key.fromMe===true)return;
const phone=body.data.key.remoteJidAlt||body.data.key.remoteJid;
const pushName=body.data.pushName||'Mitarbeiter';
const firstName=pushName.split(' ')[0];
const msgObj=body.data.message||{};
const message=(msgObj.conversation||(msgObj.extendedTextMessage&&msgObj.extendedTextMessage.text)||(msgObj.listResponseMessage&&msgObj.listResponseMessage.title)||(msgObj.buttonsResponseMessage&&msgObj.buttonsResponseMessage.selectedDisplayText)||'').trim();
const selectedId=(msgObj.listResponseMessage&&msgObj.listResponseMessage.singleSelectReply&&msgObj.listResponseMessage.singleSelectReply.selectedRowId)||(msgObj.buttonsResponseMessage&&msgObj.buttonsResponseMessage.selectedButtonId)||null;
const sel=(selectedId||message).toLowerCase().trim();
console.log('FROM:',phone,'MSG:',message,'SEL:',sel);
const wr=await pool.query("SELECT * FROM workers WHERE phone=$1 AND status='active'",[phone]);
if(wr.rows.length===0){await send(phone,'Hallo! Du bist nicht bei Rappido registriert. Bitte wende dich an dein Buero.');return;}
const worker=wr.rows[0];
const sup=worker.supervisor_phone||null;
const sess=await getsess(phone);
let step=sess.step,newData=Object.assign({},sess.data),nextStep='idle';
if(step==='idle'){
  if(sel==='zeit_erfassen'||sel==='1'){nextStep='ask_hours';newData={};await send(phone,'Wie viele Stunden hast du heute gearbeitet?\n\nZahl eingeben, z.B. 8.5\nGueltig: 0.5 bis 16');}
  else if(sel==='korrektur'||sel==='2'){nextStep='ask_correction_date';newData={};await send(phone,'Welches Datum moechtest du korrigieren?\nDatum eingeben, z.B. 06.05.2026');}
  else if(sel==='woche_pruefen'||sel==='3'){nextStep='idle';const entries=await getWeek(phone);const totalH=entries.reduce(function(s,e){return s+(parseFloat(e.stunden_total)||0);},0);const days=['So','Mo','Di','Mi','Do','Fr','Sa'];const rows=entries.map(function(e){const d=e.datum?new Date(e.datum):null;const dl=d?days[d.getDay()]+' '+d.toLocaleDateString('de-CH',{day:'2-digit',month:'2-digit'}):'--';const st=e.status==='approved'?'OK':e.status==='rejected'?'X':'...';return st+' '+dl+': '+(e.stunden_total||0)+'h'+(e.einsatzort?' | '+e.einsatzort:'');}).join('\n');await send(phone,'Deine Woche '+firstName+':\n\n'+(rows||'Keine Eintraege')+'\n\nTotal: '+totalH.toFixed(1)+'h');}
  else if(sel==='abwesenheit'||sel==='4'){nextStep='ask_absence';await send(phone,'Abwesenheit melden:\n\n1 - Krank\n2 - Unfall\n3 - Ferien / Militaer\n\nBitte Nummer tippen.');}
  else{nextStep='idle';await send(phone,menuText(firstName));}
}else if(step==='ask_hours'){
  const h=parseFloat(message.replace(',','.'));
  if(isNaN(h)||h<0.5||h>16){nextStep='ask_hours';await send(phone,'Ungueltig. Bitte Zahl zwischen 0.5 und 16. Beispiel: 8.5');}
  else{newData.stunden_total=h;nextStep='ask_overtime';await send(phone,'Davon Ueberstunden? (0 wenn keine)\nZahl eingeben, z.B. 1.5');}
}else if(step==='ask_overtime'){
  const ot=parseFloat(message.replace(',','.'));
  if(isNaN(ot)||ot<0||ot>(newData.stunden_total||16)){nextStep='ask_overtime';await send(phone,'Ungueltig. Erneut eingeben (0 wenn keine):');}
  else{newData.overtime=ot;nextStep='ask_zuschlag';await send(phone,'Zuschlag heute?\n\n1 - Kein Zuschlag\n2 - Nacht (20-05 Uhr)\n3 - Sonntag / Feiertag\n\nBitte Nummer tippen.');}
}else if(step==='ask_zuschlag'){
  const zm={'1':'none','kein_zuschlag':'none','2':'nacht','nacht_zuschlag':'nacht','3':'sonntag','sonntag_zuschlag':'sonntag'};
  newData.zuschlag=zm[sel]||'none';nextStep='ask_location';await send(phone,'Wo hast du heute gearbeitet?\n\nEinsatzort eingeben, z.B. Roche Basel');
}else if(step==='ask_location'){
  newData.einsatzort=message;nextStep='ask_expenses';await send(phone,'Hattest du heute Spesen?\n\n1 - Nein\n2 - Ja\n\nBitte Nummer tippen.');
}else if(step==='ask_expenses'){
  if(sel==='1'||sel==='no_expenses'||sel==='nein'||sel==='no'){newData.spesen_betrag=0;newData.spesen_kategorie=null;nextStep='idle';await saveTS(phone,pushName,newData,sup);await send(phone,'Danke '+firstName+'! Erfasst:\nDatum: '+new Date().toLocaleDateString('de-CH')+'\nStunden: '+newData.stunden_total+'h'+(newData.overtime>0?' (+'+newData.overtime+'h)':'')+'\nOrt: '+(newData.einsatzort||'--')+'\n\nEintrag wartet auf Bestaetigung.');}
  else{nextStep='ask_expense_amount';await send(phone,'Wie viel CHF Spesen?\n\nBetrag eingeben, z.B. 15');}
}else if(step==='ask_expense_amount'){
  const amt=parseFloat(message.replace(/chf/gi,'').replace(/fr\./gi,'').replace(/\.-/g,'').replace(',','.').trim());
  if(isNaN(amt)||amt<0){nextStep='ask_expense_amount';await send(phone,'Ungueltig. Bitte Zahl eingeben, z.B. 15');}
  else{newData.spesen_betrag=amt;nextStep='ask_expense_category';await send(phone,'Welche Art von Spesen?\n\n1 - Reise\n2 - Essen\n3 - Andere\n\nBitte Nummer tippen.');}
}else if(step==='ask_expense_category'){
  const cm={'1':'Reise','reise':'Reise','2':'Essen','essen':'Essen','3':'Andere','andere':'Andere'};
  newData.spesen_kategorie=cm[sel]||'Andere';nextStep='idle';await saveTS(phone,pushName,newData,sup);await send(phone,'Danke '+firstName+'! Erfasst:\nDatum: '+new Date().toLocaleDateString('de-CH')+'\nStunden: '+newData.stunden_total+'h\nOrt: '+(newData.einsatzort||'--')+'\nSpesen: CHF '+newData.spesen_betrag+' ('+newData.spesen_kategorie+')\n\nEintrag wartet auf Bestaetigung.');
}else if(step==='ask_correction_date'){
  newData.correction_date=message;nextStep='ask_correction_hours';await send(phone,'Wie viele Stunden waren es korrekt?\nZahl eingeben, z.B. 7.5');
}else if(step==='ask_correction_hours'){
  const hc=parseFloat(message.replace(',','.'));
  if(isNaN(hc)||hc<0||hc>16){nextStep='ask_correction_hours';await send(phone,'Ungueltige Eingabe. Bitte erneut:');}
  else{newData.new_hours=hc;nextStep='idle';await saveCorr(phone,newData.correction_date,hc);await send(phone,'Korrektur gespeichert!\nDatum: '+newData.correction_date+'\nNeue Stunden: '+hc+'h');}
}else if(step==='ask_absence'){
  const rm={'1':'sick','krank':'sick','2':'accident','unfall':'accident','3':'vacation','ferien':'vacation','militar':'military','militaer':'military'};
  const reason=rm[sel]||'other';nextStep='idle';await saveAbs(phone,pushName,reason);await send(phone,'Abwesenheit erfasst. Gute Besserung '+firstName+'! Das Buero wurde informiert.');
}else{nextStep='idle';await send(phone,menuText(firstName));}
await savesess(phone,nextStep,newData);
}catch(e){console.error('Webhook error:',e.message);}
});

// Dashboard API
app.options('/api', function(req, res) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.sendStatus(200);
});

app.post('/api', async function(req, res) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  try {
    const action = req.body.action;
    const b = req.body;
    let result;
    if (action === 'get_clients') {
      const r = await pool.query('SELECT * FROM clients WHERE email = $1 AND password_hash = $2', [b.email, b.password]);
      result = r.rows;
    } else if (action === 'get_timesheets') {
      const r = await pool.query('SELECT * FROM timesheets ORDER BY created_at DESC LIMIT 500');
      result = r.rows;
    } else if (action === 'get_workers') {
      const r = await pool.query('SELECT * FROM workers ORDER BY created_at DESC');
      result = r.rows;
    } else if (action === 'update_timesheet') {
      await pool.query('UPDATE timesheets SET status = $1 WHERE id = $2', [b.status, b.id]);
      result = { success: true };
    } else if (action === 'save_worker') {
      await pool.query('INSERT INTO workers (first_name, last_name, phone, language, employment_type, einsatzbetrieb, supervisor_phone, personalnummer, start_date, status) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)',
        [b.first_name, b.last_name, b.phone, b.language||'de', b.employment_type||'Vollzeit', b.einsatzbetrieb||null, b.supervisor_phone||null, b.personalnummer||null, b.start_date||null, b.status||'active']);
      result = { success: true };
    } else if (action === 'update_worker') {
      await pool.query('UPDATE workers SET first_name=$1, last_name=$2, phone=$3, language=$4, employment_type=$5, einsatzbetrieb=$6, supervisor_phone=$7, personalnummer=$8, start_date=$9, status=$10 WHERE id=$11',
        [b.first_name, b.last_name, b.phone, b.language||'de', b.employment_type||'Vollzeit', b.einsatzbetrieb||null, b.supervisor_phone||null, b.personalnummer||null, b.start_date||null, b.status||'active', b.id]);
      result = { success: true };
    } else if (action === 'delete_worker') {
      await pool.query('DELETE FROM workers WHERE id = $1', [b.id]);
      result = { success: true };
    } else if (action === 'update_client') {
      await pool.query('UPDATE clients SET agency_name=$1, whatsapp_number=$2, logo_url=$3 WHERE id=$4', [b.agency_name, b.whatsapp_number||null, b.logo_url||null, b.id]);
      result = { success: true };
    } else {
      result = { error: 'Unknown action' };
    }
    res.json(result);
  } catch(e) {
    console.error('API error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

app.get('/health',function(req,res){res.json({status:'ok',time:new Date().toISOString()});});
app.listen(3000,function(){console.log('Rappido bot running on port 3000');});
