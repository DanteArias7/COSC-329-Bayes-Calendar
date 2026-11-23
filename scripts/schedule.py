"""Week 11: plan study sessions for a student and put them on Google Calendar.

Run from the project root. By default it only prints the plan (dry run):
    python scripts/schedule.py --student struggling

Add --apply to put it on your calendar:
    python scripts/schedule.py --student struggling --apply

Let the student's practice score change as they study (see src/scheduler.py):
    python scripts/schedule.py --student struggling --progress --apply

Remove everything the planner added (your own events are never touched):
    python scripts/schedule.py --clear

Options:
    --student   struggling | average | advanced
    --exam      exam date as YYYY-MM-DD (default: 10 days from today)
    --calendar  calendar ID (default: your main calendar)
    --progress  simulate the student improving / forgetting over time
"""
import argparse
import os
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.scenarios import STUDENT_PROFILES
from src.scheduler import add_exam_event, apply_day, clear, plan


def print_plan(label, exam_date, days):
    print(f"\n{label} - exam on {exam_date:%a %b %d}\n")
    print(f"{'Date':<12}{'Days left':<11}{'Practice':<10}{'Action':<9}{'P(pass)':<9}{'P(high stress)':<16}EU (I / L / R)")
    for d in days:
        eu = d["expected_utility"]
        print(f"{d['date']:%a %b %d}  {d['days_left']:<3}{d['days_remaining']:<7}{d['practice_score']:<10}{d['action']:<9}"
              f"{d['p_pass']:<9.0%}{d['p_high_stress']:<16.0%}"
              f"{eu['Intense']:.1f} / {eu['Light']:.1f} / {eu['Rest']:.1f}")


def main():
    parser = argparse.ArgumentParser(description="Bayesian study planner")
    parser.add_argument("--student", choices=STUDENT_PROFILES.keys())
    parser.add_argument("--exam", help="exam date YYYY-MM-DD (default: 10 days from today)")
    parser.add_argument("--calendar", default="primary", help="calendar ID (default: main calendar)")
    parser.add_argument("--apply", action="store_true", help="put the plan on the calendar")
    parser.add_argument("--clear", action="store_true", help="remove all planner events up to the exam")
    parser.add_argument("--progress", action="store_true", help="simulate the student improving over time")
    args = parser.parse_args()

    today = date.today()
    exam_date = date.fromisoformat(args.exam) if args.exam else today + timedelta(days=10)
    if exam_date <= today:
        parser.error("exam date has to be in the future")

    if args.clear:
        from src.calendar_api import get_service
        n = clear(get_service(), today, exam_date + timedelta(days=30), args.calendar)
        print(f"Removed {n} planner event(s).")
        return

    if not args.student:
        parser.error("--student is required (struggling, average or advanced)")

    profile = STUDENT_PROFILES[args.student]
    days = plan(profile["evidence"], exam_date, today, progress=args.progress)
    print_plan(profile["label"], exam_date, days)

    if not args.apply:
        print("\nDry run. Add --apply to put this on your calendar.")
        return

    from src.calendar_api import get_service
    service = get_service()
    for d in days:
        apply_day(service, d, args.calendar)
        print(f"  added {d['date']:%a %b %d}: {d['action']}")
    add_exam_event(service, exam_date, args.calendar)
    print(f"  added exam on {exam_date:%a %b %d}")
    print("\nDone. Run with --clear to remove these events.")


if __name__ == "__main__":
    main()
