import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # consistent results


# -------------------------
# LANGUAGE FILTER
# -------------------------
def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False


# -------------------------
# BASIC TEXT QUALITY CHECK
# -------------------------
def is_clean_text(text):
    if not text:
        return False

    words = text.split()

    # Too short → useless
    if len(words) < 50:
        return False

    # Too many symbols → garbage
    symbol_ratio = len(re.findall(r"[^\w\s]", text)) / len(text)
    if symbol_ratio > 0.3:
        return False

    return True


# -------------------------
# REMOVE DUPLICATES
# -------------------------
def remove_duplicates(data):
    seen = set()
    cleaned = []

    for item in data:
        text = item.get("clean_text", "")

        key = text[:200]  # first 200 chars as fingerprint

        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


# -------------------------
# MAIN CLEAN FUNCTION
# -------------------------
def clean_outputs(data):

    filtered = []

    for item in data:

        text = item.get("clean_text", "")

        # 1. Language filter
        if not is_english(text):
            continue

        # 2. Quality filter
        if not is_clean_text(text):
            continue

        filtered.append(item)

    # 3. Remove duplicates
    filtered = remove_duplicates(filtered)

    return filtered