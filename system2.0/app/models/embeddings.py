from sentence_transformers import SentenceTransformer
import numpy as np
import torch

# -------------------------
# 🔴 LOAD MODEL (GLOBAL)
# -------------------------
print("🚀 Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# Optional: use GPU if available
if torch.cuda.is_available():
    model = model.to("cuda")
    print("⚡ Using GPU")
else:
    print("🖥️ Using CPU")


# -------------------------
# 🔴 SINGLE EMBEDDING
# -------------------------
def get_embedding(text):
    if not text:
        return None

    embedding = model.encode(
        text,
        normalize_embeddings=True  # 🔥 IMPORTANT (cosine similarity ready)
    )

    return embedding


# -------------------------
# 🔴 BATCH EMBEDDINGS (VERY IMPORTANT)
# -------------------------
def get_embeddings_batch(texts, batch_size=32):
    """
    Efficient batch embedding (USE THIS in pipeline)
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings


# -------------------------
# 🔴 SIMILARITY FUNCTION
# -------------------------
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2)


# -------------------------
# 🔴 TOP-K SIMILAR
# -------------------------
def find_most_similar(query_embedding, embeddings, top_k=5):

    scores = []

    for idx, emb in enumerate(embeddings):
        score = cosine_similarity(query_embedding, emb)
        scores.append((idx, score))

    # Sort descending
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return scores[:top_k]