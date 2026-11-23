"""Turns the system's decisions into calendar events (Week 11).

For each day from the start date up to the day before the exam:
  1. work out DaysRemaining from the exam date
  2. run the decision (inference + expected utility) for that day
  3. put the chosen action on the calendar
"""
from datetime import date, datetime, time, timedelta

from src.calendar_api import (create_all_day_event, create_event, day_bounds,
                              delete_planner_events)
from src.decision import ACTIONS, DecisionMaker
from src.inference import marginal

# Optional student progress simulation (--progress). Without it the student's
# evidence stays the same every day. With it, studying slowly raises their
# practice score and a long stretch of rest lowers it:
#   - Intense adds 1 progress point, Light adds 0.5, Rest adds 0
#   - every 2 progress points moves PracticeScore up one level
#   - 3 rest days in a row moves PracticeScore down one level (forgetting)
# The rules are deterministic so the demo gives the same result every time.
PROGRESS_GAIN = {"Intense": 1.0, "Light": 0.5, "Rest": 0.0}
POINTS_PER_LEVEL = 2.0
RESTS_BEFORE_DROP = 3
LEVELS = ["Low", "Medium", "High"]

# when each kind of session starts
START_TIMES = {
    "Intense": time(9, 0),   # 9am - 2pm
    "Light": time(19, 0),    # 7pm - 8pm
}


def days_bucket(days_left):
    """Map days until the exam to the DaysRemaining values in the model."""
    if days_left <= 3:
        return "Few"
    if days_left <= 7:
        return "Some"
    return "Many"


def update_progress(evidence, action, state):
    """Apply one day of the progress rules. Changes evidence and state in place."""
    level = LEVELS.index(evidence["PracticeScore"])
    state["points"] += PROGRESS_GAIN[action]
    state["rests"] = state["rests"] + 1 if action == "Rest" else 0
    if state["points"] >= POINTS_PER_LEVEL and level < len(LEVELS) - 1:
        evidence["PracticeScore"] = LEVELS[level + 1]
        state["points"] = 0.0
    elif state["rests"] >= RESTS_BEFORE_DROP and level > 0:
        evidence["PracticeScore"] = LEVELS[level - 1]
        state["rests"] = 0


def plan(profile_evidence, exam_date, start_date=None, decision_maker=None, progress=False):
    """Decide an action for every day from start_date to the day before the exam.

    If progress is True, the student's PracticeScore changes over time based on
    the actions taken (see the rules at the top of this file).
    Returns a list of dicts, one per day."""
    dm = decision_maker or DecisionMaker()
    start_date = start_date or date.today()
    student = dict(profile_evidence)
    state = {"points": 0.0, "rests": 0}
    days = []
    day = start_date
    while day < exam_date:
        days_left = (exam_date - day).days
        evidence = dict(student, DaysRemaining=days_bucket(days_left))
        result = dm.decide(evidence)
        best = result["best_action"]
        days.append({
            "date": day,
            "days_left": days_left,
            "days_remaining": evidence["DaysRemaining"],
            "action": best,
            "expected_utility": result["expected_utility"],
            "p_pass": marginal(result["outcomes"][best], "ExamSuccess")["Pass"],
            "p_high_stress": marginal(result["outcomes"][best], "Stress")["High"],
            "mastery": result["mastery"],
            "practice_score": evidence["PracticeScore"],
        })
        if progress:
            update_progress(student, best, state)
        day += timedelta(days=1)
    return days


def describe(day_plan):
    """Event description so it's clear on the calendar why this was chosen."""
    eu = day_plan["expected_utility"]
    m = day_plan["mastery"]
    return (
        f"{ACTIONS[day_plan['action']]['description']}.\n\n"
        f"Chosen by the Bayesian study planner.\n"
        f"Days until exam: {day_plan['days_left']} ({day_plan['days_remaining']})\n"
        f"Practice score: {day_plan['practice_score']}\n"
        f"Estimated mastery: Low {m['Low']:.0%}, Medium {m['Medium']:.0%}, High {m['High']:.0%}\n"
        f"Expected utility: Intense {eu['Intense']:.1f}, Light {eu['Light']:.1f}, Rest {eu['Rest']:.1f}\n"
        f"With this plan: P(pass) {day_plan['p_pass']:.0%}, P(high stress) {day_plan['p_high_stress']:.0%}"
    )


def apply_day(service, day_plan, calendar_id="primary"):
    """Put one day's action on the calendar. Clears the planner's old events
    for that day first, so running it again doesn't create duplicates."""
    day = day_plan["date"]
    start, end = day_bounds(day)
    delete_planner_events(service, start, end, calendar_id)

    action = day_plan["action"]
    info = ACTIONS[action]
    if action == "Rest":
        return create_all_day_event(service, info["title"], day, describe(day_plan), calendar_id)
    when = datetime.combine(day, START_TIMES[action])
    return create_event(service, info["title"], when, info["hours"], describe(day_plan), calendar_id)


def add_exam_event(service, exam_date, calendar_id="primary"):
    start, end = day_bounds(exam_date)
    delete_planner_events(service, start, end, calendar_id)
    return create_all_day_event(service, "EXAM", exam_date,
                                "Exam date used by the study planner.", calendar_id)


def clear(service, start_date, end_date, calendar_id="primary"):
    """Remove every planner event from start_date to end_date (inclusive)."""
    start, _ = day_bounds(start_date)
    _, end = day_bounds(end_date)
    return delete_planner_events(service, start, end, calendar_id)
