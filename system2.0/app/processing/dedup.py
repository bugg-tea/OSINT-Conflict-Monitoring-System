import numpy as np
import json
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity


def cluster_embeddings(embeddings):

    print("📊 Computing similarity matrix...")
    similarity = cosine_similarity(embeddings)

    # 🔴 Convert to distance
    distance_matrix = 1 - similarity

    # ✅ FIX: remove negative values
    distance_matrix = np.clip(distance_matrix, 0, None)

    print("🚀 Running DBSCAN clustering...")

    clustering = DBSCAN(
        eps=0.3,
        min_samples=2,
        metric="precomputed"
    )

    labels = clustering.fit_predict(distance_matrix)

    return labels


# -------------------------
# 🔴 GROUP BY CLUSTERS
# -------------------------
def group_clusters(chunks, labels):
    """
    Combine chunks into event clusters
    """

    cluster_map = {}

    for chunk, label in zip(chunks, labels):

        # -1 = noise (no cluster)
        if label == -1:
            continue

        if label not in cluster_map:
            cluster_map[label] = []

        cluster_map[label].append(chunk)

    return cluster_map


# -------------------------
# 🔴 BUILD EVENT STRUCTURE
# -------------------------
def build_events(cluster_map):
    """
    Convert clusters → structured events
    """

    events = []

    for cluster_id, items in cluster_map.items():

        texts = [i["text"] for i in items]
        sources = list(set(i["source"] for i in items))
        urls = list(set(i["url"] for i in items))

        event = {
            "event_id": f"event_{cluster_id}",
            "num_chunks": len(items),
            "sources": sources,
            "urls": urls,
            "summary_text": " ".join(texts[:3])  # simple merge (improve later)
        }

        events.append(event)

    return events


# -------------------------
# 🔴 MAIN PIPELINE
# -------------------------
def run_dedup_pipeline(
    chunks_file="chunks.json",
    embeddings_file="embeddings.npz",
    output_file="events.json"
):

    print("\n🚀 Starting deduplication pipeline...")

    # -------------------------
    # LOAD DATA
    # -------------------------
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    data = np.load(embeddings_file)
    embeddings = data["embeddings"]

    print(f"📄 Chunks: {len(chunks)}")
    print(f"📐 Embeddings: {embeddings.shape}")

    # -------------------------
    # CLUSTER
    # -------------------------
    labels = cluster_embeddings(embeddings)

    print(f"🔢 Unique clusters: {len(set(labels))}")

    # -------------------------
    # GROUP
    # -------------------------
    cluster_map = group_clusters(chunks, labels)

    print(f"📦 Valid clusters (no noise): {len(cluster_map)}")

    # -------------------------
    # BUILD EVENTS
    # -------------------------
    events = build_events(cluster_map)

    print(f"🧠 Events created: {len(events)}")

    # -------------------------
    # SAVE
    # -------------------------
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    print(f"\n✅ Saved events → {output_file}")


if __name__ == "__main__":
    run_dedup_pipeline()