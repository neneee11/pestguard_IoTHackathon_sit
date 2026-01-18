# app/schemas/attendance.py
from pydantic import BaseModel

class CheckInResponse(BaseModel):
    status: str
    student_name: str | None = None
    subject: str | None = None
    time: str | None = None
    message: str | None = None