from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class AccessRequest(BaseModel):
    user_id: str
    locker_id: str
    timestamp: str

class AccessPolicy(BaseModel):
    locker_id: str
    allowed_users: List[str]
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    enabled: bool = True

class DecisionResult(BaseModel):
    allow: bool
    reason: str
