def is_relevant(title):
    if not title:
        return False

    title = title.lower()

    keywords = [
        "iran", "us", "america",
        "israel", "middle east",
        "war", "conflict", "military"
    ]

    return any(k in title for k in keywords)


def filter_articles(articles):
    return [a for a in articles if is_relevant(a.get("title"))]