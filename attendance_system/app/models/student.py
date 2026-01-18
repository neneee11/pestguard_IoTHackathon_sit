# app/models/student.py
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Student(Base):
    __tablename__ = 'students'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_no = Column(String(20), unique=True, nullable=False)  # รหัสนักศึกษา
    name = Column(String(100), nullable=False)

    # Relationships
    enrollments = relationship("StudentEnrolled", back_populates="student", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="student")