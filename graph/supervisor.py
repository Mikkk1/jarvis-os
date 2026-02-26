from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from agents.briefing_agent import generate_morning_briefing
from agents.task_agent import process_completion, get_completion_status
from agents.logger_agent import generate_evening_summary
from services.messenger import send_message

class JarvisState(TypedDict):
    action: str           # "morning_briefing" | "task_done" | "evening_summary" | "status"
    user_input: str       # raw input from user
    response: str         # output message
    error: str            # error message if any

def route_action(state: JarvisState) -> Literal["briefing", "task", "summary", "status"]:
    action = state.get("action", "")
    if action == "morning_briefing":
        return "briefing"
    elif action == "task_done":
        return "task"
    elif action == "evening_summary":
        return "summary"
    else:
        return "status"

def briefing_node(state: JarvisState) -> JarvisState:
    try:
        message = generate_morning_briefing()
        send_message(message, "morning_briefing")
        return {**state, "response": message}
    except Exception as e:
        return {**state, "error": str(e), "response": f"Briefing failed: {e}"}

def task_node(state: JarvisState) -> JarvisState:
    try:
        response = process_completion(state.get("user_input", ""))
        send_message(response, "task_completion")
        return {**state, "response": response}
    except Exception as e:
        return {**state, "error": str(e), "response": f"Task logging failed: {e}"}

def summary_node(state: JarvisState) -> JarvisState:
    try:
        message = generate_evening_summary()
        send_message(message, "evening_summary")
        return {**state, "response": message}
    except Exception as e:
        return {**state, "error": str(e), "response": f"Summary failed: {e}"}

def status_node(state: JarvisState) -> JarvisState:
    status = get_completion_status()
    msg = f"Today's progress: {status['completed']}/{status['total']} tasks ({status['score']}%)"
    if status["pending"]:
        msg += "\nPending: " + ", ".join(t["name"] for t in status["pending"])
    send_message(msg, "status")
    return {**state, "response": msg}

def build_graph() -> StateGraph:
    graph = StateGraph(JarvisState)
    
    graph.add_node("briefing", briefing_node)
    graph.add_node("task", task_node)
    graph.add_node("summary", summary_node)
    graph.add_node("status", status_node)
    
    graph.set_conditional_entry_point(
        route_action,
        {
            "briefing": "briefing",
            "task": "task",
            "summary": "summary",
            "status": "status"
        }
    )
    
    graph.add_edge("briefing", END)
    graph.add_edge("task", END)
    graph.add_edge("summary", END)
    graph.add_edge("status", END)
    
    return graph.compile()

jarvis_graph = build_graph()

def run(action: str, user_input: str = "") -> str:
    result = jarvis_graph.invoke({
        "action": action,
        "user_input": user_input,
        "response": "",
        "error": ""
    })
    return result["response"]
