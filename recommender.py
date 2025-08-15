import spacy # type: ignore
from datetime import datetime

nlp = spacy.load("en_core_web_sm")

def extract_preferences(text):
    doc = nlp(text.lower())

    prefs = {
        "location": None,
        "type": None,
        "activities": [],
        "amenities": []
    }

    # Use spaCy entity recognition first
    for ent in doc.ents:
        if ent.label_ == "GPE":
            prefs["location"] = ent.text.strip().lower()
            break

    # Fallback: known locations
    if not prefs["location"]:
        known_locations = [
            "maharashtra", "himachal pradesh", "kerala",
            "uttarakhand", "gujarat", "tamil nadu", "rajasthan", "london"
        ]
        for loc in known_locations:
            if loc in text.lower():
                prefs["location"] = loc
                break

    prefs["type"] = next(
        (word for word in ["tent", "cabin", "rv"] if word in text.lower()), None
    )

    prefs["activities"] = [
        word for word in ["hiking", "bonfire", "trekking", "boating", "cultural shows", "stargazing", "fishing"]
        if word in text.lower()
    ]

    prefs["amenities"] = [
        word for word in ["toilets", "water", "firewood", "wi-fi"]
        if word in text.lower()
    ]

    return prefs


def is_available(camp_id, from_date, to_date, bookings):
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    
    for booking in bookings:
        if booking["camp_id"] == camp_id:
            booked_from = datetime.strptime(booking["from_date"], "%Y-%m-%d")
            booked_to = datetime.strptime(booking["to_date"], "%Y-%m-%d")

            # Check for date range overlap
            if from_dt <= booked_to and to_dt >= booked_from:
                return False
    return True


def match_campgrounds(preferences, campgrounds, from_date, to_date, bookings):
    matches = []
    for camp in campgrounds:
        if camp.get("status") != "Active":
            continue

        #if not is_available(camp["id"], from_date, to_date, bookings):
            #continue

        score = 0
        if preferences["location"] and preferences["location"] in camp["location"].lower():
            score += 3
        if preferences["type"] and preferences["type"] in camp["type"].lower():
            score += 1
        if preferences["activities"]:
            score += len(set(preferences["activities"]) & set([a.lower() for a in camp["activities"]]))
        if preferences["amenities"]:
            score += len(set(preferences["amenities"]) & set([a.lower() for a in camp["amenities"]]))
        if score > 0:
            matches.append((score, camp))

    matches.sort(reverse=True, key=lambda x: x[0])
    return matches[:3]       