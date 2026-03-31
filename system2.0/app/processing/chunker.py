import re


# -------------------------
# 🔴 CLEAN + SPLIT SENTENCES
# -------------------------
def split_sentences(text):
    if not text:
        return []

    # Normalize
    text = text.replace("\n", " ")

    # Basic sentence split
    sentences = re.split(r'(?<=[.!?]) +', text)

    # Remove noise
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    return sentences


# -------------------------
# 🔴 SLIDING WINDOW CHUNKING
# -------------------------
def chunk_text(
    text,
    max_tokens=250,
    overlap=50
):
    """
    Advanced chunking:
    - sentence aware
    - sliding window
    - overlap for context preservation
    """

    sentences = split_sentences(text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_len = len(sent.split())

        # If adding sentence exceeds limit → finalize chunk
        if current_length + sent_len > max_tokens:

            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)

            # 🔥 SLIDING WINDOW (IMPORTANT)
            overlap_words = chunk_text.split()[-overlap:]

            current_chunk = [" ".join(overlap_words), sent]
            current_length = len(overlap_words) + sent_len

        else:
            current_chunk.append(sent)
            current_length += sent_len

    # Add last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# -------------------------
# 🔴 OPTIONAL: EVENT-FOCUSED FILTER
# -------------------------
def filter_event_chunks(chunks):
    """
    Keep only meaningful chunks (event-like)
    """

    keywords = [
        "killed", "attack", "war", "military",
        "strike", "conflict", "protest",
        "government", "forces", "explosion"
    ]

    filtered = []

    for chunk in chunks:
        text = chunk.lower()

        if any(k in text for k in keywords):
            filtered.append(chunk)

    return filtered