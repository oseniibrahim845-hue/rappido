#!/usr/bin/env python3
"""Validate the canonical author-lead workbook against the 15-column contract.

Usage:
  python3 tools/validate_leads.py [path] [--strict] [--quiet]

Exit 1 if errors (or, with --strict, warnings) are found.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leadlib import (COLUMNS, COPY_COLUMNS, NOTE_COLUMNS, CONFIDENCE, STATUS, SEND_STATUS,
                     EMAIL_RE, URL_RE, PHONE_RE, STREET_RE,
                     read_rows, split_multi, norm_email, norm_text, dedupe_keys)

BANNED_SUBJECT = re.compile(r"\b(free|offer|opportunity|deal|urgent|limited|guarantee)\b", re.I)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}|\[(?:first_name|book|title|insert)[^\]]*\]", re.I)
DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "author_spotlight_AU.xlsx")


def validate(path):
    errors, warns = [], []
    header, rows = read_rows(path)

    if header[:len(COLUMNS)] != COLUMNS:
        missing = [c for c in COLUMNS if c not in header]
        extra = [c for c in header if c not in COLUMNS]
        if missing:
            errors.append(f"header: missing column(s) {missing}")
        if extra:
            warns.append(f"header: unexpected column(s) {extra}")
        if not missing and header != COLUMNS:
            warns.append("header: columns present but out of contract order")

    seen = {}          # dedupe key -> first row number
    seen_email = {}
    for n, r in enumerate(rows, start=2):
        def g(c):
            return (r.get(c) or "").strip()
        who = g("author_name") or g("email") or "<blank>"
        conf, status = g("research_confidence"), g("personalization_status")

        if conf not in CONFIDENCE:
            errors.append(f"row {n} ({who}): research_confidence {conf!r} not in {sorted(CONFIDENCE)}")
        if status not in STATUS:
            errors.append(f"row {n} ({who}): personalization_status {status!r} not in {sorted(STATUS)}")
        if conf == "Low" and status == "Ready":
            errors.append(f"row {n} ({who}): Low confidence may never be Ready")

        # send pipeline columns
        if "send_status" in header:
            ss = g("send_status")
            if ss and ss not in SEND_STATUS:
                errors.append(f"row {n} ({who}): send_status {ss!r} not in {sorted(SEND_STATUS)}")
            ds = g("date_sent")
            if ds and not re.match(r"^\d{4}-\d{2}-\d{2}$", ds):
                errors.append(f"row {n} ({who}): date_sent {ds!r} is not ISO YYYY-MM-DD")
            if ds and ss in ("", "Not Sent"):
                warns.append(f"row {n} ({who}): date_sent set but send_status is {ss or 'blank'!r}")
            if ss == "Sent" and not ds:
                warns.append(f"row {n} ({who}): send_status Sent but date_sent blank")

        # email
        emails = split_multi(g("email"))
        if status == "Ready" and not emails:
            errors.append(f"row {n} ({who}): Ready with no email")
        for e in emails:
            if not EMAIL_RE.match(e):
                errors.append(f"row {n} ({who}): malformed email {e!r}")
            ne = norm_email(e)
            if ne in seen_email:
                errors.append(f"row {n} ({who}): duplicate email {e!r} (first seen row {seen_email[ne]})")
            else:
                seen_email[ne] = n

        # copy columns filled iff Ready
        filled = [c for c in COPY_COLUMNS if g(c)]
        if status == "Ready":
            for c in COPY_COLUMNS + NOTE_COLUMNS:
                if not g(c):
                    errors.append(f"row {n} ({who}): Ready but {c} is empty")
            if not g("first_name"):
                errors.append(f"row {n} ({who}): Ready but first_name is empty")
            if not g("book_title"):
                errors.append(f"row {n} ({who}): Ready but book_title is empty")
        elif filled:
            errors.append(f"row {n} ({who}): status {status!r} must leave "
                          f"{filled} blank (email copy)")
        if status in ("Needs Review", "Excluded") and not any(g(c) for c in NOTE_COLUMNS):
            warns.append(f"row {n} ({who}): {status} with no reason recorded in "
                         f"personalization_detail/personalization_reason")

        if status == "Ready":
            # subject
            s = g("subject_line")
            wc = len(s.split())
            if not (4 <= wc <= 12):
                warns.append(f"row {n} ({who}): subject is {wc} words (want 4-12): {s!r}")
            if len(s) > 65:
                warns.append(f"row {n} ({who}): subject is {len(s)} chars (want <=65)")
            if s.rstrip().endswith("."):
                warns.append(f"row {n} ({who}): subject ends with a period")
            if BANNED_SUBJECT.search(s):
                errors.append(f"row {n} ({who}): subject contains a spam-trigger word: {s!r}")
            if s.isupper():
                errors.append(f"row {n} ({who}): subject is ALL CAPS")

            # opening
            ow = len(g("personalized_opening").split())
            if not (21 <= ow <= 90):
                warns.append(f"row {n} ({who}): personalized_opening is {ow} words (want 21-90)")

            # body
            b = g("email_body")
            fn = g("first_name")
            if fn and not b.startswith(f"Hi {fn},"):
                errors.append(f"row {n} ({who}): email_body does not start 'Hi {fn},'")
            op = g("personalized_opening")
            if op and op not in b:
                errors.append(f"row {n} ({who}): email_body does not contain personalized_opening verbatim")
            if "Author Spotlight Feature" not in b:
                errors.append(f"row {n} ({who}): email_body missing the Author Spotlight block")
            if PLACEHOLDER.search(b) or PLACEHOLDER.search(s):
                errors.append(f"row {n} ({who}): unfilled template placeholder in copy")
            if "unsubscribe" not in b.lower():
                warns.append(f"row {n} ({who}): email_body has no opt-out line (Spam Act 2003)")

        # sources
        srcs = split_multi(g("research_sources"))
        urls = [u for u in srcs if URL_RE.match(u)]
        if status in ("Ready",) and not urls:
            errors.append(f"row {n} ({who}): Ready with no source URL")
        if urls and not any("amazon." in u for u in urls):
            warns.append(f"row {n} ({who}): no Amazon source URL among {len(urls)} source(s)")

        # privacy leakage
        for c in ("personalization_detail", "personalization_reason",
                  "personalized_opening", "email_body"):
            v = g(c)
            if PHONE_RE.search(v):
                errors.append(f"row {n} ({who}): possible phone number in {c}")
            if STREET_RE.search(v):
                errors.append(f"row {n} ({who}): possible street address in {c}")

        # dedupe
        for k in dedupe_keys(r):
            if k in seen:
                errors.append(f"row {n} ({who}): duplicate {k[0]} key {k[1]!r} (first seen row {seen[k]})")
            else:
                seen[k] = n

    stats = {
        "rows": len(rows),
        "unique_dedupe_keys": len(seen),
        "email_bearing": sum(1 for r in rows if (r.get("email") or "").strip()),
        "Ready": sum(1 for r in rows if (r.get("personalization_status") or "").strip() == "Ready"),
        "Needs Review": sum(1 for r in rows if (r.get("personalization_status") or "").strip() == "Needs Review"),
        "Excluded": sum(1 for r in rows if (r.get("personalization_status") or "").strip() == "Excluded"),
    }
    return errors, warns, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=DEFAULT)
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--quiet", action="store_true", help="only print the summary")
    a = ap.parse_args()

    if not os.path.exists(a.path):
        print(f"FAIL  no such file: {a.path}")
        return 1
    errors, warns, stats = validate(a.path)

    print(f"== {os.path.basename(a.path)}")
    for k, v in stats.items():
        print(f"   {k:<20} {v}")
    if not a.quiet:
        for e in errors[:60]:
            print("ERROR  " + e)
        if len(errors) > 60:
            print(f"       ... and {len(errors)-60} more errors")
        for w in warns[:40]:
            print("WARN   " + w)
        if len(warns) > 40:
            print(f"       ... and {len(warns)-40} more warnings")
    print(f"-- {len(errors)} error(s), {len(warns)} warning(s)")
    bad = errors or (a.strict and warns)
    print("STATUS: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
