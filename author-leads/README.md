# Author Lead Generation — Australia

Research-and-personalization pipeline for The Author Ledger's Author Spotlight
outreach to Australian Amazon-listed and KDP/independent authors.

| File | What it is |
|---|---|
| `PROMPT.md` | **The operating prompt.** Australia rewrite of the research brief, with the 15-column output contract, evidence rules, confidence/status gates, and the 100-Ready-per-run loop. |
| `EMAIL_TEMPLATE.md` | The email body: what changed from the original draft, the fixed template, and the rules for writing the personalized opening and subject line. |
| `author_spotlight_AU.xlsx` | **The canonical file.** Sheet `Pilot Batch`, exactly 15 columns. The only user-facing lead list. |
| `templates/author_spotlight_AU_template.csv` | Same 15 columns as CSV, for batch hand-off. |
| `tools/merge_leads.py` | Idempotent merge: dedupe, timestamped backup, atomic write, before/after counts. |
| `tools/validate_leads.py` | Contract validator: schema, vocabularies, status gates, copy quality, privacy leakage, duplicates. |
| `tools/leadlib.py` | Shared schema, normalization, and I/O. |
| `logs/run_log.jsonl` | Operations log (queries, decisions, run stats). Not a lead list. |
| `backups/` | Timestamped pre-write copies of the canonical file. |

## Per-run workflow

```bash
# 1. Research per PROMPT.md, emitting a batch of 15-column rows as JSON or CSV.

# 2. Preview the merge without writing.
python3 tools/merge_leads.py --batch batch.json --run-id 2026-09-14-nsw-01 --dry-run

# 3. Merge for real (backs up, dedupes, writes atomically, logs).
python3 tools/merge_leads.py --batch batch.json --run-id 2026-09-14-nsw-01

# 4. Validate and report.
python3 tools/validate_leads.py --strict
```

Re-running step 3 with the same batch changes nothing.

## The contract in one screen

15 columns, fixed order:

```
author_name · email · first_name · book_title · book_topic
personalization_detail · personalization_reason · personalized_opening
subject_line · email_body · research_sources · research_confidence
personalization_status · send_status · date_sent
```

- `research_confidence` ∈ `High` / `Medium` / `Low` — identity certainty.
- `personalization_status` ∈ `Ready` / `Needs Review` / `Excluded`.
- `send_status` ∈ `Not Sent` / `Queued` / `Sent` / `Bounced` / `Replied` /
  `Opted Out` / `Do Not Contact`. Research only ever writes `Not Sent`.
- **`Low` confidence can never be `Ready`.**
- `personalized_opening`, `subject_line`, `email_body` are blank unless `Ready`.
- `personalization_detail` / `personalization_reason` are required on `Ready` and
  carry the open question or exclusion reason otherwise.

## Requirements

Python 3 and `openpyxl` (`pip install openpyxl`).
