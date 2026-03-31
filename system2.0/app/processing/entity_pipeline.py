import re
import json
from transformers import pipeline

# -----------------------------
# NER MODEL (FAST + STABLE)
# -----------------------------
ner_model = pipeline(
    "ner",
    model="dslim/bert-large-NER",
    aggregation_strategy="simple"
)

# -----------------------------
# CLEANING
# -----------------------------
def clean(text):
    if not text:
        return None
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip() or None

# -----------------------------
# NER EXTRACTION
# -----------------------------
def extract_ner_entities(text):

    results = ner_model(text[:1000])  # LIMIT INPUT

    entities = {
        "persons": [],
        "organizations": [],
        "locations": []
    }

    for ent in results:
        word = clean(ent["word"])
        if not word:
            continue

        if ent["entity_group"] == "PER":
            entities["persons"].append(word)

        elif ent["entity_group"] == "ORG":
            entities["organizations"].append(word)

        elif ent["entity_group"] in ["LOC", "GPE"]:
            entities["locations"].append(word)

    return entities

# -----------------------------
# LLM ENTITY EXTRACTION
# -----------------------------
def llm_extract_entities(text, llm):

    prompt = f"""
Extract entities.

Return ONLY JSON:
{{
 "actors": [],
 "locations": [],
 "organizations": [],
 "events": []
}}

TEXT:
{text[:1200]}
"""

    response = llm(prompt)

    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        return json.loads(match.group()) if match else {}
    except:
        return {}

# -----------------------------
# FUSION
# -----------------------------
def fuse_entities(ner_entities, llm_entities):

    return {
        "actors": list(set(
            (llm_entities.get("actors") or []) + ner_entities["persons"]
        )),

        "location": (
            llm_entities.get("locations", [None])[0]
            or (ner_entities["locations"][0] if ner_entities["locations"] else None)
        ),

        "organizations": list(set(ner_entities["organizations"])),

        "persons": list(set(ner_entities["persons"]))
    }

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def extract_and_fuse_entities(text, llm):

    ner_entities = extract_ner_entities(text)

    llm_entities = llm_extract_entities(text, llm)

    return fuse_entities(ner_entities, llm_entities)