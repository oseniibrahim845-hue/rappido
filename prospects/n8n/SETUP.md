# n8n outreach workflow: 20 emails every 4 hours

`outreach_workflow.json` runs **every 4 hours**, picks the **next 20 prospects** and sends them one after another, 30 seconds apart. That's up to 120 emails a day.

## How it works
1. **Every 4 hours** (cron `0 0 */4 * * *`) starts a run.
2. **Read prospects sheet** loads the `Outreach` tab of your Google Sheet.
3. **Pick next prospects + write emails** takes the 20 highest-scoring rows that have an `email` and haven't been contacted, and writes an email for each. If there are fewer than 20 left, or the `MAX_PER_DAY` cap is close, it sends fewer. If none are left it stops without sending anything.
4. **Loop Over Items** hands the prospects over one at a time until all of them are done.
5. **Send email (Gmail)** sends a plain-text email. It retries up to 3 times.
6. **Mark as sent** or **Mark as error** writes `status` and `sent_at` back to that row, so no one is emailed twice.
7. **Gap between emails (30s)** waits 30 seconds, then the loop moves to the next prospect.

### Why it doesn't stop halfway
- A failed email is marked `error` in the sheet and the loop carries on with the next prospect.
- A failed sheet update is retried 3 times. If it still fails, the loop carries on anyway.
- Gmail and Google Sheets calls retry 3 times, 5 seconds apart, before giving up.
- The gap is fixed at 30 seconds (not random). A full batch of 20 takes about 10 minutes, well inside the 1-hour run limit.

## Setup (about 10 minutes)
1. **Create the sheet.** In Google Sheets, go to File → Import → upload `outreach_sheet.csv`. Rename the tab to `Outreach`. Copy the sheet ID from its URL (the part between `/d/` and `/edit`).
2. **Fill in contacts.** Add `contact_name` and `email` for each prospect you want to reach. Rows without an email are skipped. The research didn't collect contact details, so find the right person yourself (for example the hiring manager or head of data).
3. **Import the workflow.** In n8n, go to Workflows → Import from File → `outreach_workflow.json`.
4. **Connect accounts.** Open the three Google Sheets nodes and the Gmail node and select your Google Sheets OAuth2 and Gmail OAuth2 credentials. In each Sheets node, replace `PASTE_YOUR_GOOGLE_SHEET_ID` with your sheet ID.
5. **Personalise the sender.** In the *Pick next prospects + write emails* Code node, edit `SENDER_NAME` and `SENDER_SIGNATURE`.
6. **Set your timezone.** Go to Workflow → Settings → Timezone. It controls when a "day" starts for `MAX_PER_DAY`, and the hours if you limit sending to business hours.
7. **Test first.** Put your own address in one row, click *Execute workflow*, check the email and the sheet update, then clear that row's `status`. Then switch the workflow to **Active**.

## Changing the pace
- **Emails per run:** set `BATCH_SIZE` in the Code node.
- **How often:** edit the cron. `0 0 */4 * * *` is every 4 hours. `0 0 8-16/4 * * 1-5` is 08:00, 12:00 and 16:00 on weekdays only (recommended, so prospects don't get emails at 3am).
- **Gap between emails:** change the Wait node's 30 seconds. Keep it under 60 seconds. Longer waits are saved to the database and resumed later, which is slower and more fragile.
- **Daily cap:** set `MAX_PER_DAY` in the Code node, e.g. `40`.
- **Pause:** deactivate the workflow. **Skip someone:** type anything, e.g. `skip`, in their `status` cell.

## Before you go live
- **Review each row's `outreach_angle`.** It's inserted into the email word for word, and some were written as research notes rather than sentences to a prospect. Edit them into natural sentences in the sheet.
- **Verify each posting.** The evidence links weren't checked, so make sure each role or post is still live before you mention it.
- **Keep the opt-out line and honour replies.** Many prospects are in the EU and UK (GDPR/PECR), Canada (CASL) and the US (CAN-SPAM). B2B cold email is generally allowed with a relevant offer and an easy opt-out. When someone says no, set their `status` to `unsubscribed`.
- **Volume and deliverability.** Around the clock this is 120 emails a day. That's under Gmail's sending limits (about 500 a day for personal accounts, 2,000 for Workspace), but 120 cold emails a day from one mailbox can get it flagged as spam. Keep to 30–50 a day per mailbox on an established account. On a new domain, start at 5–10 a day for the first 2 weeks, and set up SPF, DKIM and DMARC. For more volume, spread it across several mailboxes.
- **List size.** The current sheet has 49 prospects. At this pace it runs out after 3 runs (about 12 hours) once emails are filled in, then stops by itself. Add rows to keep it going.
- **Replies aren't detected automatically.** Check your inbox and mark rows `replied` so they don't get a follow-up later.
