import hashlib
import time
import requests
from pathlib import Path

CACHE = Path("cache")
CACHE.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (learning project)"}


def get(url, delay=1.0):
    """Fetch a URL, or return it from cache if we've seen it before."""
    key = CACHE / (hashlib.md5(url.encode()).hexdigest() + ".html")

    if key.exists():
        return key.read_text(encoding="utf-8")

    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    r.encoding = "utf-8"

    key.write_text(r.text, encoding="utf-8")
    time.sleep(delay)
    return r.text