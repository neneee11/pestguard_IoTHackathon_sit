from fastapi import FastAPI
from app.api.access import router as access_router

app = FastAPI(
    title="Commercial Face Access Control",
    version="1.0.0"
)

app.include_router(access_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok"}
