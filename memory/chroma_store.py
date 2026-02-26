import chromadb
from chromadb.config import Settings
import os
from datetime import datetime

client = chromadb.PersistentClient(path=".chroma")
collection = client.get_or_create_collection("jarvis_memory")

def store_daily_summary(date_str: str, score: int, completed: list, pending: list):
    """Stores end-of-day summary in ChromaDB for pattern tracking."""
    doc = f"Date: {date_str} | Score: {score}% | Completed: {', '.join(completed)} | Missed: {', '.join(pending)}"
    collection.upsert(
        documents=[doc],
        ids=[f"summary_{date_str}"],
        metadatas=[{
            "date": date_str,
            "score": score,
            "type": "daily_summary"
        }]
    )

def get_recent_patterns(days: int = 7) -> list:
    """Retrieves last N days of summaries for pattern analysis."""
    results = collection.query(
        query_texts=["daily task completion summary"],
        n_results=days,
        where={"type": "daily_summary"}
    )
    return results.get("documents", [[]])[0]
