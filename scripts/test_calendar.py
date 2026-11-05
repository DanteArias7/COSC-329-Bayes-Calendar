"""Week 8 check: make sure Google Calendar OAuth works.

Creates a 1 hour test event tomorrow at 10am, lists it, then deletes it
(pass --keep to leave it on the calendar so you can see it).

Run from the project root:
    python scripts/test_calendar.py
    python scripts/test_calendar.py --keep
"""
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.calendar_api import (create_event, day_bounds, delete_planner_events,
                              get_service, list_events)


def main():
    keep = "--keep" in sys.argv
    service = get_service()
    print("Logged in to Google Calendar")

    tomorrow = date.today() + timedelta(days=1)
    start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0)
    event = create_event(service, "Test event", start, hours=1,
                         description="Test event from the study planner setup.")
    print("Created:", event["summary"], "->", event.get("htmlLink"))

    day_start, day_end = day_bounds(tomorrow)
    print("Events tomorrow:")
    for e in list_events(service, day_start, day_end):
        print("  -", e["start"].get("dateTime", e["start"].get("date")), e.get("summary"))

    if not keep:
        n = delete_planner_events(service, day_start, day_end)
        print(f"Deleted {n} test event(s)")


if __name__ == "__main__":
    main()
