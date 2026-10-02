# Crypto Leads Outreach (n8n)

Sends **20 personalized emails every 4 hours** (120/day) to the leads list, and marks
each lead in the sheet so nobody gets emailed twice. All 400 leads are done in about 3.5 days.

```
Every 4 Hours ─┐
Manual test ───┴─> Get "Not contacted" rows -> Take 20 -> Build email -> Loop:
                     Send (Gmail) -> Mark "Contacted" / "Send failed" -> wait 30-90s -> next
```

## Setup (about 10 minutes)

1. **Upload the leads to Google Sheets**
   - Upload `Crypto_Leads_for_Google_Sheets.xlsx` to Google Drive, then open it with
     Google Sheets (*File -> Save as Google Sheets*).
   - Keep the tab name **`Crypto leads`**. The file has an extra **`Sent At`** column.
   - Copy the sheet URL.
2. **Import the workflow** in n8n: *Workflows -> Import from File* -> `crypto-leads-outreach.json`.
3. **Connect credentials**
   - Open **Get Uncontacted Leads**, **Mark as Contacted** and **Mark as Failed**. Pick or create a
     *Google Sheets OAuth2* credential, then paste your sheet URL into *Document*.
   - Open **Send Email (Gmail)**. Pick or create a *Gmail OAuth2* credential and set *Sender Name*.
4. **Edit the email.** Open **Build Personalized Email** and change `YOUR_NAME`,
   `YOUR_COMPANY` and `CALENDAR_LINK` at the top. You can change the subject and body there too.
5. **Test.** Temporarily change *Take 20* to `1` and put your own email in the first row.
   Click **Test workflow**, check the email and confirm that the row changed to `Contacted`.
   Then set it back to `20`.
6. **Activate** the workflow (toggle at the top right). It now runs every 4 hours.

## How it works

- Only rows where `Status` = `Not contacted` are picked up. After sending, the row is set to
  `Contacted` with a timestamp. If the send fails, the row is set to `Send failed`, so it is
  not retried automatically. Reset it to `Not contacted` to retry.
- The greeting uses the contact name and falls back to "Hi there," for empty names or
  bot names such as "GitHub Actions".
- Each email mentions the lead's project, source (npm/PyPI), chains and the best-fitting service.
- A random delay of 30-90 seconds between emails makes sending look less like a bulk blast.
- To pause the outreach, deactivate the workflow. To change the pace, edit *Every 4 Hours*
  or *Take 20*.

## Tips

- Use SMTP instead of Gmail by swapping the Gmail node for a **Send Email** node with the
  same fields (`{{$json.Email}}`, `{{$json.subject}}`, `{{$json.body}}`).
- 120/day is safe for a warmed-up Google Workspace account. A brand-new Gmail address
  may get flagged, so start with `Take 10` for the first few days.
- Honor "no thanks" replies by setting that row's Status to `Unsubscribed`.
