// n8n Code node: "Pick next prospects + write emails"
// Mode: Run Once for All Items. Input: every row from the "Read prospects sheet" node.
// Output: up to BATCH_SIZE items (the next prospects + their emails), best first.
//         The "Loop Over Items" node then sends them one by one.

// ---- Settings ----
const SENDER_NAME = 'YOUR NAME';
const SENDER_SIGNATURE = 'YOUR NAME\nCustom dashboards & internal tools\nyourwebsite.com';
const BATCH_SIZE = 20;              // emails per run (the workflow runs every 4 hours)
const MAX_PER_DAY = 120;            // safety cap; 120 = no extra limit at 20 emails every 4 hours
const SENDABLE_STATUSES = ['', 'pending', 'todo', 'new', 'queued']; // anything else is skipped

// ---- Helpers ----
// Makes column names forgiving: "Email", " email ", "E-mail" and "Contact Name" all work.
const normKey = k => String(k).trim().toLowerCase().replace(/[\s\-]+/g, '_').replace('e_mail', 'email');
const normRow = r => Object.fromEntries(Object.entries(r).map(([k, v]) => [normKey(k), typeof v === 'string' ? v.trim() : v]));
const isEmail = e => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
const statusOf = r => String(r.status || '').toLowerCase();

const rows = $input.all().map(i => normRow(i.json));

// ---- Daily cap ----
const today = $now.toISODate();
const sentToday = rows.filter(r => String(r.sent_at || '').startsWith(today)).length;
const allowed = Math.min(BATCH_SIZE, MAX_PER_DAY - sentToday);
if (allowed <= 0) {
  console.log(`Daily cap reached (${sentToday}/${MAX_PER_DAY}). Nothing sent.`);
  return [];
}

// ---- Emails already contacted (so duplicates in the sheet are never emailed twice) ----
const contacted = new Set(
  rows.filter(r => !SENDABLE_STATUSES.includes(statusOf(r)))
      .map(r => String(r.email || '').toLowerCase())
);

// ---- Next prospects: highest intent score first, then top of the sheet ----
const candidates = rows
  .filter(r => isEmail(String(r.email || '')))
  .filter(r => SENDABLE_STATUSES.includes(statusOf(r)))
  .filter(r => !contacted.has(String(r.email).toLowerCase()))
  .sort((a, b) =>
    (parseFloat(b.intent_score) || 0) - (parseFloat(a.intent_score) || 0) ||
    (Number(a.row_number) || 0) - (Number(b.row_number) || 0));

const seen = new Set();
const batch = [];
for (const r of candidates) {
  const key = String(r.email).toLowerCase();
  if (seen.has(key)) continue;       // same address twice in this batch
  seen.add(key);
  batch.push(r);
  if (batch.length >= allowed) break;
}

if (!batch.length) {
  const withEmail = rows.filter(r => isEmail(String(r.email || ''))).length;
  console.log(`No prospect to send. Rows: ${rows.length}, with a valid email: ${withEmail}, already contacted: ${contacted.size}.`);
  return [];
}

// ---- Write one email per prospect ----
function buildEmail(p) {
  const first = String(p.contact_name || '').split(/\s+/)[0] || 'there';
  const hook = p.evidence_type === 'public_request'
    ? `I saw ${p.company}'s post looking for automation and developer help.`
    : `I noticed ${p.company} is hiring for data, reporting and internal-tools work.`;
  const angle = p.outreach_angle ? ` ${p.outreach_angle}` : '';
  const opportunity = String(p.dashboard_opportunity || '').replace(/\.$/, '');
  const stack = p.recommended_stack ? ` (${p.recommended_stack})` : '';

  const body = `Hi ${first},

${hook}${angle}
${opportunity ? `\nWhat I have in mind for you: ${opportunity}.\n` : ''}
I build custom dashboards and internal tools${stack} and can put together a short mock-up for ${p.company} before we talk. Would a 15-minute call next week be useful?

Best,
${SENDER_SIGNATURE}

P.S. If this isn't relevant, just reply "no thanks" and I won't email you again.`;

  return {
    row_email: p.email,             // used by "Mark as sent" / "Mark as error" to find the row
    row_number: p.row_number,
    company: p.company,
    to: p.email,
    subject: `Idea for ${p.company}'s reporting`,
    body,
    sender_name: SENDER_NAME,
  };
}

console.log(`Sending ${batch.length} emails this run: ${batch.map(r => r.company).join(', ')}. ${candidates.length - batch.length} prospects left after this run.`);

return batch.map(r => ({ json: buildEmail(r) }));
