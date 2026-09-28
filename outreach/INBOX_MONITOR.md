# Inbox monitor runbook (hourly trigger "Outreach inbox monitor")

1. Confirm Gmail connector is oseniibrahim845@gmail.com (in:sent, pageSize 1). If not, stop and tell the user.
2. Search `in:inbox newer_than:2h -from:mailer-daemon -from:postmaster` plus `from:mailer-daemon newer_than:2h`.
   Only look at threads that are replies to outreach (a message from oseniibrahim845@gmail.com earlier in the thread)
   or messages from an address listed in outreach/queue.json / EA_Trading_Bot_Prospects_500.xlsx.
   Keep a record of handled message IDs in outreach/inbox_seen.json so nothing is reported twice.
3. Bounces: mark with `python3 outreach/mark.py bounced <email>`.
4. For each new human reply: read it fully, summarise it for the user in 2-3 lines, and prepare a DRAFT reply
   (do NOT send). Show the draft in chat. Send only after the user approves.
   Pricing rule: do not mention pricing in cold emails. Once the prospect shows interest AND the project has been
   discussed in enough detail (scope, platform, features), the reply must state clearly that the work is paid,
   per project, and offer a fixed quote (or give the quote if the user has provided one).
5. If there is nothing new, report nothing (one short line at most).
6. Commit/push any file changes to claude/kind-fermat-wa8eun.
