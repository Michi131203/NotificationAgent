from db.client import SupabaseClient
from services.event_services import EventService


def main():
    service = EventService()
    #service.clean_old_events()
    users = service.get_users()
    print(f"Fetched {len(users)} users: {users}")
    categories = service.get_all_user_categories()
    print(categories)

if __name__ == "__main__":
    main()
