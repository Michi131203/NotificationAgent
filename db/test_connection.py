from db.client import SupabaseClient
from services.event_services import EventService


def main():
    service = EventService()
    service.clean_old_events()


if __name__ == "__main__":
    main()
