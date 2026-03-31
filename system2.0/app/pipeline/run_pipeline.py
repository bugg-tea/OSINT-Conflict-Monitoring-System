import json
from app.ingestion.fetcher import (
    fetch_gdelt,
    fetch_reuters_rss,
    fetch_aljazeera_rss,
    fetch_guardian_rss,
    fetch_bbc,              # ✅ IMPORTANT (added, nothing removed)
    fetch_url
)

from app.processing.formatter import build_output


# -------------------------
# FILTER (MATCHING FETCHER LOGIC)
# -------------------------
KEYWORDS = [
    "iran", "us", "usa", "united states", "israel",
    "war", "conflict", "strike", "military",
    "middle east", "tension", "attack"
]


def is_relevant(article):
    text = (article.get("title") or "").lower()
    return any(k in text for k in KEYWORDS)


# -------------------------
# BALANCE SOURCES
# -------------------------
def balance_sources(articles, max_per_source=40):

    counts = {}
    result = []

    for a in articles:
        src = a.get("source", "Unknown")

        counts.setdefault(src, 0)

        if counts[src] < max_per_source:
            result.append(a)
            counts[src] += 1

    return result


# -------------------------
# PIPELINE
# -------------------------
def run_pipeline():

    print("\n🚀 Fetching sources...")

    # ✅ FETCH (UNCHANGED + BBC ADDED)
    articles = (
        fetch_gdelt() +
        fetch_reuters_rss() +
        fetch_aljazeera_rss() +
        fetch_guardian_rss() +
        fetch_bbc()   # ✅ ADDED, NOTHING REMOVED
    )

    print("📊 Total fetched:", len(articles))

    # ✅ FILTER
    articles = [a for a in articles if is_relevant(a)]
    print("🎯 After filtering:", len(articles))

    # ✅ BALANCE
    articles = balance_sources(articles)
    print("⚖️ After balancing:", len(articles))

    final_outputs = []
    failed = []

    for i, art in enumerate(articles[:120]):

        url = art.get("url")

        if not url:
            continue

        print(f"\n[{i}] Processing:", url)

        try:
            data = fetch_url(url)

            # Skip non-HTML (you can extend later if needed)
            if not data or data.get("type") != "html":
                continue

            if len(data.get("content", "")) < 200:
                continue

            output = build_output(
                title=data.get("title"),
                clean_text=data.get("content"),
                tables=data.get("tables"),
                ocr_texts=data.get("content"),
                source_url=url
            )

            output["source"] = art.get("source")

            final_outputs.append(output)

        except Exception as e:
            print("❌ Error:", e)
            failed.append(url)

    print("\n🧹 Final cleaning...")

    final_outputs = [
        o for o in final_outputs if len(o.get("clean_text", "")) > 150
    ]

    # Save outputs
    with open("final_output.json", "w", encoding="utf-8") as f:
        json.dump(final_outputs, f, indent=2)

    with open("failed.json", "w", encoding="utf-8") as f:
        json.dump(failed, f, indent=2)

    print("\n✅ DONE")
    print("Final articles:", len(final_outputs))
    print("Failed:", len(failed))


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    run_pipeline()