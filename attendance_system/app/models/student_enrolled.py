from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class StudentEnrolled(Base):
    __tablename__ = "student_enrolled"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    #attended = Column(Boolean, default=False)
    # หมายเหตุ: attended ในตารางนี้อาจหมายถึง "ผ่านวิชานี้แล้ว" หรือไม่ 
    # แต่ถ้าจะเช็คชื่อรายวันเราจะใช้ AttendanceLog แทนครับ
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', name='unique_student_subject_enrollment'),
    )

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")