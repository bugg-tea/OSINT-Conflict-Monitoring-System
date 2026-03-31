from collections import Counter
from datetime import datetime
import numpy as np


# ---------------- UTILS ----------------

def parse_time(ts):
    try:
        return datetime.fromisoformat(ts)
    except:
        return None


def get_all_timestamps(cluster):
    return [
        parse_time(t) for t in cluster["merged_event"].get("timestamps", [])
        if parse_time(t) is not None
    ]


# ---------------- TREND DETECTION ----------------

def detect_trend(timestamps):
    """
    Detect whether events are increasing over time
    """
    if len(timestamps) < 2:
        return "insufficient_data"

    timestamps = sorted(timestamps)

    mid = len(timestamps) // 2

    first_half = timestamps[:mid]
    second_half = timestamps[mid:]

    if len(first_half) == 0 or len(second_half) == 0:
        return "stable"

    first_rate = len(first_half)
    second_rate = len(second_half)

    if second_rate > first_rate:
        return "increasing"
    elif second_rate < first_rate:
        return "decreasing"
    else:
        return "stable"


# ---------------- SOURCE AGREEMENT ----------------

def source_agreement(sources):
    """
    Measure how many sources confirm the same cluster
    """
    if not sources:
        return 0

    return len(set(sources))


# ---------------- ENTITY CONSISTENCY ----------------

def entity_overlap(actors, locations):
    """
    Check how consistent entities are across reports
    """
    return {
        "actors_count": len(actors),
        "locations_count": len(locations)
    }


# ---------------- IMPORTANCE SCORING ----------------

def compute_importance(cluster):

    merged = cluster["merged_event"]

    score = 0

    # number of events
    score += merged["cluster_size"] * 2

    # sources diversity
    score += len(merged.get("sources", [])) * 3

    # actors involved
    score += len(merged.get("actors", [])) * 2

    # locations
    score += len(merged.get("locations", [])) * 1.5

    return round(score, 2)


# ---------------- SIMPLE SUMMARY ----------------

def generate_summary(cluster):

    merged = cluster["merged_event"]

    event_types = merged.get("event_types", [])
    actors = merged.get("actors", [])
    locations = merged.get("locations", [])

    summary = f"""
Cluster of {merged['cluster_size']} events.

Event Types: {', '.join(event_types[:5])}
Actors: {', '.join(actors[:5])}
Locations: {', '.join(locations[:5])}

Sources involved: {len(merged.get('sources', []))}
"""

    return summary.strip()


# ---------------- MAIN ANALYSIS ----------------

def analyze_clusters(clusters):

    analyzed = []

    for cluster in clusters:

        merged = cluster["merged_event"]

        timestamps = get_all_timestamps(cluster)

        trend = detect_trend(timestamps)

        source_count = source_agreement(merged.get("sources", []))

        importance = compute_importance(cluster)

        summary = generate_summary(cluster)

        analyzed.append({
            "cluster_id": cluster["cluster_id"],

            "analysis": {
                "trend": trend,
                "source_count": source_count,
                "importance_score": importance,
                "summary": summary
            },

            "original_cluster": cluster
        })

    return analyzed