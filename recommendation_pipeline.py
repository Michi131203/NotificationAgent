import re
import json
from db.client import SupabaseClient
from db.recommendation_repository import write_recommendation
from services.event_services import EventService
from utils.logger import get_logger
from collections import defaultdict

logger = get_logger("RecommendationPipeline")

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
    logger.info("Starting recommendation pipeline.")
    service = EventService()
    client = SupabaseClient.get_instance()
    service.clean_old_events()
    usercategories = service.get_all_user_categories()
    for row in usercategories:
        user_map[row['user_id']].append(row['category_id'])
    logger.info(f"Built category map for {len(user_map)} users.")

    eventcategories = service.get_all_event_categories()
    for row in eventcategories:
        event_map[row['event_id']].append(row['category_id'])
    logger.info(f"Built category map for {len(event_map)} events.")

    # category_id -> name (small table, fetched once)
    cat_rows = client.table("categories").select("id, name").execute().data
    cat_names = {c["id"]: c["name"] for c in cat_rows}

    # host_id -> name, lazily cached (only the hosts we actually need)
    host_cache: dict[str, str | None] = {}

    def host_name(host_id):
        if not host_id:
            return None
        if host_id not in host_cache:
            resp = client.table("hosts").select("name").eq("id", host_id).execute()
            host_cache[host_id] = resp.data[0]["name"] if resp.data else None
        return host_cache[host_id]

    matchedscore = service.generate_recommendations(user_map, event_map)
    top_recommendations = {}
    for user_id, scores in matchedscore.items():
        top_events = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
        top_recommendations[user_id] = top_events
    logger.info(f"Selected top 3 events for {len(top_recommendations)} users.")

    recommendations = []
    for user_id, top_events in top_recommendations.items():
        events = []
        for event_id, score in top_events:
            eventdetails = service.get_event_by_ID(event_id)
            if not eventdetails:
                logger.warning(f"Skipping event {event_id} for user {user_id}: no details found.")
                continue
            categories = [
                cat_names[cid]
                for cid in event_map.get(event_id, [])
                if cid in cat_names
            ]
            events.append(strip_emojis({
                "id": event_id,
                "name": eventdetails.get("name"),
                "date_time": eventdetails.get("date_time"),
                "location": eventdetails.get("location"),
                "host_name": host_name(eventdetails.get("host")),
                "image_url": eventdetails.get("image_url"),
                "source_url": eventdetails.get("source_url"),
                "event_type": eventdetails.get("event_type"),
                "categories": categories,
                "score": score,
            }))
        recommendations.append({
            "user_id": user_id,
            "events": events,
        })
        logger.info(f"Built {len(events)} event recommendations for user {user_id}.")

        try:
            rec_id = write_recommendation(user_id, events)
            logger.info(f"Wrote recommendation {rec_id} for user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to write recommendation for user {user_id}: {e}")

    try:
        with open("recommendations.json", "w", encoding="utf-8") as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Saved recommendations for {len(recommendations)} users to recommendations.json")
    except Exception as e:
        logger.error(f"Failed to write recommendations.json: {e}")



if __name__ == "__main__":
    main()
