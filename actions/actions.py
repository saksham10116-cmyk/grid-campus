from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import gspread
from google.oauth2.service_account import Credentials

# ---- Google Sheets connection setup ----
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS_FILE = "gsheet-credentials.json"
SHEET_NAME = "grid  spreadsheet"

def get_students_from_sheet():
    """Reads the live Google Sheet every time it's called, so updates are picked up instantly."""
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    records = sheet.get_all_records()

    students = []
    for r in records:
        students.append({
            "name": r.get("Name", "").strip(),
            "skills": r.get("Skills", "").strip(),
            "result": int(r.get("Result", 0)),
            "strength": r.get("Strength", "").strip(),
            "weakness": r.get("Weakness", "").strip(),
        })
    return students


class ActionGetTeamSuggestion(Action):
    def name(self) -> Text:
        return "action_get_team_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            students = get_students_from_sheet()
        except Exception as e:
            dispatcher.utter_message(text=f"Couldn't reach the student sheet: {e}")
            return []

        if not students:
            dispatcher.utter_message(text="No student data found in the sheet.")
            return []

        sorted_students = sorted(students, key=lambda s: s["result"], reverse=True)
        team_a = [s["name"] for i, s in enumerate(sorted_students) if i % 2 == 0]
        team_b = [s["name"] for i, s in enumerate(sorted_students) if i % 2 == 1]

        message = f"Suggested Team A: {', '.join(team_a)}\nSuggested Team B: {', '.join(team_b)}"
        dispatcher.utter_message(text=message)
        return []


class ActionGetStudentInfo(Action):
    def name(self) -> Text:
        return "action_get_student_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        student_name = tracker.get_slot("student_name") or next(tracker.get_latest_entity_values("student_name"), None)

        try:
            students = get_students_from_sheet()
        except Exception as e:
            dispatcher.utter_message(text=f"Couldn't reach the student sheet: {e}")
            return []

        match = next((s for s in students if s["name"].lower() == str(student_name).lower()), None)

        if match:
            message = (f"{match['name']} — Skills: {match['skills']}, "
                       f"Result: {match['result']}, Strength: {match['strength']}, "
                       f"Weakness: {match['weakness']}")
        else:
            message = f"I couldn't find a student named {student_name}."

        dispatcher.utter_message(text=message)
        return []