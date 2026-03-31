import re
import json

def safe_json_parse(text):

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass

    return None


def summarize_cluster(cluster_texts, llm):

    # LIMIT TEXT (VERY IMPORTANT)
    combined_text = "\n".join(cluster_texts[:3])[:1000] 

    prompt = f"""
Summarize ONE event.

Return JSON ONLY:

{{
 "event_summary": "",
 "event_type": "",
 "key_points": [],
 "actors": [],
 "location": "",
 "date": "",
 "impact": ""
}}

TEXT:
{combined_text}
"""

    response = llm(prompt)

    parsed = safe_json_parse(response)

    if parsed:
        return parsed

    return {
        "event_summary": response,
        "event_type": "unknown",
        "key_points": [],
        "actors": [],
        "location": None,
        "date": None,
        "impact": None
    }