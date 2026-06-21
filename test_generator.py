from generator import generate_notification

mock_events = [
    {
        "id": "test-uuid-1",
        "name": "Tresor Vienna",
        "date_time": "2026-06-28T23:00:00+00:00",
        "location": "Vienna",
        "host_name": "Flex",
        "image_url": None,
        "source_url": "https://flex.at/events/tresor",
        "event_type": "club",
        "categories": ["Techno", "Underground"]
    },
    {
        "id": "test-uuid-2",
        "name": "Rave Garden",
        "date_time": "2026-06-29T22:00:00+00:00",
        "location": "Vienna",
        "host_name": "Grelle Forelle",
        "image_url": "https://example.com/img.jpg",
        "source_url": "https://grelleforelle.com/rave-garden",
        "event_type": "club",
        "categories": ["Techno", "Rave"]
    }
]

result = generate_notification("test-user-id", mock_events)
print("Title:", result["title"])
print("Body:", result["body"])
