import json
import numpy as np
from app.processing.clustering import cluster_and_merge


# ---------------- JSON SAFE CONVERTER ----------------

def convert_to_serializable(obj):

    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]

    elif isinstance(obj, (np.integer,)):
        return int(obj)

    elif isinstance(obj, (np.floating,)):
        return float(obj)

    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    return obj


# ---------------- LOAD EVENTS ----------------

def load_events():
    with open("output.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------- SAVE OUTPUT ----------------

def save_output(data, path):
    data = convert_to_serializable(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved → {path}")


# ---------------- MAIN ----------------

def main():

    print("🚀 STEP 2: CLUSTERING STARTED")

    events = load_events()

    print(f"📊 Total events loaded: {len(events)}")

    clustered = cluster_and_merge(events)

    save_output(clustered, "clustered_events.json")

    print(f"\n🧠 Total clusters: {len(clustered)}")


if __name__ == "__main__":
    main()