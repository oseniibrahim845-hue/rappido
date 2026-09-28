# n8n outreach workflow: 20 emails every 4 hours

`outreach_workflow.json` sends **one personalised email every 12 minutes, around the clock, every day**. That's 20 emails every 4 hours, or up to 120 a day. Each send waits a random 0–3 minutes first, so the send times look less robotic.

## How it works
1. **Schedule trigger** (cron `0 */12 * * * *`) fires every 12 minutes, 20 times per 4 hours.
2. **Read prospects sheet** loads the `Outreach` tab of your Google Sheet.
3. **Pick next prospect** takes the highest-scoring row that has an `email` and an empty `status`, and writes the email from that row's columns. When no rows are left, or the optional `MAX_PER_DAY` cap is reached, it stops without sending anything.
4. **Random delay** waits 0–3 minutes.
5. **Send email (Gmail)** sends a plain-text email.
6. **Mark as sent / Mark as error** writes `status` and `sent_at` back to the row, so no one is emailed twice.

## Setup (about 10 minutes)
1. **Create the sheet.** In Google Sheets, go to File → Import → upload `outreach_sheet.csv`. Rename the tab to `Outreach`. Copy the sheet ID from its URL (the part between `/d/` and `/edit`).
2. **Fill in contacts.** Add `contact_name` and `email` for each prospect you want to reach. Rows without an email are skipped. The research didn't collect contact details, so find the right person yourself (for example the hiring manager or head of data).
3. **Import the workflow.** In n8n, go to Workflows → Import from File → `outreach_workflow.json`.
4. **Connect accounts.** Open the three Google Sheets nodes and the Gmail node and select your Google Sheets OAuth2 and Gmail OAuth2 credentials. In each Sheets node, replace `PASTE_YOUR_GOOGLE_SHEET_ID` with your sheet ID.
5. **Personalise the sender.** In the *Pick next prospect* Code node, edit `SENDER_NAME` and `SENDER_SIGNATURE`.
6. **Set your timezone.** Go to Workflow → Settings → Timezone. It controls when a "day" starts for `MAX_PER_DAY`, and the hours if you limit sending to business hours.
7. **Test first.** Put your own address in one row, click *Execute workflow*, check the email and the sheet update, then clear that row's `status`. Then switch the workflow to **Active**.

## Changing the pace
- **Business hours only (recommended):** use `0 */12 8-17 * * 1-5` for 20 every 4 hours from 08:00 to 18:00, Monday to Friday. Emails sent at 3am to prospects look automated and get opened less.
- **Daily cap:** set `MAX_PER_DAY` in the Code node, e.g. `40`.
- **Different volume:** 20 emails every 4 hours is one every 12 minutes. For 10 every 4 hours use `*/24`.
- **Pause:** deactivate the workflow. **Skip someone:** type anything, e.g. `skip`, in their `status` cell.

## Before you go live
- **Review each row's `outreach_angle`.** It's inserted into the email word for word, and some were written as research notes rather than sentences to a prospect. Edit them into natural sentences in the sheet.
- **Verify each posting.** The evidence links weren't checked, so make sure each role or post is still live before you mention it.
- **Keep the opt-out line and honour replies.** Many prospects are in the EU and UK (GDPR/PECR), Canada (CASL) and the US (CAN-SPAM). B2B cold email is generally allowed with a relevant offer and an easy opt-out. When someone says no, set their `status` to `unsubscribed`.
- **Volume and deliverability.** Around the clock this is 120 emails a day. That's under Gmail's sending limits (about 500 a day for personal accounts, 2,000 for Workspace), but 120 cold emails a day from one mailbox can get it flagged as spam. Keep to 30–50 a day per mailbox on an established account. On a new domain, start at 5–10 a day for the first 2 weeks, and set up SPF, DKIM and DMARC. For more volume, spread it across several mailboxes.
- **List size.** The current sheet has 49 prospects. At this pace it runs out in about 10 hours once emails are filled in, then stops by itself. Add rows to keep it going.
- **Replies aren't detected automatically.** Check your inbox and mark rows `replied` so they don't get a follow-up later.
