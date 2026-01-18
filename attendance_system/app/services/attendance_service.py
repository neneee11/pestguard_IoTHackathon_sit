import datetime
import pytz
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.subject import Subject
from app.models.student_enrolled import StudentEnrolled
from app.models.attendance import AttendanceLog
from app.models.student import Student

BKK_TZ = pytz.timezone('Asia/Bangkok')

class AttendanceService:
    async def process_check_in(self, db: AsyncSession, student_uuid: uuid.UUID, student_name: str):
        now = datetime.datetime.now(BKK_TZ)
        current_day = now.strftime("%A")
        current_time = now.time()

        # 1. Find active subject
        stmt = (
            select(Subject)
            .join(StudentEnrolled, Subject.id == StudentEnrolled.subject_id)
            .where(
                StudentEnrolled.student_id == student_uuid,
                Subject.day_of_week == current_day,
                Subject.time_start <= current_time,
                Subject.time_end >= current_time
            )
        )
        result = await db.execute(stmt)
        subject = result.scalars().first()

        if not subject:
            return {"status": "warning", "message": "No class scheduled right now."}

        # 2. Check duplicate log
        stmt_log = select(AttendanceLog).where(
            AttendanceLog.student_id == student_uuid,
            AttendanceLog.subject_id == subject.id,
            AttendanceLog.attendance_date == now.date()
        )
        log_result = await db.execute(stmt_log)
        if log_result.scalars().first():
            return {"status": "info", "message": f"Already checked in for {subject.name}"}

        # 3. Create Log & Update Enrollment
        new_log = AttendanceLog(
            student_id=student_uuid,
            subject_id=subject.id,
            attendance_date=now.date(),
            attended=True
        )
        db.add(new_log)

        stmt_update = (
            update(StudentEnrolled)
            .where(
                StudentEnrolled.student_id == student_uuid,
                StudentEnrolled.subject_id == subject.id
            )
            .values(attended=True)
        )
        await db.execute(stmt_update)
        await db.commit()

        return {
            "status": "success",
            "student_name": student_name,
            "subject": subject.name,
            "time": now.strftime("%H:%M:%S")
        }