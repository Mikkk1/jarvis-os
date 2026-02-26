from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from scheduler.jobs import start_scheduler
from graph.supervisor import run
from services.messenger import get_message_log
import uvicorn

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = start_scheduler()
    yield
    if scheduler:
        scheduler.shutdown()

app = FastAPI(title="Jarvis OS", version="1.0.0", lifespan=lifespan)

class TaskInput(BaseModel):
    task: str  # e.g. "done german"

# ── ENDPOINTS ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Jarvis is running", "version": "1.0.0"}

@app.get("/briefing")
def trigger_briefing():
    """Manually trigger morning briefing."""
    response = run("morning_briefing")
    return {"message": response}

@app.post("/done")
def mark_done(body: TaskInput):
    """Mark a task as done. Body: { 'task': 'done german' }"""
    response = run("task_done", user_input=body.task)
    return {"message": response}

@app.get("/summary")
def trigger_summary():
    """Manually trigger evening summary."""
    response = run("evening_summary")
    return {"message": response}

@app.get("/status")
def get_status():
    """Get today's completion status."""
    response = run("status")
    return {"message": response}

@app.get("/messages")
def get_messages():
    """Get all messages sent today."""
    return {"messages": get_message_log()}

# ── RUN ────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
