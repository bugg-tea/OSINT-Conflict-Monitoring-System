from bs4 import BeautifulSoup

def extract_article_links(html, base_url="https://www.bbc.com"):
    """
    Extract article links from homepage
    """

    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Convert relative → absolute
        if href.startswith("/"):
            href = base_url + href

        # 🔴 Filter only news articles
        if "/news/" in href:
            links.add(href)

    return list(links)