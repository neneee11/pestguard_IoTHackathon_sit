import uuid
import datetime
import pytz # แนะนำให้ใช้เพื่อแก้ปัญหา Timezone
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, HTTPException, Form, Depends, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from insightface.app import FaceAnalysis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Import files ที่เราสร้างตะกี้
from database import get_db, engine, Base
from models import Student, Subject, StudentEnrolled, AttendanceLog

# ============================
# SETUP
# ============================
app = FastAPI()
qdrant = QdrantClient(host="10.4.41.250", port=6333)
COLLECTION_NAME = "student_faces"

# InsightFace Setup
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=0, det_size=(640, 640))

# Timezone (Thai)
BKK_TZ = pytz.timezone('Asia/Bangkok')

@app.on_event("startup")
async def startup_event():
    # สร้าง Table ใน DB (ถ้ายังไม่มี) แบบ Async
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Qdrant Init
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )

def process_image(file_bytes):
    # InsightFace เป็น CPU-bound operation (ยังคงเป็น Sync)
    # ถ้า load เยอะจริงๆ ควรแยกไปรันใน ThreadPool หรือ Celery
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = face_app.get(img)
    if not faces:
        raise ValueError("No face detected")
    return faces[0].embedding

# ============================
# API: Register (Async)
# ============================
@app.post("/register")
async def register_student(
    student_no: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db) # Inject Async DB Session
):
    try:
        image_bytes = await file.read()
        embedding = process_image(image_bytes)
        
        # Generate UUID
        new_uuid = uuid.uuid4()

        # 1. Insert ลง PostgreSQL (Async)
        new_student = Student(id=new_uuid, student_no=student_no, name=name)
        db.add(new_student)
        await db.commit() # รอ commit แบบ async
        await db.refresh(new_student)

        # 2. Insert ลง Qdrant (Sync - qdrant client ปกติเร็วอยู่แล้ว)
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(new_uuid),
                    vector=embedding.tolist(),
                    payload={"student_no": student_no, "name": name}
                )
            ]
        )

        return {"status": "success", "student_id": str(new_uuid)}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================
# API: Check-in (Async + Logic แน่นๆ)
# ============================
@app.post("/check-in")
async def check_in(
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Process Image
        image_bytes = await file.read()
        try:
            embedding = process_image(image_bytes)
        except ValueError as ve:
            return {"status": "failed", "message": str(ve)}
        
        # 2. Search Qdrant
        search_result = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding.tolist(),
            limit=1,
            score_threshold=0.5
        )

        if not search_result.points:
            return {"status": "failed", "message": "Unknown person"}

        # ดึงคนแรกสุดออกมา
        top_match = search_result.points[0]

        student_uuid = uuid.UUID(top_match.id) # Convert string to UUID obj
        print(f"Match Found: {top_match.payload.get('name')} (Score: {top_match.score})")

        # 3. เตรียมเวลาปัจจุบัน (Timezone Aware)
        now = datetime.datetime.now(BKK_TZ)
        current_day = now.strftime("%A") # e.g., 'Monday'
        current_time = now.time()

        # 4. Query หา Subject ที่กำลังเรียน (SQLAlchemy Select)
        # SELECT subjects.* FROM subjects JOIN student_enrolled ...
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

        # 5. Check Duplicate Log (ป้องกันเช็คซ้ำในวันเดียว)
        stmt_log = select(AttendanceLog).where(
            AttendanceLog.student_id == student_uuid,
            AttendanceLog.subject_id == subject.id,
            AttendanceLog.attendance_date == now.date()
        )
        log_result = await db.execute(stmt_log)
        existing_log = log_result.scalars().first()

        if existing_log:
            return {"status": "info", "message": f"Already checked in for {subject.name}"}

        # 6. Insert Log & Update Enrollment
        # Insert Log
        new_log = AttendanceLog(
            student_id=student_uuid,
            subject_id=subject.id,
            attendance_date=now.date(),
            attended=True
        )
        db.add(new_log)

        # Update Enrollment Status (SQLAlchemy Update)
        stmt_update = (
            update(StudentEnrolled)
            .where(
                StudentEnrolled.student_id == student_uuid,
                StudentEnrolled.subject_id == subject.id
            )
            .values(attended=True)
        )
        await db.execute(stmt_update)

        # Commit ทั้งหมดทีเดียว (Atomic Transaction)
        await db.commit()

        return {
            "status": "success",
            "student_name": top_match.payload.get("name"),
            "subject": subject.name,
            "time": now.strftime("%H:%M:%S")
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)