import os
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from services.event_services import EventService
from services.notification_service import generate_notification
from db.notification_repository import write_notification
from db.notification_log_repository import log_notification

load_dotenv()

SCHEDULE_DAY    = os.getenv("SCHEDULE_DAY", "sun")
SCHEDULE_HOUR   = int(os.getenv("SCHEDULE_HOUR", 9))
SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", 0))


def run_pipeline() -> None:
    print(f"\n[pipeline] Starting at {datetime.now(timezone.utc).isoformat()}")

    event_service = EventService()

    event_service.clean_old_events()

    user_map: dict[str, list[str]] = {}
    for row in event_service.get_all_user_categories():
        user_map.setdefault(row["user_id"], []).append(row["category_id"])

    event_map: dict[str, list[str]] = {}
    for row in event_service.get_all_event_categories():
        event_map.setdefault(row["event_id"], []).append(row["category_id"])

    if not user_map or not event_map:
        print("[pipeline] No users or events found. Exiting.")
        return

    recommendations = event_service.generate_recommendations(user_map, event_map)

    matched_users = {uid: events for uid, events in recommendations.items() if events}
    if not matched_users:
        print("[pipeline] No matches found. Exiting.")
        return

    print(f"[pipeline] {len(matched_users)} users with matches.")

    
    all_event_ids = list({eid for events in matched_users.values() for eid in events})
    events_by_id: dict[str, dict] = {
        e["id"]: e for e in event_service.get_events_by_ids(all_event_ids)
    }

    success_count = 0
    error_count = 0

    for user_id, scored_events in matched_users.items():
        notification_id = None
        try:
            sorted_ids = sorted(scored_events, key=lambda eid: scored_events[eid], reverse=True)
            events_payload = [events_by_id[eid] for eid in sorted_ids if eid in events_by_id]

            if not events_payload:
                continue

            notification = generate_notification(user_id, events_payload)
            notification_id = write_notification(notification)

            print(f"[pipeline] ✓ {user_id} — '{notification['title']}'")
            log_notification(user_id, notification_id, "success")
            success_count += 1

        except Exception as e:
            print(f"[pipeline] ✗ {user_id} — ERROR: {e}")
            log_notification(user_id, notification_id, "error", str(e))
            error_count += 1

    print(f"\n[pipeline] Done — ✓ {success_count} succeeded, ✗ {error_count} failed.")


def start_scheduler() -> None:
    scheduler = BlockingScheduler(timezone="Europe/Vienna")

    scheduler.add_job(
        run_pipeline,
        trigger="cron",
        day_of_week=SCHEDULE_DAY,
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        id="whazup_notification_pipeline"
    )

    next_run = scheduler.get_job("whazup_notification_pipeline").next_run_time
    print(f"[scheduler] WhazUp Notification Agent started.")
    print(f"[scheduler] Schedule: Every {SCHEDULE_DAY} at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} Vienna time")
    print(f"[scheduler] Next scheduled run: {next_run}")
    print("[scheduler] Running pipeline now for initial verification...\n")

    run_pipeline()

    print("\n[scheduler] Waiting for next scheduled run...")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
