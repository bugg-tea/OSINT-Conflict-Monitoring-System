import re
from transformers import pipeline

# Load NER model once
ner = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"  # replaces grouped_entities
)


# ---------------- TEXT PROCESSING ----------------

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


# ---------------- FILTERING ----------------

def is_valid_sentence(sent):
    noise_keywords = [
        "image", "caption", "bbc news", "click here",
        "advertisement", "subscribe"
    ]

    text = sent.lower()

    if any(word in text for word in noise_keywords):
        return False

    return len(sent.split()) > 4


# ---------------- SCORING ----------------

def score_sentence(sentence):
    score = 0
    text = sentence.lower()

    event_keywords = [
        "attack", "killed", "arrest", "strike", "explosion",
        "war", "violence", "threat", "closed", "expelled",
        "clash", "bomb", "shoot", "raid", "protest",
        "conflict", "destroy", "damage"
    ]

    for word in event_keywords:
        if word in text:
            score += 2

    # Entity presence boosts score
    entities = ner(sentence)
    score += len(entities)

    # Multiple clauses suggest multiple actions
    score += text.count("and") * 0.5

    return score


# ---------------- NER ----------------

def extract_entities(sentence):
    entities = ner(sentence)

    results = []
    for e in entities:
        results.append({
            "entity": e["word"],
            "type": e["entity_group"]
        })

    return results


# ---------------- EVENT BUILDING ----------------

def build_event(article, sentence, entities, score):

    actors = []
    locations = []

    for e in entities:
        if e["type"] in ["PER", "ORG"]:
            actors.append(e["entity"])
        elif e["type"] == "LOC":
            locations.append(e["entity"])

    return {
        "event_datetime_utc": article.get("timestamp"),
        "source_name": article.get("source", "Unknown"),
        "source_url": article.get("url", ""),
        "source_type": "news",

        "claim_text": sentence,

        "event_type": infer_event_type(sentence),

        "actors": actors,
        "locations": locations,

        "primary_actor": actors[0] if actors else None,
        "primary_location": locations[0] if locations else None,

        "severity_score": score,
        "confidence_score": min(1.0, score / 10),

        "entities": entities,

        "tags": extract_tags(sentence)
    }


# ---------------- EVENT CLASSIFICATION ----------------

def infer_event_type(text):
    text = text.lower()

    if any(k in text for k in ["attack", "clash", "war", "strike"]):
        return "conflict"
    if any(k in text for k in ["killed", "death", "murder"]):
        return "violence"
    if "arrest" in text:
        return "law_enforcement"
    if "election" in text:
        return "politics"
    if any(k in text for k in ["expel", "diplomat"]):
        return "diplomacy"

    return "general"


def extract_tags(text):
    keywords = ["war", "attack", "arrest", "explosion", "protest"]
    return [k for k in keywords if k in text.lower()]


# ---------------- DEDUPLICATION ----------------

def deduplicate(events):
    seen = set()
    unique_events = []

    for e in events:
        key = (e["claim_text"][:100], tuple(e["actors"]))

        if key in seen:
            continue

        seen.add(key)
        unique_events.append(e)

    return unique_events


# ---------------- MAIN FUNCTION ----------------

def extract_events_from_article(article):

    text = clean_text(article.get("clean_text", ""))
    sentences = split_sentences(text)

    events = []

    for sent in sentences:

        if not is_valid_sentence(sent):
            continue

        score = score_sentence(sent)

        # 🔥 dynamic threshold
        if score < 1.5:
            continue

        entities = extract_entities(sent)

        event = build_event(article, sent, entities, score)

        events.append(event)

    # 🔥 remove duplicates inside article
    events = deduplicate(events)

    return events