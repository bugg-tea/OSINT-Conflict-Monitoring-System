import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from collections import defaultdict

# Load model once (local caching recommended)
model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder="./models")

# ---------------- TEXT PREPROCESSING ----------------

def truncate_text(text, max_words=300):
    if not isinstance(text, str):
        return ""
    
    words = text.split()
    return " ".join(words[:max_words])


def safe_join(items):
    return " ".join([str(i) for i in items if i])


def get_event_text(event):
    """
    Create a rich representation of the event for better clustering
    """
    claim = truncate_text(event.get("claim_text", ""))

    actors = safe_join(event.get("actors", []))
    locations = safe_join(event.get("locations", []))
    event_type = event.get("event_type", "")

    combined = f"{claim} {actors} {locations} {event_type}"

    return combined.strip()


# ---------------- EMBEDDING ----------------

def generate_embeddings(events):
    texts = [get_event_text(e) for e in events]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


# ---------------- CLUSTERING ----------------

def cluster_events(embeddings):

    clustering = DBSCAN(
        eps=0.5,          # improved threshold (tune if needed)
        min_samples=2,
        metric="cosine"
    )

    labels = clustering.fit_predict(embeddings)

    clusters = defaultdict(list)

    for idx, label in enumerate(labels):
        if label == -1:
            continue  # ignore noise

        clusters[label].append(idx)

    print(f"🔢 Clusters formed: {len(clusters)}")

    return clusters, labels


# ---------------- MERGING ----------------

def merge_cluster(events, indices):

    merged = {
        "cluster_size": len(indices),
        "event_texts": [],
        "actors": set(),
        "locations": set(),
        "event_types": set(),
        "sources": set(),
        "timestamps": []
    }

    for i in indices:
        e = events[i]

        # text
        merged["event_texts"].append(e.get("claim_text", ""))

        # actors
        for a in e.get("actors", []):
            if a:
                merged["actors"].add(a)

        # locations
        for l in e.get("locations", []):
            if l:
                merged["locations"].add(l)

        # event type
        if e.get("event_type"):
            merged["event_types"].add(e.get("event_type"))

        # sources
        if e.get("source_name"):
            merged["sources"].add(e.get("source_name"))

        # timestamps
        if e.get("event_datetime_utc"):
            merged["timestamps"].append(e["event_datetime_utc"])

    # convert sets → list
    merged["actors"] = list(merged["actors"])
    merged["locations"] = list(merged["locations"])
    merged["event_types"] = list(merged["event_types"])
    merged["sources"] = list(merged["sources"])

    return merged


# ---------------- MAIN PIPELINE ----------------

def cluster_and_merge(events):

    if not events:
        return []

    print("🚀 Generating embeddings...")
    embeddings = generate_embeddings(events)

    print("🚀 Running DBSCAN clustering...")
    clusters, labels = cluster_events(embeddings)

    clustered_events = []

    for cluster_id, indices in clusters.items():

        merged = merge_cluster(events, indices)

        clustered_events.append({
            "cluster_id": int(cluster_id),
            "merged_event": merged,
            "original_event_indices": [int(i) for i in indices]
        })

    return clustered_events