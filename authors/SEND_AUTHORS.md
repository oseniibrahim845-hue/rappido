# Author Spotlight send runbook (scheduled every 4h, user approved 2026-10-02: "send all ... do the outreach the way we did crypto")

1. cd /home/user/rappido && git pull origin claude/kind-fermat-wa8eun (scouting runs push new rows to this branch).
2. Confirm Gmail is oseniibrahim845@gmail.com (search_threads in:sent pageSize 1, check sender). Otherwise send NOTHING and tell the user.
3. python3 authors/aq.py build
4. FOLLOW-UPS FIRST: python3 authors/aq.py fu 35. For each: search Gmail `from:<email>`; if they ever replied run
   `aq.py mark replied <email>` and skip. Else find the original via `in:sent to:<email>` and send the follow-up body with
   replyThreadId = that thread, then `aq.py fudone <emails>`. Only one follow-up per lead, ever.
5. Fill the rest of 35 per batch (raised 2026-10-03, authors-only focus): python3 authors/aq.py next <35 - followups>. For each: search `in:sent to:<email>`;
   if any prior message exists, `aq.py mark skipped_already_contacted <email>`. Else send subject/body exactly as stored (plain text),
   then `aq.py mark sent <email>`; on error `aq.py mark error <email>`.
6. Check `in:inbox from:mailer-daemon newer_than:1d` for bounces of author emails -> `aq.py mark bounced <emails>`.
7. Commit ("Author outreach batch: N sent, M follow-ups") and push.
8. Report in 1-2 lines. Replies are handled by the hourly inbox monitor (draft only, never send replies without the user's approval;
   for authors use the Author Ledger live-reply format and prices from outreach/PRICE_LIST.md only when asked).
