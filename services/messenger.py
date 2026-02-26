from datetime import datetime

# In-memory message log (for testing without WhatsApp)
message_log = []

def send_message(content: str, message_type: str = "general") -> dict:
    """
    Delivery layer for Jarvis messages.
    Currently: prints to console + logs to memory.
    Later: replace _send_whatsapp() with actual Meta API call.
    """
    timestamp = datetime.now().isoformat()
    message = {
        "timestamp": timestamp,
        "type": message_type,
        "content": content
    }
    
    # Console delivery (active now)
    _send_console(content, message_type)
    
    # WhatsApp delivery (deferred - uncomment when credentials ready)
    # _send_whatsapp(content)
    
    message_log.append(message)
    return message

def _send_console(content: str, message_type: str):
    print(f"\n{'='*60}")
    print(f"[JARVIS - {message_type.upper()}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    print(content)
    print('='*60 + "\n")

def _send_whatsapp(content: str):
    """
    DEFERRED. Will use Meta WhatsApp Cloud API.
    POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages
    Headers: Authorization: Bearer {ACCESS_TOKEN}
    Body: { "messaging_product": "whatsapp", "to": "{RECIPIENT}", "type": "text", "text": {"body": content} }
    """
    pass

def get_message_log() -> list:
    return message_log
