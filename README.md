# Jarvis OS 🤖

A Python-based personal accountability agent that sends daily briefings, tracks task completion, and logs to Google Sheets.

## Features

- 🌅 **Morning Briefing** (7:00 AM PKT) — AI-generated daily kickoff with deadlines & streaks
- ✅ **Task Tracking** — Log completions via HTTP endpoint (`POST /done`)
- 📊 **Google Sheets Logging** — Every completion persisted in Sheets
- 🌙 **Evening Summary** (10:00 PM PKT) — Daily score and accountability report
- 🔥 **Streak Tracking** — Consecutive-day completion counts
- 🧠 **Vector Memory** — ChromaDB stores daily patterns for long-term analysis
- 🔌 **WhatsApp-Ready** — Pluggable messenger layer (deferred to Week 2)

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Agent Framework | LangGraph 0.2.x |
| LLM | Google Gemini 1.5 Flash |
| Scheduler | APScheduler 3.x |
| Google Sheets | gspread + google-auth |
| Vector Memory | ChromaDB (local persistent) |
| API Server | FastAPI |
| Containerization | Docker + docker-compose |

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/jarvis-os.git
cd jarvis-os
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual keys
```

### 3. Google Sheets Setup

1. Create a new Google Sheet
2. Add headers in Row 1: `Date`, `Task ID`, `Task Name`, `Completed At`, `Status`
3. Copy the Sheet ID from the URL
4. Create a Google Cloud Service Account with Sheets + Drive API
5. Download credentials JSON
6. Share the Sheet with the service account email
7. Set `GOOGLE_SHEET_ID` and `GOOGLE_SHEETS_CREDENTIALS_JSON` in `.env`

### 4. Run

```bash
python main.py
# OR
uvicorn main:app --reload
```

### 5. Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/briefing` | Trigger morning briefing |
| POST | `/done` | Mark task complete |
| GET | `/summary` | Trigger evening summary |
| GET | `/status` | Today's completion status |
| GET | `/messages` | All messages sent today |

### Marking a Task Done

```bash
curl -X POST http://localhost:8000/done \
  -H "Content-Type: application/json" \
  -d '{"task": "done german"}'
```

Valid task keywords: `arvr`, `diss`, `wahab`, `mujeeb`, `dsa`, `sql`, `linkedin`, `journal`, `german`, `jarvis`, `outreach`

## Deployment (Railway.app)

1. Push to GitHub
2. Railway → New Project → Deploy from GitHub
3. Add environment variables from `.env` in Railway's Variables tab
4. Railway auto-detects Dockerfile and deploys

## WhatsApp Integration (Week 2)

When ready, only 3 changes needed:
1. Fill `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_RECIPIENT_NUMBER` in `.env`
2. Uncomment `_send_whatsapp(content)` in `services/messenger.py`
3. Implement `_send_whatsapp()` with Meta API call

No other files need to change.

## Project Structure

```
jarvis-os/
├── agents/
│   ├── briefing_agent.py    # Morning briefing generation
│   ├── task_agent.py        # Task completion processing
│   └── logger_agent.py      # Evening summary generation
├── config/
│   └── tasks.json           # Sarim's 9 daily tasks
├── memory/
│   └── chroma_store.py      # ChromaDB vector persistence
├── services/
│   ├── gemini_service.py    # Gemini 1.5 Flash wrapper
│   ├── sheets_service.py    # Google Sheets integration
│   └── messenger.py         # Pluggable delivery layer
├── graph/
│   └── supervisor.py        # LangGraph routing supervisor
├── scheduler/
│   └── jobs.py              # APScheduler cron jobs
├── main.py                  # FastAPI application
├── Dockerfile
└── docker-compose.yml
```
