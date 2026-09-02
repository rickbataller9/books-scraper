import hashlib
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

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

#.product_pod
#   - h3 a
#   - .product_price .price_color
#   - .star-rating

def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    books = []

    for pod in soup.select(".product_pod"):
        books.append({
            "title": pod.select_one("h3 a")["title"],
            "price": pod.select_one(".price_color").text,
            "rating": pod.select_one(".star-rating")["class"],
            "stock": pod.select_one(".instock.availability").text,
            "url": pod.select_one("h3 a")["href"],
        })

    return books