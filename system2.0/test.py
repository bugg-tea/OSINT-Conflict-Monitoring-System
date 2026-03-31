from app.ingestion.fetcher import fetch_url
from app.processing.image_analysis import analyze_image
from app.processing.fusion import fuse_content
from app.processing.cleaner import clean_text_advanced
from app.processing.formatter import build_output

import json

# 🔴 Input URL
url = "https://www.bbc.com/news"

# ---------------- FETCH ----------------
result = fetch_url(url)

title = result.get("title")
text = result.get("content")
tables = result.get("tables", [])
images = result.get("images", [])

print("\n===== PAGE TITLE =====")
print(title)

# ---------------- IMAGE ANALYSIS ----------------
ocr_texts = []

for i, img_url in enumerate(images):
    print(f"\nImage {i+1}: {img_url}")

    analysis = analyze_image(img_url)

    # 🔴 Take ONLY final selected text
    final_text = analysis["final"]["text"]
    ocr_texts.append(final_text)

# ---------------- FUSION ----------------
# ---------------- OCR MERGE (FIX) ----------------
valid_ocr = []

for t in ocr_texts:
    if not t:
        continue
    if isinstance(t, str) and not t.startswith("OCR ERROR"):
        valid_ocr.append(t.strip())

# 🔴 Convert list → single string
ocr_combined = " ".join(valid_ocr)

# ---------------- FUSION ----------------
fused = fuse_content(text, tables, ocr_combined)

# ---------------- CLEANING ----------------
cleaned = clean_text_advanced(fused)

# ---------------- FINAL OUTPUT ----------------
final_output = build_output(
    title=title,
    clean_text=cleaned,
    tables=tables,
    ocr_texts=ocr_texts,
    source_url=url
)

# ---------------- PRINT ----------------
print("\n===== FINAL STRUCTURED OUTPUT =====\n")
print(json.dumps(final_output, indent=4))