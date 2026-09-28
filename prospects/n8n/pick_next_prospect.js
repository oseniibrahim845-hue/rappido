// n8n Code node: "Pick next prospect + write email"
// Mode: Run Once for All Items. Input: every row from the "Read prospects sheet" node.
// Output: exactly one item (the next prospect + their email), or nothing if no one is left.

// ---- Settings ----
const SENDER_NAME = 'YOUR NAME';
const SENDER_SIGNATURE = 'YOUR NAME\nCustom dashboards & internal tools\nyourwebsite.com';
const MAX_PER_DAY = 120;            // safety cap; 120 = no extra limit at 20 emails every 4 hours
const SENDABLE_STATUSES = ['', 'pending', 'todo', 'new', 'queued']; // anything else is skipped

// ---- Helpers ----
// Makes column names forgiving: "Email", " email ", "E-mail" and "Contact Name" all work.
const normKey = k => String(k).trim().toLowerCase().replace(/[\s\-]+/g, '_').replace('e_mail', 'email');
const normRow = r => Object.fromEntries(Object.entries(r).map(([k, v]) => [normKey(k), typeof v === 'string' ? v.trim() : v]));
const isEmail = e => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);

const rows = $input.all().map(i => normRow(i.json));

// ---- Daily cap ----
const today = $now.toISODate();
const sentToday = rows.filter(r => String(r.sent_at || '').startsWith(today)).length;
if (sentToday >= MAX_PER_DAY) {
  console.log(`Daily cap reached (${sentToday}/${MAX_PER_DAY}). Nothing sent.`);
  return [];
}

// ---- Emails already contacted (so duplicates in the sheet are never emailed twice) ----
const contacted = new Set(
  rows.filter(r => !SENDABLE_STATUSES.includes(String(r.status || '').toLowerCase()))
      .map(r => String(r.email || '').toLowerCase())
);

// ---- Find the next prospect: highest intent score first, then top of the sheet ----
const candidates = rows
  .filter(r => isEmail(String(r.email || '')))
  .filter(r => SENDABLE_STATUSES.includes(String(r.status || '').toLowerCase()))
  .filter(r => !contacted.has(String(r.email).toLowerCase()))
  .sort((a, b) =>
    (parseFloat(b.intent_score) || 0) - (parseFloat(a.intent_score) || 0) ||
    (Number(a.row_number) || 0) - (Number(b.row_number) || 0));

if (!candidates.length) {
  const withEmail = rows.filter(r => isEmail(String(r.email || ''))).length;
  console.log(`No prospect to send. Rows: ${rows.length}, with a valid email: ${withEmail}, already contacted: ${contacted.size}.`);
  return [];
}

const next = candidates[0];

// ---- Write the email ----
const first = String(next.contact_name || '').split(/\s+/)[0] || 'there';
const hook = next.evidence_type === 'public_request'
  ? `I saw ${next.company}'s post looking for automation and developer help.`
  : `I noticed ${next.company} is hiring for data, reporting and internal-tools work.`;
const angle = next.outreach_angle ? ` ${next.outreach_angle}` : '';
const opportunity = String(next.dashboard_opportunity || '').replace(/\.$/, '');
const stack = next.recommended_stack ? ` (${next.recommended_stack})` : '';

const body = `Hi ${first},

${hook}${angle}
${opportunity ? `\nWhat I have in mind for you: ${opportunity}.\n` : ''}
I build custom dashboards and internal tools${stack} and can put together a short mock-up for ${next.company} before we talk. Would a 15-minute call next week be useful?

Best,
${SENDER_SIGNATURE}

P.S. If this isn't relevant, just reply "no thanks" and I won't email you again.`;

console.log(`Next prospect: ${next.company} <${next.email}> (score ${next.intent_score}). ${candidates.length - 1} left after this.`);

return [{ json: {
  row_email: next.email,          // used by "Mark as sent" / "Mark as error" to find the row
  row_number: next.row_number,
  company: next.company,
  to: next.email,
  subject: `Idea for ${next.company}'s reporting`,
  body,
  sender_name: SENDER_NAME,
  remaining_after_this: candidates.length - 1,
} }];
