#!/usr/bin/env python3
"""Idempotent merge of a research batch into the canonical author-lead workbook.

  python3 tools/merge_leads.py --batch batch.json [--run-id r1] [--dry-run]

Batch may be JSON (list of objects), CSV, or XLSX using the 15 contract columns.
Re-running the same batch is a no-op. Always backs up before writing, and writes
the canonical file atomically.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leadlib import (COLUMNS, COPY_COLUMNS, STATUS, CONFIDENCE, read_rows,
                     write_rows, backup, dedupe_keys, split_multi, norm_email,
                     now_stamp, MULTI)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "author_spotlight_AU.xlsx")
BACKUPS = os.path.join(ROOT, "backups")
RUNLOG = os.path.join(ROOT, "logs", "run_log.jsonl")


def load_batch(path):
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            data = data.get("rows", [])
        return [{k: ("" if v is None else str(v)) for k, v in r.items()} for r in data]
    _, rows = read_rows(path)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--canonical", default=CANON)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    header, existing = read_rows(a.canonical)
    if header[:len(COLUMNS)] != COLUMNS:
        header = list(COLUMNS) + [h for h in header if h not in COLUMNS]

    index = {}
    for n, r in enumerate(existing, start=2):
        for k in dedupe_keys(r):
            index.setdefault(k, n)

    before = {
        "rows": len(existing),
        "unique_keys": len(index),
        "email_bearing": sum(1 for r in existing if (r.get("email") or "").strip()),
        "ready": sum(1 for r in existing
                     if (r.get("personalization_status") or "").strip() == "Ready"),
    }

    batch = load_batch(a.batch)
    added, skipped, rejected, merged_emails = [], [], [], []

    for r in batch:
        row = {c: (r.get(c) or "").strip() for c in COLUMNS}

        # contract checks -- a bad row never enters the canonical file
        why = None
        if not row["author_name"]:
            why = "no author_name"
        elif not row["email"]:
            why = "no email"
        elif row["research_confidence"] not in CONFIDENCE:
            why = f"bad research_confidence {row['research_confidence']!r}"
        elif row["personalization_status"] not in STATUS:
            why = f"bad personalization_status {row['personalization_status']!r}"
        elif row["research_confidence"] == "Low" and row["personalization_status"] == "Ready":
            why = "Low confidence cannot be Ready"
        elif row["personalization_status"] == "Ready" and not all(
                row[c] for c in COPY_COLUMNS):
            why = "Ready with incomplete email copy"
        elif row["personalization_status"] != "Ready" and any(
                row[c] for c in COPY_COLUMNS):
            why = "non-Ready row carries email copy"
        if why:
            rejected.append((row.get("author_name") or row.get("email"), why))
            continue

        row["send_status"] = row["send_status"] or "Not Sent"

        keys = dedupe_keys(row)
        hit = next((k for k in keys if k in index), None)
        if hit:
            # Same author, new public address -> fold into the existing row.
            target = existing[index[hit] - 2]
            have = {norm_email(e) for e in split_multi(target.get("email"))}
            new = [e for e in split_multi(row["email"]) if norm_email(e) not in have]
            if new:
                target["email"] = MULTI.join(split_multi(target.get("email")) + new)
                merged_emails.append((target.get("author_name"), new))
                for k in dedupe_keys(target):
                    index.setdefault(k, index[hit])
            skipped.append((row["author_name"], f"{hit[0]} match -> row {index[hit]}"))
            continue

        existing.append(row)
        n = len(existing) + 1
        for k in keys:
            index.setdefault(k, n)
        added.append(row["author_name"])

    after = {
        "rows": len(existing),
        "unique_keys": len(index),
        "email_bearing": sum(1 for r in existing if (r.get("email") or "").strip()),
        "ready": sum(1 for r in existing
                     if (r.get("personalization_status") or "").strip() == "Ready"),
    }

    print(f"batch           {os.path.basename(a.batch)}  ({len(batch)} row(s))")
    print(f"rows            {before['rows']} -> {after['rows']}")
    print(f"unique keys     {before['unique_keys']} -> {after['unique_keys']}")
    print(f"email-bearing   {before['email_bearing']} -> {after['email_bearing']}")
    print(f"Ready           {before['ready']} -> {after['ready']}")
    print(f"added           {len(added)}")
    print(f"skipped (dupe)  {len(skipped)}")
    print(f"rejected        {len(rejected)}")
    for nm, w in rejected:
        print(f"   REJECT  {nm}: {w}")
    for nm, new in merged_emails:
        print(f"   MERGED EMAIL  {nm}: +{', '.join(new)}")

    if a.dry_run:
        print("dry-run: nothing written")
        return 0

    if not added and not merged_emails:
        print("no changes: canonical file left untouched")
        return 0

    b = backup(a.canonical, BACKUPS)
    if b:
        print(f"backup          {os.path.relpath(b, ROOT)}")
    write_rows(a.canonical, header, existing)
    print(f"wrote           {os.path.relpath(a.canonical, ROOT)} (atomic)")

    os.makedirs(os.path.dirname(RUNLOG), exist_ok=True)
    with open(RUNLOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": now_stamp(), "run_id": a.run_id,
            "batch": os.path.basename(a.batch),
            "added": len(added), "skipped": len(skipped),
            "rejected": [{"who": n, "why": w} for n, w in rejected],
            "before": before, "after": after,
        }) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
