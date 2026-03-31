import json
from app.processing.chunker import chunk_text, filter_event_chunks


def run_chunking_pipeline(
    input_file="final_output.json",
    output_file="chunks.json"
):

    print("\n🚀 Starting chunking pipeline...")

    # -------------------------
    # LOAD FINAL OUTPUT
    # -------------------------
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"📄 Articles loaded: {len(articles)}")

    all_chunks = []

    # -------------------------
    # PROCESS EACH ARTICLE
    # -------------------------
    for idx, article in enumerate(articles):

        text = article.get("clean_text", "")
        title = article.get("title", "")
        source = article.get("source", "")
        url = article.get("source_url", "")

        if not text:
            continue

        print(f"\n[{idx}] Chunking: {title[:60]}")

        # 🔴 STEP 1: CHUNK
        chunks = chunk_text(text)


        # 🔴 STEP 3: STRUCTURE EACH CHUNK
        for i, chunk in enumerate(chunks):

            chunk_obj = {
                "chunk_id": f"{idx}_{i}",
                "title": title,
                "source": source,
                "url": url,
                "text": chunk
            }

            all_chunks.append(chunk_obj)

    print(f"\n📊 Total chunks created: {len(all_chunks)}")

    # -------------------------
    # SAVE CHUNKS
    # -------------------------
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print("\n✅ Chunking DONE")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    run_chunking_pipeline()