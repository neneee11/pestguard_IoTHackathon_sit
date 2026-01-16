#import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Face Locker Access Control"
    VERSION: str = "1.0.0"
    
    # --- Qdrant Database Config ---
    # ค่า Default คือ localhost สำหรับรันเทสบนเครื่อง
    # แต่เมื่อรันบน Docker เราจะแก้ค่านี้ผ่าน .env เป็นชื่อ service (เช่น qdrant_db)
    QDRANT_HOST: str = "localhost" 
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "face_vectors"
    
    # --- AI Model Config ---
    # ความเหมือนขั้นต่ำ (0.0 - 1.0) ยิ่งมากยิ่งแม่นแต่ผ่านยาก
    FACE_SIMILARITY_THRESHOLD: float = 0.75 
    
    # ความมั่นใจว่าเป็นคนจริง (0.0 - 1.0)
    ANTI_SPOOF_THRESHOLD: float = 0.70
    
    # Path ของโมเดล (ควรวางไว้ในโฟลเดอร์ resources)
    ANTI_SPOOF_MODEL_PATH: str = "resources/anti_spoof_model.jit"
    
    # --- System Config ---
    # ใช้ 'cuda' ถ้ามี NVIDIA GPU, หรือ 'cpu' ถ้าไม่มี
    DEVICE: str = "cpu" 

    class Config:
        # บอกให้ Pydantic ไปอ่านค่าจากไฟล์ .env (ถ้ามี)
        env_file = ".env"
        env_file_encoding = "utf-8"

# สร้าง Instance เดียวเพื่อเรียกใช้ทั้งโปรแกรม
settings = Settings()