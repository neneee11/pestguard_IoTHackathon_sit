from datetime import datetime

def log_event(event, user=None, detail=None):
    print({
        "time": datetime.utcnow().isoformat(),
        "event": event,
        "user": user,
        "detail": detail
    })
