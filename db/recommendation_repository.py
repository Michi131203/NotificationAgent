from db.client import SupabaseClient


def write_recommendation(user_id: str, events: list[dict]) -> str:
    """Inserts a recommendation row (top matched events for a user) and returns its id."""
    client = SupabaseClient.get_instance()
    response = client.table("recommendations").insert({
        "user_id": user_id,
        "events": events,
    }).execute()
    return response.data[0]["id"]
