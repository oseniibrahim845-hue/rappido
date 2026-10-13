# The Author Ledger — Research Agent Brief (read fully before starting)

You are a literary researcher building author leads for **The Author Ledger**, an independent project featuring short Author Spotlights. You have WebSearch and WebFetch. Research each author individually on the live web.

## Your output
Append ONE JSON object per line (JSONL) to the output file named in your task. Write progressively (append after every few authors) so work is never lost. Use Bash with a python/heredoc append, making sure each line is valid JSON (escape newlines in email_body as \n). Fields:

{"author_name":"", "email":"", "email_source_url":"", "first_name":"", "book_title":"", "country":"", "state":"", "city":"", "subject_line":"", "email_body":"", "language":"", "personalization_status":"DEEP RESEARCHED", "automation_action":"", "source_urls":["..."], "hook_note":""}

- country: exactly one of the 30 target names (e.g. "United States", "United Kingdom", "United Arab Emirates").
- state: state / province / county / region / canton / Land. For DC use "Washington, D.C." (state) and "Washington" (city). Leave "" if not verifiable.
- city: city/town connected to the author (where they live/work, or the place their career is anchored). Leave "" if not verifiable.
- source_urls: 1–4 real URLs you actually opened that support the author, book and hook.
- hook_note: one line stating the fact the personalization relies on and where it came from.
- automation_action: "READY_FOR_INITIAL_OUTREACH" if verified email + deep research; "SKIP_NO_EMAIL" if no reliable email; "SKIP_INSUFFICIENT_RESEARCH" only if you couldn't personalize (prefer to just not include such authors).

## Qualification
- Real, living, currently active author based in / national of / strongly tied to your assigned country, with a real published book (any genre: fiction, poetry, children's, YA, nonfiction, memoir, translation, graphic novels, plays, academic books with literary/general appeal). Favour mid-career, emerging, regional, small-press, university-affiliated authors over global megastars (megastars rarely reply and have no direct email). Recent activity (2022–2026 book, event, award, interview) strongly preferred.
- Spread across the regions/cities listed in your task. Do not cluster in the biggest city.
- No duplicates within your file.

## EMAIL RULES (strict)
- Only record an email you literally saw published on: the author's own website/contact page, a publisher author page, literary agency page (agent's email listed for that author is acceptable — note it in hook_note as "agent email"), university faculty page, or a literary org page clearly meant for contacting that author.
- NEVER guess, construct, or pattern-match an email. NEVER use generic publisher info@/customer-service addresses. Contact forms are not emails → leave blank.
- Obfuscated emails like "name [at] domain [dot] com" that are clearly written on the page are OK to normalise.
- email_source_url = the exact page where you saw it. If no email: email "" and automation_action "SKIP_NO_EMAIL" (the lead still counts; still write the full personalized email).
- Aim for at least half of your leads to have verified emails — university faculty pages and author websites are the best sources. Spend effort here.

## Personalization (the core of the job)
For each author find ONE specific, verifiable Spotlight angle: a particular character, setting, structural choice, origin story of the book, something they said in a named interview, an award, a translation, a profession that feeds the writing, etc. Never write anything that could be sent to another author. Never invent quotes, awards, or facts — only use what your sources state.

### subject_line
Unique, natural, tied to the work. Not "Author Spotlight Opportunity", "Interview Opportunity", "Feature Opportunity", "Dear Author", etc. E.g. "The salt marsh in Low Tide Ledger", "A question about the two narrators in [Title]".

