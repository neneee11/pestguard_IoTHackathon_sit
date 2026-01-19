from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.face_service import face_service
from app.models.student import Student
from app.schemas.student import RegisterResponse
import uuid

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_student(
    student_no: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Image Processing
        image_bytes = await file.read()
        embedding = face_service.get_embedding(image_bytes)
        
        new_uuid = uuid.uuid4()

        # 2. DB Insert
        new_student = Student(id=new_uuid, student_no=student_no, name=name)
        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)

        # 3. Vector DB Upsert
        face_service.save_face_vector(
            student_uuid=new_uuid, 
            embedding=embedding, 
            metadata={"student_no": student_no, "name": name}
        )

        return RegisterResponse(status="success", student_id=str(new_uuid))

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))