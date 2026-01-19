from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.database import engine
from app.models import Base # Ensure models are imported so Alembic sees them

app = FastAPI(title="Attendance AI System")

# Include Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Attendance AI System is running"}

# Note: In production, use Alembic for migrations instead of startup_event
# If you strictly want auto-create for dev/testing:
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
