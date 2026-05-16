import os
import json
import dateparser
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TASKS_FILE = "tasks.json"

tasks = []


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            tasks.extend(json.load(f))


def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def add_task(title, due_date=None):
    task = {"title": title, "done": False, "due_date": due_date, "calendar_event_id": None}
    tasks.append(task)

    if due_date:
        try:
            service = get_calendar_service()
            dt = dateparser.parse(due_date, settings={"PREFER_DATES_FROM": "future"})
            if not dt:
                print("Sorry, I didn't understand that date. Task saved without a calendar event.")
                save_tasks()
                return
            event = {
                "summary": title,
                "start": {"dateTime": dt.isoformat(), "timeZone": "America/New_York"},
                "end": {"dateTime": dt.isoformat(), "timeZone": "America/New_York"},
            }
            created = service.events().insert(calendarId="primary", body=event).execute()
            task["calendar_event_id"] = created["id"]
            print(f"\nTask added successfully!")
            print(f"  Title    : {title}")
            print(f"  Due      : {dt.strftime('%A, %d %B %Y at %H:%M')}")
            print(f"  Calendar : Added to Google Calendar")
        except Exception as e:
            print(f"Could not add to Google Calendar: {e}")
    else:
        print(f"\nTask added successfully!")
        print(f"  Title    : {title}")
        print(f"  Calendar : Not scheduled")

    save_tasks()


def complete_task(index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
        print(f"Completed: {tasks[index]['title']}")
        save_tasks()
    else:
        print("Invalid task number.")


def list_tasks():
    if not tasks:
        print("No tasks yet!")
        return
    for i, task in enumerate(tasks):
        status = "done" if task["done"] else "pending"
        due = f" | due: {task['due_date']}" if task["due_date"] else ""
        calendar = " [on calendar]" if task["calendar_event_id"] else ""
        print(f"{i + 1}. [{status}] {task['title']}{due}{calendar}")


def main():
    load_tasks()
    print("Simple To-Do App")
    print("Commands: add, complete, list, quit")

    while True:
        command = input("\nWhat would you like to do? ").strip().lower()

        if command == "add":
            title = input("Task name: ").strip()
            if not title:
                print("Task name cannot be empty.")
                continue
            due_date = input("When? (e.g. tomorrow, next Friday, 17th May — or press Enter to skip): ").strip() or None
            add_task(title, due_date)

        elif command == "complete":
            list_tasks()
            try:
                number = int(input("Enter task number to complete: "))
                complete_task(number - 1)
            except ValueError:
                print("Please enter a valid number.")

        elif command == "list":
            list_tasks()

        elif command == "quit":
            print("Goodbye!")
            break

        else:
            print("Unknown command. Try: add, complete, list, quit")


if __name__ == "__main__":
    main()
