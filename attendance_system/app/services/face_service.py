import cv2
import numpy as np
import uuid
from insightface.app import FaceAnalysis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings

class FaceService:
    def __init__(self):
        # Initialize InsightFace
        self.face_app = FaceAnalysis(name='buffalo_l')
        self.face_app.prepare(ctx_id=0, det_size=settings.DET_SIZE)
        
        # Initialize Qdrant
        self.qdrant = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.qdrant.collection_exists(settings.COLLECTION_NAME):
            self.qdrant.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )

    def get_embedding(self, file_bytes: bytes):
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        faces = self.face_app.get(img)
        if not faces:
            raise ValueError("No face detected")
        return faces[0].embedding

    def save_face_vector(self, student_uuid: uuid.UUID, embedding: np.ndarray, metadata: dict):
        self.qdrant.upsert(
            collection_name=settings.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(student_uuid),
                    vector=embedding.tolist(),
                    payload=metadata
                )
            ]
        )

    def search_face(self, embedding: np.ndarray):
        search_result = self.qdrant.query_points(
            collection_name=settings.COLLECTION_NAME,
            query=embedding.tolist(),
            limit=1,
            score_threshold=0.5
        )
        if not search_result.points:
            return None
        return search_result.points[0]

# Singleton instance
face_service = FaceService()