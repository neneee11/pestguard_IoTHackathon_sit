# app/models/subject.py
import uuid
from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    day_of_week = Column(String(20), nullable=False) # e.g., 'Monday'
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)

    # Relationships
    enrollments = relationship("StudentEnrolled", back_populates="subject")
    attendance_logs = relationship("AttendanceLog", back_populates="subject")

