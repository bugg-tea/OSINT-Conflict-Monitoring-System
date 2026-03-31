import easyocr
import requests
import numpy as np
import cv2
from PIL import Image
import torch

# 🔴 BLIP imports
from transformers import BlipProcessor, BlipForConditionalGeneration

# ---------------- OCR SETUP ----------------
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_url):
    try:
        resp = requests.get(image_url)
        img_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        result = reader.readtext(img)

        text = " ".join([r[1] for r in result])

        return text

    except Exception as e:
        return f"OCR ERROR: {str(e)}"


# ---------------- BLIP SETUP ----------------
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption_image(image_url):
    try:
        image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")

        inputs = processor(image, return_tensors="pt")

        with torch.no_grad():
            out = model.generate(**inputs)

        caption = processor.decode(out[0], skip_special_tokens=True)

        return caption

    except Exception as e:
        return f"BLIP ERROR: {str(e)}"


# ---------------- HYBRID LOGIC ----------------
def analyze_image(image_url):

    # Step 1: OCR
    ocr_text = extract_text_from_image(image_url)

    # Step 2: BLIP
    caption = caption_image(image_url)

    # Step 3: Decide what to use
    if ocr_text and not ocr_text.startswith("OCR ERROR") and len(ocr_text.strip()) > 5:
        result = {
            "type": "OCR",
            "text": ocr_text
        }
    else:
        result = {
            "type": "BLIP",
            "text": caption
        }

    return {
        "ocr": ocr_text,
        "caption": caption,
        "final": result
    }