# Author Spotlight — Email Template (Australia)

Derived from the 634 shipped `Ready` bodies in `author_spotlight1.xlsx`
(mean 184 words, range 158–227; 632/634 open `Hi <First>,`; all 634 carry an
identical fixed tail). The only variable parts are the greeting, the opening
paragraph, and the subject line.

---

## 1. What changed from the draft you pasted

Your draft is a pure template — it would read identically to all 100 recipients.
The shipped rows replaced its generic top with a researched opening. Concretely:

| Your draft | Shipped version | Why |
|---|---|---|
| "I hope you're having a productive day." | *removed* | 0 of 634 kept it. Filler before the only sentence that proves the email isn't bulk. |
| "I recently discovered your book and was truly inspired by the message, insight, and value you're sharing…" | replaced by `personalized_opening` | Generic praise that fits any book signals a mail-merge. The researched fact is the entire value of the email. |
| "Your work reflects a unique perspective, and I believe your story has the potential to inspire…" | *removed* | Same reason — unfalsifiable flattery. |
| "Enhance your brand and online presence" | "Enhance your **author** brand and online presence" | Specific to the reader's identity. |
| "Create additional brand awareness to reach readers and raise your book exposure" | "Create additional awareness and exposure for your book" | The original is clumsy; this is the shipped wording. |
| "If you'd like to take advantage of this…" | "If you'd like to learn more…" | "Take advantage of" reads transactional on a first touch. |
| — | **+ sender identification and opt-out line** | Spam Act 2003 (Cth). See §4. |
| signed *Ademola Adewuyi* | signed **Oseni Ibrahim** | Your file's 634 rows are signed with the other name — check before sending. |

---

## 2. The template

`{{first_name}}` and `{{personalized_opening}}` are the only substitutions.
Everything else is fixed and must be byte-identical across rows.

```
Hi {{first_name}},

{{personalized_opening}}

I'd like to invite you to be featured in an Author Spotlight Feature on The Author
Ledger. This feature will showcase your journey as an author, the inspiration behind
your book, and the experiences and ideas that make your work distinctive.

A feature like this can help you:

- Introduce your work to a wider audience of readers
- Strengthen your credibility and visibility as an author
- Enhance your author brand and online presence
- Create additional awareness and exposure for your book

Our team will take care of the entire process, ensuring everything is simple,
seamless, and convenient from start to finish.

If you'd like to learn more, I'd be delighted to provide the information and guide
you through the next steps.

I look forward to hearing from you.

Warm regards,
Oseni Ibrahim
The Author Ledger

I found your contact details published on your author page. If you'd rather not hear
from me again, reply with "unsubscribe" and I'll remove you immediately.
```

---

## 3. Writing `personalized_opening`

This paragraph is the whole email. Rules, taken from what shipped:

- **21–90 words, target ~45.** 2–3 sentences.
- **One specific, verifiable fact** from `research_sources` — the book's actual
  premise, its intended reader, the author's relevant background, the real-world
  event behind it, a quoted opening image.
- **Name the book** in the first sentence.
- **No adjectival praise.** Not "inspiring", "powerful", "amazing", "truly moved".
  Show you read something; don't assert a feeling.
- **Never invent.** If research produced nothing concrete, the row is
  `Needs Review`, not a padded opening.
- Plain, level register — a peer who did their homework, not a fan and not a vendor.

**Worked examples (real rows):**

> I came across *Be You-T-Full* and liked that you wrote it for people curious about
> non-surgical options like Botox and lasers but unsure where to even start. Given
> that you've run your own aesthetic practice since 2006 and teach at UC Irvine's
> graduate nursing program, it's clear the book comes from real clinical experience
> rather than marketing copy.

> *Dennis Littrell's True Crime Companion* caught my eye for its concept: instead of
> telling one true crime story, it's a collection of your own reviews of some of the
> best true crime books out there, with updates added later. That's a different way
> into the genre than most true crime authors take.

**Australian openings** should use the local hook where the research supports it —
setting, regional subject matter, a local writers' centre or festival credit — but
only where it is evidenced. Use Australian spelling in the opening when quoting or
paraphrasing the author's own material.

---

## 4. Subject line

4–12 words · ≤65 characters · sentence case · no trailing period.

Banned: `Re:` / `Fwd:` on a cold email, ALL CAPS, exclamation marks, emoji, and the
words *free*, *offer*, *opportunity*, *deal*, *urgent*, *limited*.

Patterns that shipped:

- `Loved the concept behind Be You-T-Full`
- `Your True Crime Companion caught my eye`
- `That Texas ranch behind Tessa's Heart`
- `The wine-country expertise behind Cypress Cove`
- `80 years of journalism in Fire Bone!` ← the one exception; avoid the `!`

---

## 5. Compliance additions (Australia)

The last block of the template is not decoration. Under the **Spam Act 2003 (Cth)** a
commercial electronic message sent to an Australian address must identify the sender
and carry a functional unsubscribe, and must rest on consent — here, *inferred*
consent from a conspicuously published author-business address, valid only while the
message is directly relevant to that author's published work.

So:

1. Keep the sender line (`Oseni Ibrahim` / `The Author Ledger`).
2. Keep the opt-out sentence, and **honour it within 5 working days** — the Act's
   limit — by setting `send_status = Opted Out` and never re-adding that person.
3. Keep the relevance real. The personalized opening is what makes this outreach
   about the recipient's published work rather than untargeted bulk mail — which is
   the compliance argument as much as the conversion one.
4. If a source page says "no unsolicited enquiries", that is an exclusion, not a lead.

This is operational guidance, not legal advice — confirm with your own adviser before
sending at volume.
