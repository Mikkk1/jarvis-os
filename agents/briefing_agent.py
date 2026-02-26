from services.gemini_service import generate_text
from services.sheets_service import get_streak
from datetime import date
import json
import os

def load_tasks() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "../config/tasks.json")
    with open(config_path) as f:
        return json.load(f)

def calculate_days_until(deadline_str: str) -> int:
    if not deadline_str:
        return None
    deadline = date.fromisoformat(deadline_str)
    return (deadline - date.today()).days

def generate_morning_briefing() -> str:
    """
    Generates a personalized morning briefing using Gemini.
    Returns formatted text ready for delivery.
    """
    config = load_tasks()
    tasks = config["daily_tasks"]
    
    # Build context for Gemini
    task_lines = []
    for task in tasks:
        days_left = calculate_days_until(task.get("deadline"))
        streak = get_streak(task["id"])
        
        line = f"- {task['name']} ({task['priority']})"
        if days_left is not None:
            line += f" | ⚠️ {days_left} days left"
        if streak > 0:
            line += f" | 🔥 {streak} day streak"
        task_lines.append(line)
    
    tasks_text = "\n".join(task_lines)
    today = date.today().strftime("%A, %B %d, %Y")
    
    prompt = f"""You are Jarvis, a personal AI accountability agent for Sarim Zahid.
Generate a sharp, motivating morning briefing for today: {today}

His non-negotiable tasks today:
{tasks_text}

Rules for the briefing:
1. Start with a single punchy line (not "Good morning", something stronger)
2. List all tasks clearly with their deadlines/streaks
3. Call out the CRITICAL AR/VR deadline specifically — it's urgent
4. End with one sentence that creates urgency without being cheesy
5. Keep it under 300 words
6. Tone: direct, no fluff, like a serious coach not a cheerleader

Output only the briefing text. No commentary."""

    return generate_text(prompt)
