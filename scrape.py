import hashlib
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

CACHE = Path("cache")
CACHE.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (learning project)"}
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


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

def parse_page(html, base_url):
    pods = BeautifulSoup(html, "lxml")
    books = []

    for pod in pods.select(".product_pod"):
        books.append({
            "title": pod.select_one("h3 a")["title"],
            "rating": RATINGS.get(pod.select_one(".star-rating")["class"][-1]),
            "price": float(pod.select_one(".price_color").text.replace("£", "").replace(",", "")),
            "stock": 'In stock' in pod.select_one(".instock.availability").text.strip(),
            "url": urljoin(base_url, pod.select_one("h3 a")["href"])
        })

    return books


def find_next(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    link = soup.select_one(".next a")
    if link is None:
        return None
    return urljoin(base_url, link["href"])

url = "https://books.toscrape.com/"
allBooks = []
while url:
    page = get(url)
    allBooks.extend(parse_page(page, url))
    url = find_next(page, url)

def write_csv(books, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "rating", "price", "stock", "url"])
        w.writeheader()
        w.writerows(books)

print(len(allBooks))
write_csv(allBooks, "books.csv")
