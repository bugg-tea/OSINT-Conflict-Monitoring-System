# app/processing/fusion.py

def fuse_content(main_text=None, tables=None, ocr_text=None, captions=None):
    """
    Combine all extracted data into a single clean text block
    """

    combined_parts = []

    # -------------------------
    # 1. MAIN TEXT
    # -------------------------
    if main_text:
        combined_parts.append(main_text)

    # -------------------------
    # 2. TABLES
    # -------------------------
    if tables:
        for table in tables:
            try:
                combined_parts.append("\n[TABLE DATA]")
                combined_parts.append(str(table))
            except:
                continue

    # -------------------------
    # 3. OCR TEXT
    # -------------------------
    if ocr_text:
        if not ocr_text.startswith("OCR ERROR"):
            combined_parts.append("\n[OCR TEXT]")
            combined_parts.append(ocr_text)

    # -------------------------
    # 4. IMAGE CAPTIONS (optional but useful)
    # -------------------------
    if captions:
        combined_parts.append("\n[IMAGE CAPTIONS]")
        for cap in captions:
            combined_parts.append(cap)

    # -------------------------
    # FINAL CLEAN JOIN
    # -------------------------
    fused_content = "\n".join(combined_parts)

    return fused_content.strip()