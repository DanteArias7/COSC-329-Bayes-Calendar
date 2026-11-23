# Calendar Integration and Student Scenarios (Week 11)

## How the system schedules

`src/scheduler.py` runs the decision for **every day** from today until the day before the exam:

1. Work out **DaysRemaining** from the exam date (Few = 0-3 days, Some = 4-7, Many = 8+).
2. Run the inference query and expected utility (Weeks 9-10) with that day's evidence.
3. Put the chosen action on Google Calendar:

| Action | Calendar event |
|---|---|
| Intense | 5 hour "Intense study block", 9am - 2pm |
| Light | 1 hour "Light review", 7pm - 8pm |
| Rest | All-day "Rest day" marker, and any planner study session on that day is removed |

The exam date is also added as an all-day "EXAM" event.

Each event's description says why it was chosen: days until the exam, practice score, estimated mastery, the expected utility of all three actions, and P(pass) / P(high stress) for the chosen plan.

Every event the planner creates starts with `[Bayes Study Planner]`. Before scheduling a day, the planner deletes its own old events on that day, so running it again updates the plan instead of making duplicates. `--clear` removes only planner events, never the user's own.

## Simulating students

`src/scenarios.py` defines three students by concept difficulty and practice score:

| Student | Difficulty A / B / C | Practice score |
|---|---|---|
| Struggling | Hard / Hard / Medium | Low |
| Average | Medium / Medium / Medium | Medium |
| Advanced | Easy / Easy / Medium | High |

### Fixed students

If a student's evidence never changes, each type gets one consistent action: **struggling → Intense, average → Light, advanced → Rest**. This shows the system adapts to the student, but a real student's understanding changes as they study.

### With student progress (`--progress`)

A simple deterministic progress model updates the practice score after each day:

- Intense adds 1 progress point, Light adds 0.5, Rest adds 0.
- Every 2 points moves PracticeScore up one level.
- 3 rest days in a row moves PracticeScore down one level (forgetting).

With this, the schedules change over time ([week11_schedules.md](week11_schedules.md)):

- **Struggling:** two intense days, then switches to light reviews once practice scores improve to Medium.
- **Average:** light reviews until practice scores reach High, then rests. After 3 rest days the score drops, so the system brings back a light review.
- **Advanced:** rests until the score slips, does light reviews to get it back to High, then rests before the exam.

So the system responds to how the student is doing each day, not just to the type of student they started as. The progress model is simulated, not learned from data, and its rules are kept simple on purpose. A dynamic Bayesian network would be the proper way to model this, which is a possible extension.

## Testing

`tests/test_scheduler.py` checks the scheduler with a fake Google Calendar (no internet needed): the right events and times get created, rerunning doesn't duplicate events, rest days replace study events, and `--clear` doesn't touch other events. The real calendar was tested with `scripts/test_calendar.py`.
