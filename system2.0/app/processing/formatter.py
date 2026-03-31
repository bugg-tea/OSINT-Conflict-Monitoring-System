from datetime import datetime
from langdetect import detect, LangDetectException


def detect_language(text):
    """
    Detect language of text
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def merge_ocr_text(ocr_input):
    """
    Accept both string or list safely
    """

    if not ocr_input:
        return ""

    # 🔴 If already string → return directly
    if isinstance(ocr_input, str):
        return ocr_input

    # 🔴 If list → merge
    if isinstance(ocr_input, list):
        valid_texts = []
        for t in ocr_input:
            if isinstance(t, str) and not t.startswith("OCR ERROR"):
                valid_texts.append(t.strip())
        return " ".join(valid_texts)

    return ""


def build_output(
    title,
    clean_text,
    tables,
    ocr_texts,
    source_url
):
    """
    Final structured output builder
    """

    # 🔴 Merge OCR texts
    merged_ocr = merge_ocr_text(ocr_texts)

    # 🔴 Detect language (use main text)
    language = detect_language(clean_text if clean_text else "")

    # 🔴 Timestamp
    timestamp = datetime.utcnow().isoformat()

    # 🔴 Final structured output
    output = {
        "title": title,
        "clean_text": clean_text,
        "tables": tables if tables else [],
        "ocr_text": merged_ocr,
        "source": source_url,
        "timestamp": timestamp,
        "language": language,

        # 🔥 Extra intelligence (VERY IMPORTANT)
        "num_images": len(ocr_texts) if ocr_texts else 0,
        "num_tables": len(tables) if tables else 0
    }

    return output