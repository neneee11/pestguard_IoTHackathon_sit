from datetime import time

POLICIES = {
    "locker_01": {
        "enabled": True,
        "allowed_users": ["user_001", "user_002"],
        "start_time": time(8, 0),
        "end_time": time(18, 0)
    }
}

def get_policy(locker_id: str):
    return POLICIES.get(locker_id)
