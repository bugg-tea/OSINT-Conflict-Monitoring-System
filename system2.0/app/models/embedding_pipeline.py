import json
import numpy as np
from app.models.embeddings import get_embeddings_batch


def run_embedding_pipeline(
    input_file="chunks.json",
    output_file="embeddings.npz"
):

    print("\n🚀 Starting embedding pipeline...")

    # -------------------------
    # LOAD CHUNKS
    # -------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"📄 Chunks loaded: {len(chunks)}")

    texts = [c["text"] for c in chunks]

    # -------------------------
    # GENERATE EMBEDDINGS
    # -------------------------
    embeddings = get_embeddings_batch(texts)

    embeddings = np.array(embeddings)

    print(f"✅ Embeddings shape: {embeddings.shape}")

    # -------------------------
    # SAVE
    # -------------------------
    np.savez(
        output_file,
        embeddings=embeddings
    )

    print(f"\n💾 Saved embeddings to {output_file}")


if __name__ == "__main__":
    run_embedding_pipeline()