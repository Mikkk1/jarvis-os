from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from graph.supervisor import run

PKT = pytz.timezone("Asia/Karachi")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=PKT)
    
    # Morning briefing at 7:00 AM PKT
    scheduler.add_job(
        func=lambda: run("morning_briefing"),
        trigger=CronTrigger(hour=7, minute=0, timezone=PKT),
        id="morning_briefing",
        name="Morning Briefing",
        replace_existing=True
    )
    
    # Evening summary at 10:00 PM PKT
    scheduler.add_job(
        func=lambda: run("evening_summary"),
        trigger=CronTrigger(hour=22, minute=0, timezone=PKT),
        id="evening_summary",
        name="Evening Summary",
        replace_existing=True
    )
    
    scheduler.start()
    print("[SCHEDULER] Started. Morning: 7:00 AM PKT | Evening: 10:00 PM PKT")
    return scheduler