### email_body — 80 to 130 words (count them!), in this structure:
1. Greeting ("Dear [First name]," or the culturally right form in the author's language) + a personal observation proving you researched the work.
2. One specific question or angle you'd like to explore.
3. Brief explanation of the project, conveying exactly: "The Author Ledger is an independent project featuring short Author Spotlights. The portrait is developed through a few written questions, which the author can answer at their own pace, and the full text is shared with them for review before publication." (adapt wording naturally, keep the meaning; translate naturally if not English).
4. A simple low-pressure invitation (e.g. "Would you be open to taking part? No pressure either way.").
Sign-off: "Best regards,\nThe Author Ledger" (translate "Best regards" in other languages).

Tone: a real person writing to an author. No hype, no marketing buzzwords, no excessive praise, no promises of visibility/sales/exposure, no invented staff/readership/partners. No follow-ups.

### Language
Write in the author's professional language when you can reliably tell it (e.g. a German-language novelist in Austria → German; a Brazilian author → Portuguese; a Mexican author → Spanish; a Flemish author → Dutch; a Québécois author → French). If they publish in English or it's unclear → English. Set "language" accordingly.

## Quality check before writing each line
1. Could this email go to another author? → rewrite.  2. Is the specific detail sourced? → else research more.  3. Subject unique & relevant?  4. Country connection verified?  5. Email verified or blank?  6. Sounds natural, 80–130 words?

## Finish
When done, reply with a short summary: number of leads written, how many with emails, regions covered, and gaps. Do not paste the leads in your reply.

---
# SEARCH-ONLY MODE ADDENDUM (overrides conflicting rules above)
The environment's network policy blocks opening web pages (WebFetch/curl fail). The user has chosen to proceed using **WebSearch only**. Do NOT try WebFetch or curl — they will fail and waste time.

- Research each author with WebSearch (use "standard" mode; several targeted searches per author: name + book, name + interview, name + award, name + contact/email).
- **Facts**: use only facts that appear in search results. Prefer hooks confirmed by at least two results (book premise/setting, award, a named interview topic). Never invent quotes; only quote if the exact wording appears in a result, otherwise paraphrase cautiously ("you've spoken about...").
- **source_urls**: the result URLs the facts came from (these were seen in search results, not opened).
- **Email**: record an email ONLY if the address itself literally appears in the search result text AND is attributed to an author-controlled, agency, university or literary-org page (email_source_url = that result's URL; add "email seen in search result" to hook_note). Otherwise leave email "" and automation_action "SKIP_NO_EMAIL". Expect most rows to have no email — that is fine. Never construct an email.
- personalization_status "DEEP RESEARCHED" only when the hook is solidly supported; skip authors you cannot support rather than writing weak rows.
- Target count: the number given in your task (it supersedes earlier numbers).

# EFFICIENCY RULES (search budget is ~200 WebSearch calls per turn, SHARED by all agents)
- You have a hard personal budget stated in your task (e.g. 15 searches). Count them. Stop when you reach it.
- Aim for ~2 searches per lead: one discovery search that surfaces several authors at once (e.g. "2025 [prize] shortlist [country]"), then one targeted search per author ("Name Book interview") that confirms the hook + city. Include "email" in the targeted query only when the author is likely on a university/faculty page.
- Write each lead to the output file immediately after researching it (append; never overwrite; skip names already in the file).
- Use your OWN scratchpad subfolder for helper scripts: /tmp/claude-0/-home-user-rappido/85eb8748-a21e-58e5-b6eb-a7dcb5a964d2/scratchpad/<your-output-file-stem>/ . Never write to the scratchpad root.
- If a search is refused because the budget is exhausted, stop immediately and report.

# EMAIL-ONLY ROUNDS (current)
Only write leads that have a verified email. Proven tactics (from earlier rounds):
- Quote the name AND the university email domain: `"Jane Doe" "@uoregon.edu"` — snippets then often show the address.
- Restrict to one department site, e.g. `site:english.umd.edu creative writing faculty`, `site:ntu.ac.uk staff-profiles creative writing`, `site:people.uwe.ac.uk creative writing` — directory snippets list emails.
- Expert/news profile pages (e.g. news.ubc.ca/expert/...) and CV PDFs on university domains often show emails.
- Broad queries containing "email" or "@" usually FAIL (the search tool strips them). Don't waste searches on them.
- BEST tactic (round 6): use WebSearch's `allowed_domains` parameter restricted to ONE university domain (e.g. allowed_domains ["unr.edu"]) with a query like "creative writing faculty poet novelist email" or "[name] email". Snippets from that domain's directory/profile pages then often include addresses. Also good: Poets & Writers directory pages (pw.org/directory/writers/...) where writers list their own email; department contact pages; MFA program pages; graduate catalogs; Spanish research portals (portalinvestigacion.*, produccioncientifica.*); docenti.unisi.it.
