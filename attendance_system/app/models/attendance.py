# app/models/attendance.py
import uuid
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    attendance_date = Column(Date, nullable=False, default=func.current_date())
    attended = Column(Boolean, nullable=False, default=True)
    timestamp = Column(Time, default=func.current_time()) # เก็บเวลาที่สแกนจริง

    # Relationships
    student = relationship("Student", back_populates="attendance_logs")
    subject = relationship("Subject", back_populates="attendance_logs")