# The Author Ledger — author lead scouting (runs 1–10 — 748 leads)

- `author_ledger_leads.csv` — the 17-column outreach CSV (748 rows, 632 with an email to confirm).
- `author_ledger_leads_with_email.xlsx` / `.csv` — only the rows with an email (xlsx opens in Google Sheets; second tab = sources).
- `author_ledger_sources.csv` — per-row audit trail (language, email_source, source URLs).
- `raw/` — per-region JSONL from the research agents. `pipeline/` — brief, merge/QA and email-check scripts.

**Status: no row is ready to send.** During this run the environment's network policy blocked
opening web pages (WebFetch/curl denied), and the shared web-search budget (200/turn) ran out.
Every fact and email here came from search-result snippets only, so every row is marked
`INSUFFICIENT RESEARCH` / `SKIP_INSUFFICIENT_RESEARCH`, with `last_error` naming the page to open to confirm.
After confirming a row by hand, set `personalization_status=DEEP RESEARCHED` and
`automation_action=READY_FOR_INITIAL_OUTREACH` (or `SKIP_NO_EMAIL` when email is blank), and clear `last_error`.
