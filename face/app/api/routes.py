import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional

# Import Services ที่เราสร้างไว้
from app.services.face_service import face_service
from app.services.vector_db import qdrant_service

# Import Schemas (เดี๋ยวเราจะสร้างไฟล์นี้เป็นขั้นตอนต่อไป)
from app.api.schemas import VerifyResponse, EnrollResponse

from pydantic import BaseModel # เพิ่มสำหรับรับ Json Body

# Setup Logger
logger = logging.getLogger(__name__)

# สร้าง Router
router = APIRouter()

class BookingRequest(BaseModel):
    user_id: int
    locker_id: str

# ---------------------------------------------------------
# 1. VERIFY ENDPOINT (สำหรับ ESP32 สแกนหน้าเปิดตู้)
# ---------------------------------------------------------
@router.post("/register", response_model=EnrollResponse)
async def register_user(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):
    """เก็บหน้าและ ID ลงฐานข้อมูล"""
    # 1. แปลงรูป
    image_bytes = await file.read()
    img = face_service.bytes_to_image(image_bytes)
    if img is None: raise HTTPException(400, "Invalid Image")

    # 2. หา Vector
    face_obj, _ = face_service.detect_one_face(img)
    if face_obj is None: raise HTTPException(400, "Face not found")

    # 3. บันทึกลง DB (โดยยังไม่มี Locker ID)
    success = qdrant_service.register_new_user(user_id, face_obj.embedding.tolist())
    
    if not success: raise HTTPException(500, "Database Error")

    return EnrollResponse(status="success", message=f"User {user_id} registered.")

@router.post("/book")
async def book_locker(request: BookingRequest):
    """
    รับ user_id กับ locker_id เพื่อผูกสิทธิ์ (ไม่ต้องถ่ายรูป)
    """
    # เรียกฟังก์ชันอัปเดต Payload ใน Qdrant
    success = qdrant_service.update_booking(request.user_id, request.locker_id)
    
    if success:
        return {"status": "success", "message": f"Locker {request.locker_id} assigned to User {request.user_id}"}
    else:
        raise HTTPException(404, "User ID not found or Database error")
    
@router.post("/verify", response_model=VerifyResponse)
async def verify_face(
    file: UploadFile = File(...)
):
    """
    รับไฟล์ภาพ -> ตรวจ Liveness -> ค้นหาใน DB -> คืนค่า User/Locker ID
    """
    try:
        # 1. อ่านไฟล์รูปภาพ
        image_bytes = await file.read()
        img = face_service.bytes_to_image(image_bytes)
        
        if img is None:
            logger.warning("Verify failed: Invalid image file.")
            return VerifyResponse(status="reject", reason="invalid_image")

        # 2. ให้ AI หาใบหน้า (Detect & Crop)
        face_obj, face_crop = face_service.detect_one_face(img)
        
        if face_obj is None:
            logger.info("Verify failed: No face detected.")
            return VerifyResponse(status="reject", reason="no_face_detected")

        # 3. Liveness Check (ป้องกันรูปถ่าย/มือถือ)
        is_real = face_service.check_liveness(face_crop)
        if not is_real:
            logger.warning("Verify failed: Spoof detected!")
            return VerifyResponse(status="reject", reason="spoof_detected")

        # 4. ค้นหาใน Qdrant
        # face_obj.embedding คือ Vector 512 ตัวเลข
        hit = qdrant_service.search_face(face_obj.embedding)

        if hit is None:
            logger.info("Verify failed: Unknown person (Score too low).")
            return VerifyResponse(status="reject", reason="unknown_person")

        # 5. เจอตัวจริง! (Success)
        user_id = hit.id
        locker_id = hit.payload.get("locker_id")
        
        if locker_id is None:
        # รู้จักหน้านะ แต่ไม่ได้จองตู้ไว้
            return VerifyResponse(status="reject", reason="no_booking_found", user_id=str(hit.id))
        
        logger.info(f"Verify Success! User: {user_id}, Locker: {locker_id}")
        
        return VerifyResponse(
            status="allow",
            user_id=str(user_id),
            locker_id=str(locker_id)
        )

    except Exception as e:
        logger.error(f"Internal Server Error during verify: {e}")
        # กรณี Server พังจริงๆ ให้ส่ง 500 กลับไป
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error processing image"
        )

# ---------------------------------------------------------
# 2. ENROLL ENDPOINT (สำหรับลงทะเบียนผ่านเว็บ/แอป)
# ---------------------------------------------------------
@router.post("/enroll", response_model=EnrollResponse)
async def enroll_face(
    user_id: int = Form(...),    # รับเป็น Form Data
    locker_id: str = Form(...),  # รับเป็น Form Data
    file: UploadFile = File(...)
):
    """
    รับไฟล์ภาพ + ID -> แปลงเป็น Vector -> บันทึกลง DB
    """
    logger.info(f"Enrolling User: {user_id} for Locker: {locker_id}")
    
    try:
        # 1. แปลงไฟล์ภาพ
        image_bytes = await file.read()
        img = face_service.bytes_to_image(image_bytes)
        
        if img is None:
            raise HTTPException(400, "Invalid image file")

        # 2. หาใบหน้า (Enrollment ควรเข้มงวด ต้องเจอหน้าชัดๆ)
        face_obj, _ = face_service.detect_one_face(img)
        
        if face_obj is None:
            raise HTTPException(400, "No face detected in the image. Please try again.")

        # 3. บันทึกลง Qdrant
        # แปลง embedding (numpy array) เป็น list ปกติก่อนส่งให้ JSON
        embedding_list = face_obj.embedding.tolist()
        
        success = qdrant_service.upsert_face(user_id, locker_id, embedding_list)
        
        if not success:
            raise HTTPException(500, "Failed to save to database")

        return EnrollResponse(
            status="success", 
            message=f"User {user_id} enrolled successfully."
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Enrollment error: {e}")
        raise HTTPException(500, f"Enrollment failed: {str(e)}")