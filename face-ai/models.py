# models.py
import uuid
from sqlalchemy import Column, Integer, String, Boolean, Time, Date, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

# Table 1: students [cite: 2]
class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_no = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

# Table 2: subjects [cite: 3]
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    day_of_week = Column(String(20), nullable=False) # e.g., 'Monday'
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)

# Table 3: student_enrolled [cite: 4]
class StudentEnrolled(Base):
    __tablename__ = "student_enrolled"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    attended = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', name='unique_student_subject_enrollment'),
    )

# Table 4: attendance_logs [cite: 6]
class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    attendance_date = Column(Date, nullable=False, default=func.current_date())
    attended = Column(Boolean, nullable=False, default=True)