from services.groq_service import generate_text
from services.sheets_service import get_streak
from datetime import date
import json
import os

def load_tasks() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "../config/tasks.json")
    with open(config_path) as f:
        return json.load(f)

def calculate_days_until(deadline_str: str) -> int | None:
    if not deadline_str:
        return None
    deadline = date.fromisoformat(deadline_str)
    return (deadline - date.today()).days

def score_urgency(task: dict) -> int:
    """Higher score = shown first in briefing."""
    score = 0
    priority_weights = {"CRITICAL": 1000, "HIGH": 500, "MEDIUM": 200, "LOW": 50}
    score += priority_weights.get(task.get("priority", "LOW"), 0)
    days_left = calculate_days_until(task.get("deadline"))
    if days_left is not None:
        if days_left <= 3:    score += 800
        elif days_left <= 7:  score += 400
        elif days_left <= 14: score += 200
        elif days_left <= 30: score += 100
    return score

def get_urgency_flag(days_left) -> str:
    if days_left is None: return ""
    if days_left <= 3:  return "🚨 CRITICAL"
    if days_left <= 7:  return "⚠️"
    return "📅"

def generate_morning_briefing() -> str:
    """
    Fixed-format briefing: Python builds structure, Groq fills opener + closer only.
    Format is identical every day — only the 2 LLM lines differ.
    """
    config = load_tasks()
    tasks = config["daily_tasks"]
    today = date.today().strftime("%A, %B %d, %Y")

    # Sort tasks by urgency score descending
    tasks_sorted = sorted(tasks, key=score_urgency, reverse=True)

    # Groq: opener only — 15 words max
    opening_prompt = f"""You are Jarvis, Sarim's personal AI agent.
Today is {today}. Write ONE punchy opening line for his morning briefing.
Not 'Good morning.' Not motivational fluff. Signal: day has started, work to do.
Max 15 words. Output only the line, nothing else."""
    opening_line = generate_text(opening_prompt, max_tokens=60).strip()

    # Build task list in Python — NOT by Groq
    task_lines = []
    for task in tasks_sorted:
        days_left = calculate_days_until(task.get("deadline"))
        streak = get_streak(task["id"])
        urgency = get_urgency_flag(days_left)
        line = f"• *{task['name']}* — {task['priority']}"
        if days_left is not None:
            line += f" {urgency} {days_left}d left"
        if streak > 0:
            line += f" 🔥 {streak} day streak"
        task_lines.append(line)

    tasks_block = "\n".join(task_lines)

    # Groq: closer only — 20 words max
    closing_prompt = """You are Jarvis. Write ONE closing line for a morning briefing.
Creates urgency. Direct. No fluff. No exclamation marks. Max 20 words. Output only the line."""
    closing_line = generate_text(closing_prompt, max_tokens=60).strip()

    # Assemble fixed format — structure never changes
    briefing = f"""{opening_line}

📅 *{today}*

*TODAY'S TASKS (by priority):*
{tasks_block}

{closing_line}"""
    return briefing
