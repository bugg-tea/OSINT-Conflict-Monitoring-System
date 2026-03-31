import requests
from bs4 import BeautifulSoup
import pdfplumber
from PIL import Image
from io import BytesIO
import re
import time
import feedparser
from playwright.sync_api import sync_playwright

from app.processing.fusion import fuse_content
from app.processing.image_analysis import analyze_image
from app.processing.cleaner import clean_text_advanced as clean_final_text
from app.processing.table_extractor import extract_tables_from_html
from app.ingestion.link_extractor import extract_article_links


# ---------------------------
# HEADERS
# ---------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}


# ---------------------------
# KEYWORD FILTER (Iran Conflict)
# ---------------------------
KEYWORDS = [
    "iran", "us", "usa", "united states", "israel",
    "war", "conflict", "strike", "military",
    "middle east", "tension", "attack"
]


def is_relevant(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)


# ---------------------------
# GDELT
# ---------------------------
def fetch_gdelt():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    queries = [
        "iran us conflict",
        "iran war",
        "iran israel tension",
        "middle east iran crisis",
        "us iran military"
    ]

    articles = []

    for q in queries:
        for _ in range(3):
            try:
                res = requests.get(
                    url,
                    params={
                        "query": q,
                        "mode": "ArtList",
                        "maxrecords": 20,
                        "format": "json"
                    },
                    headers=HEADERS,
                    timeout=30
                )

                if res.status_code != 200:
                    continue

                data = res.json()

                for a in data.get("articles", []):
                    if is_relevant(a.get("title", "")):
                        articles.append({
                            "title": a.get("title"),
                            "url": a.get("url"),
                            "source": "GDELT"
                        })

                break

            except:
                time.sleep(2)

    return articles


# ---------------------------
# REUTERS
# ---------------------------
def fetch_reuters_rss():
    feed = feedparser.parse("https://feeds.reuters.com/reuters/topNews")

    return [
        {
            "title": e.title,
            "url": e.link,
            "source": "Reuters"
        }
        for e in feed.entries[:40]
        if is_relevant(e.title)
    ]


# ---------------------------
# AL JAZEERA
# ---------------------------
def fetch_aljazeera_rss():
    feed = feedparser.parse("https://www.aljazeera.com/xml/rss/all.xml")

    return [
        {
            "title": e.title,
            "url": e.link,
            "source": "AlJazeera"
        }
        for e in feed.entries[:40]
        if is_relevant(e.title)
    ]


# ---------------------------
# GUARDIAN (UNCHANGED)
# ---------------------------
def fetch_guardian_rss():
    feed = feedparser.parse("https://www.theguardian.com/world/rss")

    return [
        {
            "title": e.title,
            "url": e.link,
            "source": "Guardian"
        }
        for e in feed.entries[:40]
        if is_relevant(e.title)
    ]


# ---------------------------
# BBC (ADDED - NOT REMOVING ANYTHING)
# ---------------------------
def fetch_bbc():
    feed = feedparser.parse("http://feeds.bbci.co.uk/news/rss.xml")

    return [
        {
            "title": e.title,
            "url": e.link,
            "source": "BBC"
        }
        for e in feed.entries[:40]
        if is_relevant(e.title)
    ]


# ---------------------------
# BROWSER FETCH
# ---------------------------
def fetch_html_browser(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            html = page.content()
            browser.close()

            return html
    except:
        return None


# ---------------------------
# IMAGE EXTRACTION
# ---------------------------
def extract_image_urls(html):
    soup = BeautifulSoup(html, "html.parser")

    images = []

    for img in soup.find_all("img"):
        src = img.get("src")

        if not src:
            continue

        if not src.startswith("http"):
            src = "https:" + src

        if any(x in src.lower() for x in ["logo", "icon"]):
            continue

        images.append(src)

    return list(set(images))


# ---------------------------
# CLEAN TEXT
# ---------------------------
def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)
    return re.sub(r"\n+", "\n", text).strip()


# ---------------------------
# HTML FETCH
# ---------------------------
def fetch_html(url):

    time.sleep(1)

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        html = res.text

        if len(html) < 5000:
            html = fetch_html_browser(url)

    except:
        html = fetch_html_browser(url)

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = clean_text(soup.get_text(separator="\n"))

    if not is_relevant(text):
        return None

    tables = extract_tables_from_html(str(soup))
    images = extract_image_urls(html)

    ocr_texts = []

    for img in images[:2]:
        try:
            analysis = analyze_image(img)
            if analysis["final"]["type"] == "OCR":
                ocr_texts.append(analysis["ocr"])
        except:
            continue

    fused = fuse_content(
        main_text=text[:2000],
        tables=tables,
        ocr_text="\n".join(ocr_texts),
        captions=[]
    )

    fused = clean_final_text(fused)

    return {
        "type": "html",
        "title": soup.title.string if soup.title else None,
        "content": fused,
        "tables": tables,
        "images": images[:5]
    }


# ---------------------------
# PDF FETCH
# ---------------------------
def fetch_pdf(url):
    res = requests.get(url, headers=HEADERS, timeout=10)

    text = ""

    with pdfplumber.open(BytesIO(res.content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not is_relevant(text):
        return None

    return {
        "type": "pdf",
        "text": clean_text(text),
        "url": url
    }


# ---------------------------
# IMAGE FETCH
# ---------------------------
def fetch_image(url):
    res = requests.get(url, headers=HEADERS, timeout=10)

    return {
        "type": "image",
        "image": Image.open(BytesIO(res.content)),
        "url": url
    }


# ---------------------------
# ROUTER
# ---------------------------
def fetch_url(url):

    if url.endswith(".pdf"):
        return fetch_pdf(url)

    if url.endswith((".jpg", ".jpeg", ".png")):
        return fetch_image(url)

    return fetch_html(url)

