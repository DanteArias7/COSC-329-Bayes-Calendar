# COSC 329 Bayes Calendar

A personalized study planner that uses a Bayesian network to decide what to schedule before an exam. Based on how difficult the exam concepts are, how much time is left, and how the student is doing, it picks between an intense study block, a light review session, or a rest day, and puts it on Google Calendar.

COSC 329 project, Option 3 (Bayesian Calendar), solo.

## Project structure

```
src/
  model.py          Bayes net variables, structure and CPTs
  inference.py      Inference queries (Variable Elimination)
  decision.py       Actions, utility function and expected utility
  scheduler.py      Plans each day until the exam and puts it on the calendar
  scenarios.py      Simulated student types
  calendar_api.py   Google Calendar login + create/list/delete events
scripts/
  test_calendar.py  Checks that Calendar login works with a test event
  test_inference.py Runs test queries on example students
  run_decision.py   Picks the best action for example students
  sensitivity.py    Checks how the choice changes with the utility weights
  schedule.py       Plans a student's days and adds them to Google Calendar
  simulate_scenarios.py  Simulates every student type (no calendar)
tests/
  test_scheduler.py Scheduler tests with a fake calendar
  print_cpts.py     Writes every CPT to docs/cpt_tables.md
  draw_network.py   Draws the network to docs/network_draft.png
docs/
  network_draft.md  Variables, edges and reasoning for the network
  cpts.md           Reasoning for every CPT + the inference task
  cpt_tables.md     Full CPT tables
  week9_inference_results.md  Test query results
  utility.md        Actions, utility function and expected utility
  week10_decision_results.md  Best action for each example student
  utility_sensitivity.md      Results with different utility weights
  week11.md         How scheduling and the student scenarios work
  week11_schedules.md         Simulated schedules for each student
```

## Setup

1. Install Python 3.10+ and the dependencies:
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set up Google Calendar API access:
   1. Go to https://console.cloud.google.com/ and create a new project.
   2. Go to **APIs & Services > Library**, search for **Google Calendar API** and enable it.
   3. Go to **APIs & Services > OAuth consent screen**. Choose **External**, fill in the app name and your email, and add yourself as a **test user**.
   4. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**. Choose **Desktop app**.
   5. Download the JSON file, rename it to `credentials.json` and put it in the project root. (It's in `.gitignore` so it won't get committed.)

3. Test the calendar connection:
   ```
   python scripts/test_calendar.py          # creates, lists, then deletes a test event
   python scripts/test_calendar.py --keep   # leaves the test event on your calendar
   ```
   The first run opens a browser to sign in. After that the login is saved in `token.json`.

4. Check the network and run test queries:
   ```
   python -m src.model               # builds the network and validates the CPTs
   python scripts/test_inference.py  # example students -> P(Pass) and stress for each action
   python scripts/print_cpts.py      # full CPT tables
   python scripts/run_decision.py    # expected utility of each action + best action
   python scripts/sensitivity.py     # best action with different utility weights
   python scripts/draw_network.py
   ```

## Running the planner

```
python scripts/schedule.py --student struggling              # dry run: prints the plan
python scripts/schedule.py --student struggling --apply      # puts it on your calendar
python scripts/schedule.py --student average --progress --apply   # student improves over time
python scripts/schedule.py --clear                           # removes all planner events
python scripts/simulate_scenarios.py                         # all students, no calendar
python tests/test_scheduler.py                               # tests (fake calendar)
```

`--student` is `struggling`, `average` or `advanced`. `--exam YYYY-MM-DD` sets the exam date (default: 10 days from today). Running `--apply` again replaces the planner's events instead of duplicating them.

## Progress

- [x] Week 8: project setup, Calendar API connection, first draft of the network
- [x] Week 9: CPTs, build the full network in pgmpy, test inference queries
- [x] Week 10: actions, utility function, expected utility
- [x] Week 11: schedule the chosen action on the calendar, simulate student scenarios
- [ ] Week 12: results and report
- [ ] Week 13: presentation video
- [ ] Week 14: final submission
