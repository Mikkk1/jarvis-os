from services.gemini_service import generate_text
from services.sheets_service import get_todays_completions
from agents.task_agent import get_completion_status
from datetime import date
import json
import os

def load_tasks() -> list:
    config_path = os.path.join(os.path.dirname(__file__), "../config/tasks.json")
    with open(config_path) as f:
        return json.load(f)["daily_tasks"]

def generate_evening_summary() -> str:
    """
    Generates the evening accountability summary.
    Shows what was done, what wasn't, score, and a brief reflection prompt.
    """
    status = get_completion_status()
    completions = get_todays_completions()
    
    completed_names = [c.get("Task Name") for c in completions]
    pending_names = [t["name"] for t in status["pending"]]
    
    today = date.today().strftime("%A, %B %d, %Y")
    score = status["score"]
    
    prompt = f"""You are Jarvis, Sarim's personal AI accountability agent.
Generate an evening summary for {today}.

Completion score: {score}% ({status['completed']}/{status['total']} tasks)

Completed today:
{chr(10).join(f'✅ {name}' for name in completed_names) if completed_names else 'None'}

Not completed today:
{chr(10).join(f'❌ {name}' for name in pending_names) if pending_names else 'All done!'}

Rules:
1. Start with the score prominently
2. If score < 50%: be direct about it, no softening
3. If score >= 80%: acknowledge it briefly, then focus on tomorrow
4. List missed tasks and their consequence (deadlines, streaks broken)
5. End with ONE specific action for tomorrow morning
6. Under 250 words. No fluff.

Output only the summary text."""

    return generate_text(prompt)
