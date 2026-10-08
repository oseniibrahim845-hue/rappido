# Author Spotlight sender for n8n (50 emails a day)

Files
- `author_spotlight_sender.json`  the workflow to import into n8n (Workflows, Import from file)
- `build_workflows.py`  rebuilds both workflow files. Edit the email text or limits here, then run it
- `test_runner.py`, `make_test_data.py`, `smtp_sink.py`, `test_author_spotlight_sender.json`  the test kit (see Testing)

## Setup (about 15 minutes)
1. Make your own copy of the Google Sheet "Author Ledger Leads" (File, Make a copy). Copy the new sheet ID from its web address.
2. In n8n import `author_spotlight_sender.json`. Open the nodes named "Read Leads", "Mark Sent", "Mark Failed", "Read Leads For Mail" and "Mark Bounced or Replied". Pick your Google Sheets credential and paste your sheet ID.
3. Open "Send Email". Create an SMTP credential for any mailbox you want to send from (Gmail needs an app password. Hostinger uses smtp.hostinger.com port 465). Put that address in the From field.
4. Open "New Mail (IMAP)". Create an IMAP credential for the same mailbox (Hostinger uses imap.hostinger.com port 993). This watches for bounces and replies and marks those rows, so nobody is emailed twice.
5. In "Pick Batch" set `DRY_RUN: true` and run the workflow once by hand. It builds the emails but sends nothing. Check the output, then set `DRY_RUN: false` and activate the workflow.

## How it works
- Runs every hour from 8:00 to 17:00 (workflow timezone, change it in Settings). It sends up to 5 emails per run, with a random wait of 90 to 240 seconds between emails. That gives 50 a day.
- Hard cap: it counts sends in the last 24 hours from the `sent_at` column and never goes over 50 (`DAILY_CAP`).
- It only sends to rows with `status` empty or `pending`, a valid email, a book title and a personal opening. Duplicates and anyone with another status (sent, bounced, replied, failed) are skipped.
- No follow ups. Replies and bounces are marked in the sheet by the IMAP flow.
- Plain text only, no tracking, and the n8n footer is turned off.

## Sheet columns
email, first_name, book_title, personalized_opening, country, status, sent_at, error. Fill the first five. The workflow fills the rest. The opening should be two short sentences built on one real detail about the author or book.

## Warm up a new mailbox
Weeks 1 and 2: warm up and replies only. Week 3: 10 a day (`PER_RUN: 1`). Week 4: 25 a day (`PER_RUN: 3`). Then 50 a day (`PER_RUN: 5`). Keep bounces under 3 percent.

## Testing (done on n8n 2.35.7)
The test copy swaps Google Sheets and the mailbox for local files and a local mail server, and runs the same code nodes. Results: a normal run sends 5 and marks them. With 47 already sent in 24 hours it sends 3. With 50 sent it sends 0. A dry run sends 0. Invalid emails, missing openings, duplicates, and bounced, replied or failed rows are skipped. Bounce and reply messages mark the right rows. Emails have no n8n footer, no "paid" or "free" wording, and no brackets or dashes.
Not tested against real accounts: the Google Sheets nodes, the IMAP trigger and a real SMTP login. Do the dry run first.

## Rules to keep
Run only one sender at a time. If this workflow runs, stop the Gmail runs done by Claude, or the 50 a day limit is broken. For EU contacts keep a clear way to opt out, and for US contacts keep a real postal address in the footer.
