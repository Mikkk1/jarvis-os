import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet_client():
    creds = Credentials.from_service_account_file(
        os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON"),
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client

def log_task_completion(task_id: str, task_name: str) -> bool:
    """
    Logs a completed task to Google Sheets.
    Sheet structure: Date | Task ID | Task Name | Completed At | Status
    """
    try:
        client = get_sheet_client()
        sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
        
        row = [
            str(date.today()),
            task_id,
            task_name,
            datetime.now().strftime("%H:%M:%S"),
            "DONE"
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"[SHEETS ERROR] {e}")
        return False

def get_todays_completions() -> list:
    """Returns all tasks completed today from the sheet."""
    try:
        client = get_sheet_client()
        sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
        records = sheet.get_all_records()
        today = str(date.today())
        return [r for r in records if r.get("Date") == today and r.get("Status") == "DONE"]
    except Exception as e:
        print(f"[SHEETS ERROR] {e}")
        return []

def get_streak(task_id: str) -> int:
    """Counts consecutive days a task has been completed."""
    try:
        client = get_sheet_client()
        sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
        records = sheet.get_all_records()
        
        task_records = [r for r in records if r.get("Task ID") == task_id and r.get("Status") == "DONE"]
        if not task_records:
            return 0
        
        dates = sorted(set(r["Date"] for r in task_records), reverse=True)
        streak = 0
        check_date = date.today()
        
        for d in dates:
            if str(check_date) == d:
                streak += 1
                from datetime import timedelta
                check_date -= timedelta(days=1)
            else:
                break
        
        return streak
    except Exception as e:
        print(f"[SHEETS ERROR] {e}")
        return 0
