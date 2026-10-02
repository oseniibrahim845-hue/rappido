# Daily author scouting -> Author Spotlight rows (fresh-session routine)

You run in a fresh session. Setup:
  cd /home/user/rappido && git fetch origin claude/kind-fermat-wa8eun && git checkout claude/kind-fermat-wa8eun && git pull origin claude/kind-fermat-wa8eun

Goal per run: about 40 NEW authors with personalization_status "Ready", written as Author Spotlight rows.
Launch 4 parallel general-purpose subagents (model sonnet), one per country group from the rotation below
(pick the 4 groups after the last group used, recorded in authors/spotlight/ROTATION.txt; update that file).
Each subagent writes authors/spotlight/bank_<YYYYMMDD>_<group>.json and aims for 10-12 Ready rows (~50 searches max).

Country-group rotation (skip sanctioned countries: Iran, Russia, Belarus, North Korea, Syria, Cuba):
 us_south, us_midwest, us_west, us_northeast, uk, ireland, canada, australia, new_zealand, south_africa, nigeria,
 kenya_ghana, india, philippines, singapore_malaysia, mexico, colombia, argentina, spain, chile, peru_ecuador,
 caribbean_jamaica_trinidad, germany_netherlands_english_writers, nordics_english_writers

Each subagent:
1. Read /home/user/rappido/authors/intl/SEEN_EMAILS.txt and skip any email already there.
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
5. Append every email you output to SEEN_EMAILS.txt.
Do NOT send any email.

After the subagents finish: run `python3 authors/aq.py build` to load Ready rows into authors/queue.json, then
`git add -A authors && git commit -m "Author scouting <date>: N ready" && git push -u origin claude/kind-fermat-wa8eun`
(retry push with backoff on network errors; if a push is rejected, pull --rebase and push again).
Report Ready / Needs Review counts by country in 2-3 lines.
