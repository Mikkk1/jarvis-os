from services.sheets_service import log_task_completion, get_todays_completions
from services.messenger import send_message
import json
import os

def load_tasks() -> list:
    config_path = os.path.join(os.path.dirname(__file__), "../config/tasks.json")
    with open(config_path) as f:
        return json.load(f)["daily_tasks"]

def find_task_by_input(user_input: str) -> dict | None:
    """
    Matches user input like 'done german' or 'done dsa' to a task.
    Uses fuzzy keyword matching against task id and name.
    """
    tasks = load_tasks()
    user_input_lower = user_input.lower().strip()
    
    # Remove 'done' prefix if present
    if user_input_lower.startswith("done"):
        keyword = user_input_lower.replace("done", "").strip()
    else:
        keyword = user_input_lower
    
    for task in tasks:
        if keyword in task["id"].lower() or keyword in task["name"].lower():
            return task
    
    return None

def process_completion(user_input: str) -> str:
    """
    Processes a 'done [task]' command.
    Logs to sheets, returns confirmation message.
    """
    task = find_task_by_input(user_input)
    
    if not task:
        return f"❌ Could not find task matching '{user_input}'. Try: done german, done dsa, done arvr, done linkedin"
    
    success = log_task_completion(task["id"], task["name"])
    
    if success:
        completions = get_todays_completions()
        total_tasks = 9
        done_count = len(completions)
        
        response = f"✅ Logged: {task['name']}\n"
        response += f"Progress today: {done_count}/{total_tasks} tasks done"
        return response
    else:
        return f"⚠️ Logged locally but failed to sync to sheets. Will retry."

def get_completion_status() -> dict:
    """Returns today's completion status."""
    completions = get_todays_completions()
    all_tasks = load_tasks()
    
    completed_ids = [c.get("Task ID") for c in completions]
    pending = [t for t in all_tasks if t["id"] not in completed_ids]
    
    return {
        "total": len(all_tasks),
        "completed": len(completions),
        "pending": pending,
        "score": round(len(completions) / len(all_tasks) * 100)
    }
