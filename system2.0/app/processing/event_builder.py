import uuid
from datetime import datetime

def compute_confidence(num_sources, agreement_score):

    return min(1.0, (num_sources * 0.1) + agreement_score)


def compute_severity(event_type):

    severity_map = {
        "war": 0.95,
        "attack": 0.9,
        "explosion": 0.9,
        "political": 0.5,
        "economic": 0.6
    }

    return severity_map.get(event_type, 0.5)


def build_event(cluster_id, cluster_chunks, entities, summary, source_info):

    return {
        "event_id": str(uuid.uuid4()),
        "cluster_id": cluster_id,

        "event_datetime_utc": summary.get("date"),
        "event_type": summary.get("event_type"),

        "event_summary": summary.get("event_summary"),

        "actors": summary.get("actors", []),

        "location": entities.get("location"),
        "organizations": entities.get("organizations"),
        "persons": entities.get("persons"),

        "sources": source_info,

        "confidence_score": compute_confidence(len(cluster_chunks), 0.8),

        "severity_score": compute_severity(summary.get("event_type")),

        "tags": [],
        "last_updated_at": datetime.utcnow().isoformat()
    }