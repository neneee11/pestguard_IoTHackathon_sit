from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------
# Response Schemas (ข้อมูลที่ Server ส่งกลับ)
# ---------------------------------------------------------

class VerifyResponse(BaseModel):
    """
    Format ที่ส่งกลับให้ ESP32 หลังจากสแกนหน้า
    """
    status: str              # "allow" หรือ "reject"
    reason: Optional[str] = None  # เหตุผลถ้า reject (เช่น "spoof_detected", "unknown_person")
    user_id: Optional[str] = None # ID ของ user (ส่งมาเฉพาะตอน allow)
    locker_id: Optional[str] = None # เบอร์ตู้ (ส่งมาเฉพาะตอน allow)

class EnrollResponse(BaseModel):
    """
    Format ที่ส่งกลับหลังจากลงทะเบียนเสร็จ
    """
    status: str              # "success" หรือ "failed"
    message: str             # ข้อความแจ้งเตือน (เช่น "User 123 enrolled successfully")