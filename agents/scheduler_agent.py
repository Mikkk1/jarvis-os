from services.sheets_service import get_todays_completions
from agents.task_agent import load_tasks
import json
import os
from datetime import datetime
import pytz

PKT = pytz.timezone("Asia/Karachi")

def load_schedule() -> dict:
    path = os.path.join(os.path.dirname(__file__), "../config/schedule.json")
    with open(path) as f:
        return json.load(f)

def get_current_block(now: datetime) -> dict | None:
    """Returns the active schedule block for the given PKT time."""
    schedule = load_schedule()
    current_time = now.strftime("%H:%M")
    for block in schedule["blocks"]:
        if block["start"] <= current_time < block["end"]:
            return block
    return None

def get_minutes_left_in_block(block: dict, now: datetime) -> int:
    end_h, end_m = map(int, block["end"].split(":"))
    end_dt = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
    return max(0, int((end_dt - now).total_seconds() / 60))

def get_next_task() -> str:
    """Core logic for the 'next' command: returns the best task for the current block."""
    now = datetime.now(PKT)
    block = get_current_block(now)

    if not block:
        return "⏸ No active work block right now. Rest, pray, or plan ahead."

    if block["type"] in ["prayer_personal", "prayer_rest"]:
        return f"🕌 {block['name']} — this is prayer/rest time. No task assigned."

    # Get completions + all tasks
    completions = get_todays_completions()
    completed_ids = {c.get("Task ID") for c in completions}
    all_tasks = load_tasks()

    # Filter: task in this block AND not yet done
    block_task_ids = set(block.get("tasks", []))
    candidates = [
        t for t in all_tasks
        if t["id"] in block_task_ids and t["id"] not in completed_ids
    ]

    if not candidates:
        # All block tasks done — pull from any incomplete deep_work task
        candidates = [
            t for t in all_tasks
            if t["id"] not in completed_ids
            and t.get("block_category") == "deep_work"
        ]
        if not candidates:
            return "✅ All tasks complete for today. Jarvis is proud."

    # Score and pick top task
    from agents.briefing_agent import score_urgency, calculate_days_until
    best = sorted(candidates, key=score_urgency, reverse=True)[0]
    mins_left = get_minutes_left_in_block(block, now)

    from datetime import date
    days_left = calculate_days_until(best.get("deadline"))
    deadline_str = f"{days_left}d left" if days_left is not None else "no deadline"

    return (
        f"⚡ *Next task:* {best['name']}\n"
        f"Block: {block['name']} | {mins_left} min remaining\n"
        f"Priority: {best['priority']} | {deadline_str}"
    )
