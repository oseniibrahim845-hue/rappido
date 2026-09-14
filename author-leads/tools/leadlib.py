"""Shared helpers for the author-lead pipeline: schema, normalization, I/O."""
import csv, os, re, sys, unicodedata, tempfile, shutil
from datetime import datetime, timezone

COLUMNS = [
    "author_name", "email", "first_name", "book_title", "book_topic",
    "personalization_detail", "personalization_reason", "personalized_opening",
    "subject_line", "email_body", "research_sources", "research_confidence",
    "personalization_status", "send_status", "date_sent",
]
# Email copy: must be blank unless status == Ready, and complete when it is.
COPY_COLUMNS = ["personalized_opening", "subject_line", "email_body"]
# Audit trail: required on Ready, and encouraged on Needs Review / Excluded to
# record the open question or the exclusion reason next to the row.
NOTE_COLUMNS = ["personalization_detail", "personalization_reason"]

CONFIDENCE = {"High", "Medium", "Low"}
STATUS = {"Ready", "Needs Review", "Excluded"}
SEND_STATUS = {"Not Sent", "Queued", "Sent", "Bounced", "Replied",
               "Opted Out", "Do Not Contact"}
SHEET = "Pilot Batch"
MULTI = " ; "

TITLES = r"^(dr|mr|mrs|ms|miss|prof|professor|rev|sir|dame|fr)\.?\s+"
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
URL_RE = re.compile(r"https?://\S+")
# Obvious personal-phone / street-address leakage in free text
PHONE_RE = re.compile(r"(?:\+?61[\s\-]?\d[\s\-]?\d{4}[\s\-]?\d{4}"
                      r"|\b0[2-478][\s\-]?\d{4}[\s\-]?\d{4}\b"
                      r"|\b\(\d{3}\)\s?\d{3}-\d{4}\b"
                      r"|\b\d{3}-\d{3}-\d{4}\b)")
STREET_RE = re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+"
                       r"(Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Lane|Ln|Court|Ct|"
                       r"Parade|Pde|Crescent|Cres|Highway|Hwy|Terrace|Tce)\b")


def now_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def norm_text(s):
    """Fold case, accents, punctuation and spacing for dedupe comparison."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(TITLES, "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_email(e):
    """Lowercase; for Gmail, ignore dots and +tags (same mailbox)."""
    if not e:
        return ""
    e = str(e).strip().lower()
    if "@" not in e:
        return e
    local, _, domain = e.partition("@")
    local = local.split("+", 1)[0]
    if domain in ("gmail.com", "googlemail.com"):
        local = local.replace(".", "")
        domain = "gmail.com"
    return f"{local}@{domain}"


def split_multi(cell):
    if not cell:
        return []
    return [p.strip() for p in re.split(r"\s*;\s*", str(cell)) if p.strip()]


def amazon_ids(sources):
    """Extract Amazon author IDs / ASINs from source URLs for dedupe."""
    ids = set()
    for u in sources:
        for m in re.finditer(r"/(?:author|stores/author)/([A-Z0-9]{10})", u):
            ids.add(m.group(1))
        for m in re.finditer(r"/(?:dp|gp/product)/([A-Z0-9]{10})", u):
            ids.add(m.group(1))
    return ids


def dedupe_keys(row):
    """All keys that must not collide with an existing row."""
    keys = set()
    name = norm_text(row.get("author_name"))
    if name:
        keys.add(("name", name))
    for e in split_multi(row.get("email")):
        ne = norm_email(e)
        if ne:
            keys.add(("email", ne))
    srcs = split_multi(row.get("research_sources"))
    for aid in amazon_ids(srcs):
        keys.add(("amazon", aid))
    if name and norm_text(row.get("book_title")):
        keys.add(("name+book", name + "|" + norm_text(row.get("book_title"))))
    return keys


# ---------------------------------------------------------------- I/O

def read_rows(path):
    """Read canonical workbook or CSV -> (header, list[dict])."""
    if not os.path.exists(path):
        return list(COLUMNS), []
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb[SHEET] if SHEET in wb.sheetnames else wb.active
        data = list(ws.iter_rows(values_only=True))
        if not data:
            return list(COLUMNS), []
        header = [str(h) if h is not None else "" for h in data[0]]
        rows = []
        for r in data[1:]:
            if not any(c is not None and str(c).strip() for c in r):
                continue
            rows.append({header[i]: ("" if i >= len(r) or r[i] is None else str(r[i]))
                         for i in range(len(header))})
        return header, rows
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or COLUMNS), [
            {k: (v or "") for k, v in r.items()} for r in rd
            if any((v or "").strip() for v in r.values())
        ]


def write_rows(path, header, rows):
    """Atomic write; preserves the given header order exactly."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = SHEET
        ws.append(header)
        for r in rows:
            ws.append([r.get(h, "") for h in header])
        ws.freeze_panes = "A2"
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".xlsx")
        os.close(fd)
        wb.save(tmp)
    else:
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".csv")
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({h: r.get(h, "") for h in header})
    os.replace(tmp, path)


def backup(path, backup_dir):
    if not os.path.exists(path):
        return None
    os.makedirs(backup_dir, exist_ok=True)
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    dest = os.path.join(backup_dir, f"{stem}_{now_stamp()}{ext}")
    shutil.copy2(path, dest)
    return dest
