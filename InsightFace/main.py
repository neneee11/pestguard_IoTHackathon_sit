from fastapi import FastAPI,HTTPException, UploadFile, File
import cv2, numpy as np
from qdrant_client import QdrantClient
from face_model import get_embedding
from qdrant_service import init_collection, insert_face, search_face

app = FastAPI()

qdrant = QdrantClient(
    url="http://localhost:6333"
)

MATCH_THRESHOLD = 0.8

@app.get("/")
def root():
    return {"message": "API is working"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "pestguard-api"
    }

@app.get("/qdrant")
def test_qdrant():
    return qdrant.get_collections()

@app.post("/analyze")
def analyze(data: dict):
    return {
        "input": data,
        "result": "processing"
    }

@app.post("/register")
async def register_face(user_id: str, file: UploadFile = File(...)):
    image_bytes = await file.read()
    embedding = get_embedding(image_bytes)

    insert_face(embedding, user_id)
    existing = search_face(embedding)
    if existing and existing[0].score > 0.9:
        return {
            "status": "duplicate",
            "user_id": existing[0].payload["user_id"],
            "score": existing[0].score
        }
    
    return {"status": "registered", "user_id": user_id}

@app.post("/identify")
async def identify_face(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        with open("debug_received_image.jpg", "wb") as f:
            f.write(image_bytes)
        print("Save debug image: debug_received_image.jpg")

        embedding = get_embedding(image_bytes)

        results = search_face(embedding)

        if not results:
            return {"match": False}

        top = results[0]

        if top.score < MATCH_THRESHOLD:
            return {
                "match": False,
                "reason": "below_threshold",
                "score": top.score
            }
    
        return {
            "match": True,
            "user_id": top.payload["user_id"],
            "score": top.score
        }
    except ValueError as e:
        # ดักจับ Error "No face detected"
        if str(e) == "No face detected":
            raise HTTPException(status_code=400, detail="ไม่พบใบหน้าในรูปภาพ (No face detected)")
        else:
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        # ดักจับ Error อื่นๆ ทั่วไป
        raise HTTPException(status_code=500, detail="Internal Server Error")