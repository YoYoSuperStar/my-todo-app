import os
import json
import dateparser
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TASKS_FILE = "tasks.json"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return []


def save_tasks(tasks):
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


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    title = data.get("title", "").strip()
    due_input = data.get("due", "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    task = {"title": title, "done": False, "due": due_input or None, "due_formatted": None, "calendar_event_id": None}

    if due_input:
        dt = dateparser.parse(due_input, settings={"PREFER_DATES_FROM": "future"})
        if dt:
            task["due_formatted"] = dt.strftime("%A, %d %B %Y at %H:%M")
            try:
                service = get_calendar_service()
                event = {
                    "summary": title,
                    "start": {"dateTime": dt.isoformat(), "timeZone": "America/New_York"},
                    "end": {"dateTime": dt.isoformat(), "timeZone": "America/New_York"},
                }
                created = service.events().insert(calendarId="primary", body=event).execute()
                task["calendar_event_id"] = created["id"]
            except Exception as e:
                print(f"Calendar error: {e}")

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    return jsonify(task), 201


@app.route("/tasks/<int:index>", methods=["PATCH"])
def toggle_task(index):
    tasks = load_tasks()
    if index < 0 or index >= len(tasks):
        return jsonify({"error": "Task not found"}), 404
    tasks[index]["done"] = not tasks[index]["done"]
    save_tasks(tasks)
    return jsonify(tasks[index])


@app.route("/tasks/<int:index>", methods=["DELETE"])
def delete_task(index):
    tasks = load_tasks()
    if index < 0 or index >= len(tasks):
        return jsonify({"error": "Task not found"}), 404
    tasks.pop(index)
    save_tasks(tasks)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
