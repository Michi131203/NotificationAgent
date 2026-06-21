import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_notification(user_id: str, events: list[dict]) -> dict:
    if not events:
        raise ValueError(f"No events for user {user_id}")

    event_lines = []
    for e in events:
        cats = ", ".join(e.get("categories", []))
        event_lines.append(
            f"- {e['name']} | {e.get('host_name', 'Unknown venue')} | "
            f"{e.get('location', '?')} | {e['date_time'][:10]} | {cats}"
        )
    events_text = "\n".join(event_lines)

    all_cats = []
    for e in events:
        all_cats.extend(e.get("categories", []))
    top_category = max(set(all_cats), key=all_cats.count) if all_cats else "Events"

    locations = [e.get("location") for e in events if e.get("location")]
    top_location = locations[0] if locations else "Austria"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""You are the WhazUp event discovery app — Austria's nightlife guide.
Generate a short, punchy in-app notification for a user about their matched events.

Events:
{events_text}

Top category: {top_category}
Primary location: {top_location}
Number of events: {len(events)}

Return ONLY valid JSON with exactly two keys:
- "title": max 60 chars, punchy, include event count + top category + city + 1 emoji
- "body": 2-3 sentences, friendly and hype, no bullet points, conversational Austrian nightlife tone

Example:
{{"title": "3 Techno Events in Vienna this weekend 🎧", "body": "Your weekend lineup is sorted. We found {len(events)} {top_category} events in {top_location} that match your vibe — from underground sets to big room bangers. Tap to see the full lineup."}}

Return raw JSON only. No markdown, no code blocks, no preamble."""
            }
        ]
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    generated = json.loads(raw)

    return {
        "user_id": user_id,
        "title": generated["title"],
        "body": generated["body"],
        "events": events,
        "read": False
    }
