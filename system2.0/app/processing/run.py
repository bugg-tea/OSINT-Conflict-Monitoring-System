import json

from app.processing.event_extractor import extract_events_from_article


def load_articles():
    with open("final_output.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(events, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved → {path}")


def main():

    print("🚀 STEP 1 PIPELINE STARTED")

    articles = load_articles()

    all_events = []

    for article in articles:

        events = extract_events_from_article(article)

        all_events.extend(events)

    # 🔥 GLOBAL DEDUP (important)
    from app.processing.event_extractor import deduplicate
    all_events = deduplicate(all_events)

    save_output(all_events, "output.json")

    print(f"\n🧠 Total Events: {len(all_events)}")


if __name__ == "__main__":
    main()