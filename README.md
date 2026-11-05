# COSC 329 Bayes Calendar

A personalized study planner that uses a Bayesian network to decide what to schedule before an exam. Based on how difficult the exam concepts are, how much time is left, and how the student is doing, it picks between an intense study block, a light review session, or a rest day, and puts it on Google Calendar.

COSC 329 project, Option 3 (Bayesian Calendar), solo.

## Project structure

```
src/
  model.py          Bayes net variables and structure (CPTs coming in Week 9)
  calendar_api.py   Google Calendar login + create/list/delete events
scripts/
  test_calendar.py  Checks that Calendar login works with a test event
  draw_network.py   Draws the network to docs/network_draft.png
docs/
  network_draft.md  Variables, edges and reasoning for the draft network
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

4. Check the network structure:
   ```
   python -m src.model
   python scripts/draw_network.py
   ```

## Progress

- [x] Week 8: project setup, Calendar API connection, first draft of the network
- [ ] Week 9: CPTs, build the full network in pgmpy, test inference queries
- [ ] Week 10: actions, utility function, expected utility
- [ ] Week 11: schedule the chosen action on the calendar, simulate student scenarios
- [ ] Week 12: results and report
- [ ] Week 13: presentation video
- [ ] Week 14: final submission
