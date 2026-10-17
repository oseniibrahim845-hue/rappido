# Outreach batch runbook (used by the scheduled 4-hourly trigger)

1. `cd /home/user/rappido && git fetch origin claude/kind-fermat-wa8eun && git checkout claude/kind-fermat-wa8eun && git pull origin claude/kind-fermat-wa8eun`
2. Confirm the Gmail connector is oseniibrahim845@gmail.com: `search_threads in:sent` (pageSize 1) and check `sender`.
   If it is any other account: send NOTHING, stop, and tell the user.
2b. `pip install -q dnspython openpyxl` then `python3 outreach/mx_check.py` (drops domains with no mail server).
2c. `python3 outreach/make_queue.py outreach/lead_bank_round*.json`
   (idempotent: only adds lead-bank entries not already in the queue), then re-run `python3 outreach/mx_check.py`.
2d. FOLLOW-UPS FIRST (user approved 2026-09-30: one bump per cold lead, 4+ days after the first email).
   `python3 outreach/followup.py list 25` -> due follow-ups. For each: search Gmail `from:<email>`; if they ever replied,
   run `followup.py replied <email>` and skip. Otherwise find the original via `in:sent to:<email>` and send the stored
   follow-up body with `replyThreadId` = that thread (subject "Re: ..."), then `followup.py done <emails...>`.
   Never send a second follow-up. Follow-ups count toward the 25-per-batch cap.
3. Load `outreach/queue.json`; take the first (25 minus follow-ups sent) entries with status "pending".
4. For each: search Gmail `in:sent to:<email>`. If any prior sent message exists, set status "skipped_already_contacted".
   Otherwise send with subject/body exactly as stored (plain text), set status "sent", sent_at = UTC ISO time.
   On a send error set status "error" with the message in "error".
5. Check `in:inbox from:mailer-daemon newer_than:1d` for bounces of this batch; set status "bounced".
5b. Mark results with `python3 outreach/mark.py sent <emails...>` (or skipped_already_contacted / bounced / error).
6. Save queue.json, commit ("Outreach batch: N sent"), push to claude/kind-fermat-wa8eun.
7. If no pending entries remain AND no follow-ups are due or upcoming (every "sent" entry has followup_at), delete the trigger named "EA outreach 25 every 4h" (list_triggers -> delete_trigger) and report totals.
