from db.client import SupabaseClient
from services.event_services import EventService
from collections import defaultdict

user_map = defaultdict(list)
event_map = defaultdict(list)

def main():
    service = EventService()
    #service.clean_old_events()
    usercategories = service.get_all_user_categories()
    for row in usercategories:
        user_map[row['user_id']].append(row['category_id'])
    eventcategories = service.get_all_event_categories()
    for row in eventcategories:
        event_map[row['event_id']].append(row['category_id'])
    print(event_map)

if __name__ == "__main__":
    main()
