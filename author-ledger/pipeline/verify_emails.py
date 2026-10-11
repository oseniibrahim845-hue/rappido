"""Re-fetch each row's email_source and confirm the email (or an obfuscated form) is printed there.
Writes email_check.json: {email: "found" | "not_found" | "fetch_error:<msg>"}. Cached across runs."""
import glob, html, json, os, re, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, "email_check.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def fetch(url):
    p = subprocess.run(["curl", "-sSL", "--max-time", "25", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", url],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode(errors="ignore")[:80])
    return p.stdout.decode("utf-8", errors="ignore")


def cf_decode(hexs):
    k = int(hexs[:2], 16)
    return "".join(chr(int(hexs[i:i + 2], 16) ^ k) for i in range(2, len(hexs), 2))


def present(email, page):
    t = html.unescape(urllib.parse.unquote(page)).lower()
    if email in t:
        return True
    for h in re.findall(r'data-cfemail="([0-9a-f]+)"', page) + re.findall(r'/cdn-cgi/l/email-protection#([0-9a-f]+)', page):
        try:
            if cf_decode(h).lower() == email:
                return True
        except Exception:
            pass
    local, dom = email.split("@")
    flat = re.sub(r"\s+", " ", t)
    pat = re.escape(local) + r"\s*[\(\[\{]?\s*(at|@|ät|arroba|chez)\s*[\)\]\}]?\s*" + \
        r"\s*[\(\[\{]?\s*(dot|\.|punkt|punto|ponto|point)\s*[\)\]\}]?\s*".join(re.escape(x) for x in dom.split("."))
    return re.search(pat, flat) is not None


def check(item):
    email, src = item
    try:
        return email, ("found" if present(email, fetch(src)) else "not_found")
    except Exception as e:
        return email, f"fetch_error:{e}"


items = {}
for path in glob.glob(os.path.join(BASE, "..", "raw", "*.jsonl")):
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        e = (r.get("email") or "").strip().lower()
        if e and r.get("email_source") and cache.get(e) != "found":
            items[e] = r["email_source"]
with ThreadPoolExecutor(12) as ex:
    for e, res in ex.map(check, items.items()):
        cache[e] = res
json.dump(cache, open(CACHE, "w"), indent=1)
from collections import Counter
print(Counter(v.split(":")[0] for v in cache.values()))
