from datetime import datetime, timezone
from db.client import SupabaseClient


def log_notification(
    user_id: str,
    notification_id: str | None,
    status: str,
    error_message: str | None = None
) -> None:
    """Logs a pipeline attempt to notification_log. Never raises."""
    try:
        client = SupabaseClient.get_instance()
        client.table("notification_log").insert({
            "user_id": user_id,
            "notification_id": notification_id,
            "status": status,
            "error_message": error_message,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        print(f"[notification_log] Failed to write log for user {user_id}: {e}")
