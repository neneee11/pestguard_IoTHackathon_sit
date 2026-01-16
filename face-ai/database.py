# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base

# เปลี่ยน user, password, dbname ตามจริง
DATABASE_URL = "postgresql+asyncpg://ai_user:NewStrongPassword%40123@10.4.41.250/attendance_ai"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency สำหรับ FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()