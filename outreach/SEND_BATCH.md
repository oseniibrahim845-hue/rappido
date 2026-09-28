# Outreach batch runbook (used by the scheduled 4-hourly trigger)

1. `cd /home/user/rappido && git fetch origin claude/kind-fermat-wa8eun && git checkout claude/kind-fermat-wa8eun && git pull origin claude/kind-fermat-wa8eun`
2. Confirm the Gmail connector is oseniibrahim845@gmail.com: `search_threads in:sent` (pageSize 1) and check `sender`.
   If it is any other account: send NOTHING, stop, and tell the user.
3. Load `outreach/queue.json`; take the first 25 entries with status "pending".
4. For each: search Gmail `in:sent to:<email>`. If any prior sent message exists, set status "skipped_already_contacted".
   Otherwise send with subject/body exactly as stored (plain text), set status "sent", sent_at = UTC ISO time.
   On a send error set status "error" with the message in "error".
5. Check `in:inbox from:mailer-daemon newer_than:1d` for bounces of this batch; set status "bounced".
5b. Mark results with `python3 outreach/mark.py sent <emails...>` (or skipped_already_contacted / bounced / error).
6. Save queue.json, commit ("Outreach batch: N sent"), push to claude/kind-fermat-wa8eun.
7. If no pending entries remain, delete the trigger named "EA outreach 25 every 4h" (list_triggers -> delete_trigger) and report totals.
