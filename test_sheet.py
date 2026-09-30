import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS_FILE = "gsheet-credentials.json"
SHEET_NAME = "grid  spreadsheet"

print("Step 1: Loading credentials...")
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
print("Step 1 OK")

print("Step 2: Authorizing client...")
client = gspread.authorize(creds)
print("Step 2 OK")

print("Step 3: Opening sheet by name:", SHEET_NAME)
sheet = client.open(SHEET_NAME)
print("Step 3 OK — sheet found:", sheet.title)

print("Step 4: Getting first tab...")
ws = sheet.sheet1
print("Step 4 OK — tab name:", ws.title)

print("Step 5: Reading records...")
records = ws.get_all_records()
print("Step 5 OK — total students found:", len(records))
print("First student:", records[0] if records else "NONE FOUND")
@app.post("/add_student")
def add_student(s: StudentModel):
    ws = client.open("grid spreadsheet").sheet1
    ws.append_row([s.name, s.skills, s.result, s.strength, s.weakness])
    return {"status": "success"}