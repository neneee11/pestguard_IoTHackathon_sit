from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.attendance import CheckInResponse
from app.services.face_service import face_service
from app.services.attendance_service import AttendanceService
import uuid

router = APIRouter()
attendance_service = AttendanceService()

@router.post("/check-in", response_model=CheckInResponse)
async def check_in(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Get Embedding
        image_bytes = await file.read()
        embedding = face_service.get_embedding(image_bytes)
        
        # 2. Identify Person
        match = face_service.search_face(embedding)
        if not match:
            return {"status": "failed", "message": "Unknown person"}
            
        student_uuid = uuid.UUID(match.id)
        student_name = match.payload.get("name")

        # 3. Process Logic
        return await attendance_service.process_check_in(db, student_uuid, student_name)

    except ValueError as ve:
        return {"status": "failed", "message": str(ve)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))