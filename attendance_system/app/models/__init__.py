# app/models/__init__.py
from app.core.database import Base
from app.models.student import Student
from app.models.subject import Subject
from app.models.attendance import AttendanceLog
from app.models.student_enrolled import StudentEnrolled