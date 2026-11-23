"""Tests for the scheduler using a fake Google Calendar (no internet needed).

Run from the project root:
    python tests/test_scheduler.py
"""
import os
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.calendar_api import APP_TAG
from src.scenarios import STUDENT_PROFILES
from src.scheduler import add_exam_event, apply_day, clear, days_bucket, plan


class _Call:
    def __init__(self, fn):
        self.fn = fn

    def execute(self):
        return self.fn()


class FakeEvents:
    """Mimics the parts of service.events() the project uses."""

    def __init__(self):
        self.items = {}
        self.next_id = 0

    def insert(self, calendarId, body):
        def run():
            self.next_id += 1
            ev = dict(body, id=str(self.next_id))
            self.items[ev["id"]] = ev
            return ev
        return _Call(run)

    def delete(self, calendarId, eventId):
        return _Call(lambda: self.items.pop(eventId))

    def list(self, calendarId, timeMin, timeMax, singleEvents, orderBy, pageToken=None):
        lo = datetime.fromisoformat(timeMin).replace(tzinfo=None)
        hi = datetime.fromisoformat(timeMax).replace(tzinfo=None)

        def start_of(ev):
            s = ev["start"]
            return (datetime.fromisoformat(s["dateTime"]) if "dateTime" in s
                    else datetime.fromisoformat(s["date"]))
        return _Call(lambda: {"items": [e for e in self.items.values() if lo <= start_of(e) < hi]})


class FakeService:
    def __init__(self):
        self._events = FakeEvents()

    def events(self):
        return self._events


def test_days_bucket():
    assert [days_bucket(d) for d in (1, 3, 4, 7, 8, 20)] == ["Few", "Few", "Some", "Some", "Many", "Many"]


def test_different_students_get_different_actions():
    exam, start = date(2026, 12, 3), date(2026, 11, 30)  # 3 days left -> Few
    first = {name: plan(p["evidence"], exam, start)[0]["action"]
             for name, p in STUDENT_PROFILES.items()}
    assert first == {"struggling": "Intense", "average": "Light", "advanced": "Rest"}, first


def test_plan_covers_every_day_before_exam():
    days = plan(STUDENT_PROFILES["average"]["evidence"], date(2026, 12, 3), date(2026, 11, 23))
    assert len(days) == 10
    assert days[0]["date"] == date(2026, 11, 23) and days[-1]["date"] == date(2026, 12, 2)
    assert days[-1]["days_left"] == 1


def test_progress_changes_struggling_students_plan():
    days = plan(STUDENT_PROFILES["struggling"]["evidence"], date(2026, 12, 3),
                date(2026, 11, 23), progress=True)
    actions = [d["action"] for d in days]
    assert actions[0] == "Intense" and "Light" in actions  # studies hard, then eases off
    assert days[-1]["practice_score"] != "Low"


def test_apply_creates_right_events_and_is_rerunnable():
    service = FakeService()
    days = plan(STUDENT_PROFILES["struggling"]["evidence"], date(2026, 12, 3),
                date(2026, 11, 30), progress=False)
    for d in days:
        apply_day(service, d)
    for d in days:  # running it twice should not create duplicates
        apply_day(service, d)
    events = list(service.events().items.values())
    assert len(events) == 3
    for ev in events:
        assert ev["summary"].startswith(APP_TAG)
        assert ev["start"]["dateTime"].endswith("09:00:00")  # intense block starts 9am
        assert ev["end"]["dateTime"].endswith("14:00:00")    # 5 hours


def test_rest_day_is_all_day_and_replaces_study_event():
    service = FakeService()
    day = plan(STUDENT_PROFILES["struggling"]["evidence"], date(2026, 12, 3), date(2026, 12, 2))[0]
    apply_day(service, day)
    rest = dict(day, action="Rest")
    apply_day(service, rest)
    events = list(service.events().items.values())
    assert len(events) == 1 and "date" in events[0]["start"]
    assert "Rest day" in events[0]["summary"]


def test_clear_only_removes_planner_events():
    service = FakeService()
    service.events().insert("primary", {"summary": "Dentist",
                                        "start": {"dateTime": "2026-12-01T10:00:00"},
                                        "end": {"dateTime": "2026-12-01T11:00:00"}}).execute()
    for d in plan(STUDENT_PROFILES["average"]["evidence"], date(2026, 12, 3), date(2026, 11, 30)):
        apply_day(service, d)
    add_exam_event(service, date(2026, 12, 3))
    clear(service, date(2026, 11, 30), date(2026, 12, 3))
    left = [e["summary"] for e in service.events().items.values()]
    assert left == ["Dentist"], left


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print("passed", t.__name__)
    print(f"All {len(tests)} tests passed")
