from db.client import SupabaseClient


def write_notification(notification: dict) -> str:
    """Inserts a notification row and returns its id."""
    client = SupabaseClient.get_instance()
    response = client.table("notifications").insert({
        "user_id": notification["user_id"],
        "title": notification["title"],
        "body": notification["body"],
        "events": notification["events"],
        "read": notification.get("read", False)
    }).execute()
    return response.data[0]["id"]
