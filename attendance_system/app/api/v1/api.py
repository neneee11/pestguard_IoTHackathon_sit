from fastapi import APIRouter
from app.api.v1.endpoints import students, attendance

api_router = APIRouter()
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])