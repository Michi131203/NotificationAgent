from datetime import datetime, timedelta
from db.repository import EventRepository
from utils.logger import get_logger

class EventService:
    def __init__(self):
        self.repo = EventRepository()
        self.logger = get_logger("EventService")
    
    def clean_old_events(self):
        old_events = self.repo.get_old_events()
        self.logger.info(f"Found {len(old_events)} old events to clean.")
        for event in old_events:
            try:
                self.repo.delete_event(event['name'])
                self.logger.info(f"Cleaning event: {event['name']}")
            except Exception as e:
                self.logger.error(f"Failed to delete event '{event['name']}': {e}")
        self.logger.info("Finished cleaning old events.")
    def get_all_user_categories(self):
        try:
            self.logger.info("Fetching user categories from the database.")
            categories = self.repo.get_all_user_categories()
            self.logger.info(f"Fetched {len(categories)} user categories.")
            return categories
        except Exception as e:
            self.logger.error(f"Failed to fetch user categories: {e}")
            return []
    def get_all_event_categories(self):
        try:
            self.logger.info("Fetching event categories from the database.")
            categories = self.repo.get_all_event_categories()
            self.logger.info(f"Fetched {len(categories)} event categories.")
            return categories
        except Exception as e:
            self.logger.error(f"Failed to fetch event categories: {e}")
            return []
        
    def generate_recommendations(self, user_map, event_map):
        all_results = {}

        for user_id, user_categories in user_map.items():
            scores = {}

            for event_id, event_categories in event_map.items():
                user_categories_set = set(user_categories)
                event_categories_set = set(event_categories)
                matches = user_categories_set.intersection(event_categories_set)
                if matches:
                    scores[event_id] = len(matches)

            all_results[user_id] = scores

        return all_results