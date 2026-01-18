import asyncio
import sys
import os
from datetime import time

sys.path.append(os.getcwd())

# ✅ แก้ไขตรงนี้: เปลี่ยนจาก SessionLocal เป็น AsyncSessionLocal
from app.core.database import AsyncSessionLocal 

from app.models.student import Student
from app.models.subject import Subject
from app.models.student_enrolled import StudentEnrolled

async def seed_data():
    print("🌱 Seeding data...")
    
    # ✅ แก้ไขตรงนี้: เรียกใช้ AsyncSessionLocal()
    async with AsyncSessionLocal() as db:
        
        # --- 1. สร้างวิชา (Subjects) ---
        subject_ai = Subject(
            name="AI & Computer Vision",
            day_of_week="Sunday", 
            time_start=time(13, 0),
            time_end=time(20, 0)
        )
        
        subject_iot = Subject(
            name="IoT System Design",
            day_of_week="Monday",
            time_start=time(9, 0),
            time_end=time(12, 0)
        )
        
        db.add_all([subject_ai, subject_iot])
        await db.commit()
        
        await db.refresh(subject_ai)
        await db.refresh(subject_iot)
        
        """
        # --- 2. สร้างนักเรียน (Student) ---
        student = Student(
            student_no="66000123",
            name="Test Student"
        )
        
        db.add(student)
        await db.commit()
        await db.refresh(student)

        # --- 3. ลงทะเบียนเรียน (Enrollment) ---
        enrollment = StudentEnrolled(
            student_id=student.id,
            subject_id=subject_ai.id
        )
        
        db.add(enrollment)
        await db.commit()
        """
    print("🎉 Seeding complete! Data is ready.")

if __name__ == "__main__":
    asyncio.run(seed_data())