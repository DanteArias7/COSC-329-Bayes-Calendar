"""Helpers for talking to the Google Calendar API.

The first time this runs it opens a browser window to sign in with Google.
After that the login is saved in token.json so you don't have to sign in again.
"""
import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# full read/write access to calendars (needed to create and delete events)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(ROOT, "credentials.json")
TOKEN_FILE = os.path.join(ROOT, "token.json")

# tag added to every event we create so we can find and clean them up later
APP_TAG = "[Bayes Study Planner]"
TIMEZONE = "America/Vancouver"


def get_service():
    """Log in (or reuse the saved login) and return a Calendar API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found. Download the OAuth client file from "
                    "Google Cloud Console and put it in the project root (see README)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def create_event(service, title, start, hours, description="", calendar_id="primary"):
    """Create an event starting at `start` (a datetime) that lasts `hours` hours."""
    end = start + timedelta(hours=hours)
    event = {
        "summary": f"{APP_TAG} {title}",
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": TIMEZONE},
    }
    return service.events().insert(calendarId=calendar_id, body=event).execute()


def list_events(service, start, end, calendar_id="primary"):
    """Return all events between two datetimes."""
    result = service.events().list(
        calendarId=calendar_id,
        timeMin=start.astimezone().isoformat(),
        timeMax=end.astimezone().isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return result.get("items", [])


def delete_planner_events(service, start, end, calendar_id="primary"):
    """Delete only the events this app created in a date range.

    Used for the "rest day" action. Only touches events with APP_TAG in the
    title so it never deletes the user's own events.
    """
    deleted = 0
    for event in list_events(service, start, end, calendar_id):
        if event.get("summary", "").startswith(APP_TAG):
            service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()
            deleted += 1
    return deleted


def day_bounds(day):
    """Start and end of a given date as datetimes."""
    start = datetime(day.year, day.month, day.day)
    return start, start + timedelta(days=1)
