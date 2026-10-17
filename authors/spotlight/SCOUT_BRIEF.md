# Daily author scouting -> Author Spotlight rows (fresh-session routine)

You run in a fresh session. Setup:
  cd /home/user/rappido && git fetch origin claude/kind-fermat-wa8eun && git checkout claude/kind-fermat-wa8eun && git pull origin claude/kind-fermat-wa8eun

Goal per run: about 40 NEW authors with personalization_status "Ready", written as Author Spotlight rows.
Launch 4 parallel general-purpose subagents (model sonnet), one per group. If the run message names groups, use exactly
those; otherwise pick 4 groups from the rotation below at random. Each subagent writes
authors/spotlight/bank_<YYYYMMDDHHMM>_<group>.json (unique name) and aims for 10-15 Ready rows (~50 searches max).
Many scouting sessions may run in parallel, so do NOT edit shared files (no SEEN_EMAILS.txt appends, no queue.json,
no ROTATION.txt). Only add your own new bank files. Duplicates are removed later by aq.py build.

Country-group rotation (skip sanctioned countries: Iran, Russia, Belarus, North Korea, Syria, Cuba; also skip Nigeria entirely, user decision 2026-10-02):
 us_south, us_midwest, us_west, us_northeast, uk, ireland, canada, australia, new_zealand, south_africa,
 kenya_ghana, india, philippines, singapore_malaysia, mexico, colombia, argentina, spain, chile, peru_ecuador,
 caribbean_jamaica_trinidad, germany_netherlands_english_writers, nordics_english_writers

Each subagent:
1. Skip any email already in /home/user/rappido/authors/intl/SEEN_EMAILS.txt, authors/queue.json, or any
   authors/spotlight/bank_*.json file (grep them).
2. Find CURRENT authors (book out in the last ~18 months or announced for 2026-27) with a PUBLICLY DISPLAYED email
   (author site contact page, Linktree/Instagram/Facebook bio, publisher/agent page). Never guess or construct an email;
   obscured "[at]" or "[email protected]" emails are not usable. Indie/self-published genre authors (romance, fantasy,
   thriller, horror, cozy mystery, YA, sci-fi) and small-press authors are the best targets. Skip minors, deceased,
   big-agency-only contacts, publisher order desks and generic org addresses.
3. For each candidate follow /home/user/rappido/authors/spotlight/BRIEF.md exactly (research checks, best_offer, the
   26 output keys, email structure, sender Oseni Ibrahim, Spanish for Spanish-language authors).
   Extra rule for automated sending: the best_offer paragraph must only state a gap as fact if it was verified.
   If the gap is Unclear, phrase it as an option without claiming absence (for example "If a short trailer or a few
   reels for <book> is something you have been considering, we can handle the full production."). This lets the row be Ready.
4. Mark Ready only when author, book, email and opening details are verified from search results; otherwise Needs Review.
Do NOT send any email.

After the subagents finish: `git add authors/spotlight/bank_*.json && git commit -m "Author scouting <date>: N ready" &&
git push -u origin claude/kind-fermat-wa8eun` (the send routine loads them into the queue with aq.py build)
(retry push with backoff on network errors; if a push is rejected, pull --rebase and push again).
Report Ready / Needs Review counts by country in 2-3 lines.
