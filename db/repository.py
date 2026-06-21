from db.client import SupabaseClient
from datetime import datetime, timedelta

class EventRepository:
    def __init__(self):
        self.client = SupabaseClient.get_instance()
    
    def get_old_events(self, days: int = 30):
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        try:
            response = self.client.table("events").select("name").lt("created_at", cutoff_date).execute()
        except Exception as e:
            raise Exception(f"Error fetching old events: {e}")
        return response.data
    def delete_event(self, event_name: str):
        try:
            response = self.client.table("events").delete().eq("name", event_name).execute()
        except Exception as e:
            raise Exception(f"Error deleting event '{event_name}': {e}")
        return response.data
    def get_all_user_categories(self):
        try:
            response = self.client.table("user_categories").select("user_id, category_id").execute()
        except Exception as e:
            raise Exception(f"Error fetching categories: {e}")
        return response.data
    def get_all_event_categories(self):
        try:
            response = self.client.table("event_categories").select("event_id, category_id").execute()
        except Exception as e:
            raise Exception(f"Error fetching event categories: {e}")
        return response.data
            