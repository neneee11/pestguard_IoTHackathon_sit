from fastapi import APIRouter, UploadFile, File
import cv2
import numpy as np

from app.services.face_detect import FaceDetector
from app.core.recognition import FaceRecognizer
from app.core.qdrant import QdrantService

router = APIRouter()

detector = FaceDetector()
recognizer = FaceRecognizer()
qdrant = QdrantService()

@router.post("/enroll")
async def enroll(user_id: str, file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    face = detector.detect(img)
    if face is None:
        return {"status": "fail", "reason": "no_face"}

    emb = recognizer.get_embedding(face)
    if emb is None:
        return {"status": "fail", "reason": "embedding_fail"}

    qdrant.add_face(
        embedding=emb,
        payload={"user_id": user_id}
    )

    return {"status": "success", "user_id": user_id}
