import trafilatura
from bs4 import BeautifulSoup
import re

def extract_main_text(html):
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        output_format="txt"
    )

    # 🔴 Fallback if trafilatura fails
    if not text:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Get all visible text
        text = soup.get_text(separator="\n")

    return text


def extract_metadata(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    title = None
    description = None

    if soup.title:
        title = soup.title.get_text(strip=True)

    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        description = meta_tag.get("content")

    # 🔴 Ensure consistent output (VERY IMPORTANT)
    return {
        "title": title,
        "description": description
    }
    
    
def extract_tables(html):
    """
    Extract tables from HTML (structured data)
    """
    soup = BeautifulSoup(html, "html.parser")
    tables_data = []

    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        table_rows = []

        for row in rows:
            cols = row.find_all(["td", "th"])
            cols_text = [col.get_text(strip=True) for col in cols]
            table_rows.append(cols_text)

        if table_rows:
            tables_data.append(table_rows)

    return tables_data


def extract_captions(html):
    """
    Extract image captions
    """
    soup = BeautifulSoup(html, "html.parser")

    captions = []

    for tag in soup.find_all(["figcaption", "caption"]):
        text = tag.get_text(strip=True)
        if text:
            captions.append(text)

    return captions


def clean_text(text):
    """
    Final cleaning layer
    """
    if not text:
        return None

    text = re.sub(r"\[\d+\]", "", text)  # remove references
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def parse_html(html):
    """
    Main parser pipeline
    """

    metadata = extract_metadata(html)

    title = metadata.get("title")
    description = metadata.get("description")

    main_text = extract_main_text(html)
    main_text = clean_text(main_text)

    tables = extract_tables(html)
    captions = extract_captions(html)

    
    return {
        "title": title,
        "description": description,
        "main_text": main_text,
        "tables": tables,
        "captions": captions
}