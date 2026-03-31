import re
import unicodedata

def is_low_quality_sentence(s):
    """
    Filter out useless OCR/BLIP noise
    """

    # Too many generic words (image captions)
    generic_patterns = [
        "a man", "a woman", "a person", "a group",
        "sitting", "standing", "looking", "wearing",
        "in front of", "on the street", "at a table"
    ]

    for p in generic_patterns:
        if p in s.lower():
            return True

    # Too short / vague
    if len(s.split()) < 6:
        return True

    return False

def clean_text_advanced(text):
    if not text:
        return ""

    # -------------------------------
    # 1. Normalize encoding
    # -------------------------------
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8", "ignore")

    # -------------------------------
    # 2. Remove URLs
    # -------------------------------
    text = re.sub(r"http\S+|www\S+", "", text)

    # -------------------------------
    # 3. Remove unwanted symbols
    # -------------------------------
    text = re.sub(r"[^a-zA-Z0-9.,!?'\- ]", " ", text)

    # -------------------------------
    # 4. Fix spacing
    # -------------------------------
    text = re.sub(r"\s+", " ", text).strip()

    # -------------------------------
    # 5. Remove common noise phrases
    # -------------------------------
    noise_patterns = [
        r"bbc news.*?world",
        r"breaking news.*?",
        r"technology of business",
        r"artificial intelligence",
        r"culture experiences",
        r"sustainable business",
        r"ocr text"
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # -------------------------------
    # 6. Better sentence splitting
    # -------------------------------
    sentences = re.split(r'(?<=[.!?])\s+', text)

    clean_sentences = []

    for s in sentences:
        s = s.strip()

        # remove garbage / short lines
        if len(s) < 30:
            continue

        # remove lines with too many numbers (noise)
        if len(re.findall(r"\d", s)) > len(s) * 0.3:
            continue

        s = s.lower()

        if is_low_quality_sentence(s):
            continue

        clean_sentences.append(s)

    # -------------------------------
    # 7. Remove duplicates (order safe)
    # -------------------------------
    seen = set()
    unique_sentences = []

    for s in clean_sentences:
        if s not in seen:
            unique_sentences.append(s)
            seen.add(s)

    # -------------------------------
    # 8. Final join
    # -------------------------------
    final_text = " ".join(unique_sentences)

    return final_text