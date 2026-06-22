import re
import json
from db.client import SupabaseClient
from services.event_services import EventService
from collections import defaultdict

user_map = defaultdict(list)
event_map = defaultdict(list)

# Deckt die gängigen Emoji-Unicode-Blöcke ab (Symbole, Smileys, Flaggen, etc.)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # Symbole, Emoticons, Objekte, etc.
    "\U00002600-\U000027BF"  # Misc. Symbole & Dingbats
    "\U0001F1E6-\U0001F1FF"  # Regional Indicator (Flaggen)
    "\U00002190-\U000021FF"  # Pfeile
    "\U0000FE00-\U0000FE0F"  # Variation Selectors
    "\U00002B00-\U00002BFF"  # Misc. Symbole und Pfeile
    "]+",
    flags=re.UNICODE,
)


def strip_emojis(value):
    """Entfernt Emojis aus Strings; geht rekursiv durch dicts/listen."""
    if isinstance(value, str):
        return EMOJI_PATTERN.sub("", value).strip()
    if isinstance(value, dict):
        return {k: strip_emojis(v) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_emojis(v) for v in value]
    return value

def main():
    service = EventService()
    #service.clean_old_events()
    usercategories = service.get_all_user_categories()
    for row in usercategories:
        user_map[row['user_id']].append(row['category_id'])
    eventcategories = service.get_all_event_categories()
    for row in eventcategories:
        event_map[row['event_id']].append(row['category_id'])
    matchedscore = service.generate_recommendations(user_map, event_map)
    top_recommendations = {}
    for user_id, scores in matchedscore.items():
        top_events = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
        top_recommendations[user_id] = top_events

    recommendations = []
    for user_id, top_events in top_recommendations.items():
        events = []
        for event_id, score in top_events:
            eventdetails = service.get_event_by_ID(event_id)
            if not eventdetails:
                continue
            eventdetails = strip_emojis(eventdetails)
            events.append({
                "id": event_id,
                "name": eventdetails.get("name"),
                "description": eventdetails.get("description"),
                "location": eventdetails.get("location"),
                "start_time": eventdetails.get("start_time"),
                "host": eventdetails.get("host"),
                "score": score,
            })
        recommendations.append({
            "user_id": user_id,
            "events": events,
        })

    with open("recommendations.json", "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2, default=str)
    print(f"Saved recommendations for {len(recommendations)} users to recommendations.json")
    
if __name__ == "__main__":
    main()
