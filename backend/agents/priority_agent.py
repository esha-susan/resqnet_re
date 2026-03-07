PRIORITY_KEYWORDS = {
    "Critical": [
        "death", "dead", "fatality", "trapped", "buried",
        "explosion", "bomb", "collapse", "building collapsed",
        "earthquake", "tsunami", "terrorist", "hostage",
        "gas leak", "chemical spill"
    ],

    "High": [
        "fire", "burning", "flames", "smoke",
        "heart attack", "stroke", "seizure",
        "flood", "flooding", "landslide",
        "serious crash", "major accident"
    ],

    "Medium": [
        "small fire", "injury", "injured", "wound",
        "fight", "assault", "robbery",
        "traffic accident", "minor crash",
        "power outage", "water pipe burst"
    ],

    "Low": [
        "minor", "small", "noise complaint",
        "suspicious", "pothole", "garbage"
    ]
}


def analyze_priority(text: str) -> str:
    if not text:
        return "Low"

    text_lower = text.lower()

    for priority in ["Critical", "High", "Medium", "Low"]:
        for keyword in PRIORITY_KEYWORDS[priority]:
            if keyword in text_lower:
                return priority

    return "Low"


def analyze_incident(title: str, description: str) -> dict:
    combined_text = f"{title} {description}"

    priority = analyze_priority(combined_text)

    return {
        "priority": priority,
        "analyzed_text": combined_text[:100],
        "auto_assigned": True
    }