import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Config (จะเขียนในขั้นตอนถัดไป)
from app.config import settings

# Import Router (ตัวจัดการ URL ที่จะเขียนใน app/api/routes.py)
from app.api.routes import router as api_router

# Import Service Instances (ตัวแปร Global ที่เราจะสั่งให้โหลดโมเดล)
from app.services.face_service import face_service
from app.services.vector_db import qdrant_service

# 1. Setup Logging (เพื่อให้เห็น Log เวลาอยู่บน Docker)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 2. Lifespan Manager (ทำงานตอน Start/Stop Server)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ZONE ---
    logger.info("🚀 Server starting... Initializing resources.")
    
    try:
        # A. โหลดโมเดล AI เข้า RAM (InsightFace + AntiSpoof)
        # ขั้นตอนนี้อาจใช้เวลา 5-10 วินาที
        logger.info("⏳ Loading AI Models...")
        face_service.load_models()
        logger.info("✅ AI Models loaded successfully.")

        # B. เชื่อมต่อ Qdrant และเช็คว่ามี Collection หรือยัง
        logger.info("⏳ Connecting to Qdrant Database...")
        qdrant_service.init_collection()
        logger.info("✅ Database connected and collection verified.")
        
    except Exception as e:
        logger.error(f"❌ Critical Error during startup: {e}")
        raise e # ถ้าโหลดโมเดลไม่ผ่าน ให้ Server พังไปเลย (ดีกว่ารันแล้วทำงานไม่ได้)

    yield # จุดที่ Server ทำงานปกติรับ Request

    # --- SHUTDOWN ZONE ---
    logger.info("🛑 Server shutting down...")
    # (ถ้ามีการเชื่อมต่อ Database ค้างไว้ สั่งปิดตรงนี้ได้)

# 3. Create App Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan # ผูกฟังก์ชัน startup/shutdown
)

# 4. Add Middleware (สำคัญสำหรับ IoT/Web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # ใน Production จริงควรระบุ IP ถ้าทำได้ (แต่ * สะดวกสุดสำหรับ IoT)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Register Routers (นำเข้า API Endpoints)
app.include_router(api_router, prefix="/api/v1")

# 6. Health Check Endpoint (เอาไว้ให้ Docker เช็คว่า Server ตายหรือยัง)
@app.get("/")
async def health_check():
    return {
        "status": "online", 
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    # ใช้สำหรับ Debug บนเครื่อง (Production จะรันผ่าน Docker/Uvicorn command)
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)