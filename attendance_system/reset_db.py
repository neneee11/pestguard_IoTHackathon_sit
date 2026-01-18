import asyncio
import sys
import os

# เพิ่ม Path ปัจจุบันเพื่อให้ Python มองเห็นโฟลเดอร์ 'app'
sys.path.append(os.getcwd())

# 1. Import engine และ Base จากตำแหน่งใหม่
# (ปกติ Base มักจะอยู่ใน app/core/database.py หรือ app/models/__init__.py)
# ลองเช็คดูนะครับว่า Base ประกาศไว้ที่ไหน ถ้าอยู่ที่ database.py ก็ใช้บรรทัดนี้:
from app.core.database import engine, Base 

# 2. **สำคัญมาก**: ต้อง Import Models ทั้งหมดมาที่นี่ เพื่อให้ Base รู้จักตาราง
# (ถ้าไม่ Import ตารางจะไม่ถูกสร้าง)
from app.models.student import Student
from app.models.subject import Subject
from app.models.attendance import AttendanceLog # หรือชื่อ Class ที่คุณใช้ในไฟล์ attendance.py
from app.models.student_enrolled import StudentEnrolled # อย่าลืมตารางนี้ (ถ้าแยกไฟล์ไว้)

async def reset_database():
    print("🔄 Resetting database...")
    async with engine.begin() as conn:
        # ลบตารางเก่าทิ้ง
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️  Dropped old tables.")
        
        # สร้างตารางใหม่
        await conn.run_sync(Base.metadata.create_all)
        print("✨ Created new tables.")
    
    print("✅ Database reset successfully!")

if __name__ == "__main__":
    asyncio.run(reset_database())