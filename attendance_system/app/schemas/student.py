# app/schemas/student.py
from pydantic import BaseModel
from uuid import UUID

class StudentBase(BaseModel):
    student_no: str
    name: str

# Used when returning student data
class StudentResponse(StudentBase):
    id: UUID

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models

# Used for the registration response
class RegisterResponse(BaseModel):
    status: str
    student_id: str