from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

message_log = []

def send_message(content: str, message_type: str = "general") -> dict:
    timestamp = datetime.now().isoformat()
    message = {"timestamp": timestamp, "type": message_type, "content": content}
    
    _send_console(content, message_type)
    _send_whatsapp(content)
    
    message_log.append(message)
    return message

def _send_console(content: str, message_type: str):
    print(f"\n{'='*60}")
    print(f"[JARVIS - {message_type.upper()}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    print(content)
    print('='*60 + "\n")

def _send_whatsapp(content: str):
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    recipient = os.getenv("WHATSAPP_RECIPIENT_NUMBER")
    
    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": content}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"[WHATSAPP ERROR] {response.status_code}: {response.text}")

def get_message_log() -> list:
    return message_log