
from config.settings import Settings
from supabase import create_client, Client

class SupabaseClient:
    _instance: Client | None = None

    @classmethod
    def get_instance(cls) -> Client:
        if cls._instance is None:
            url = Settings.SUPABASE_URL
            key = Settings.SUPABASE_KEY
            if not url or not key:
                raise ValueError("Supabase URL and Key must be set in environment variables.")
            cls._instance = create_client(url, key)
        return cls._instance

