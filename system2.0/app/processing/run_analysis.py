import json
from app.processing.analysis import analyze_clusters


def load_clusters():
    with open("clustered_events.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved → {path}")


def main():

    print("🚀 STEP 3: ANALYSIS STARTED")

    clusters = load_clusters()

    analyzed = analyze_clusters(clusters)

    save_output(analyzed, "analyzed_clusters.json")

    print(f"\n📊 Total analyzed clusters: {len(analyzed)}")


if __name__ == "__main__":
    main()