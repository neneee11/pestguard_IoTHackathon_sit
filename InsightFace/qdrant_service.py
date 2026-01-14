from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter
import uuid

client = QdrantClient(url="http://localhost:6333")

COLLECTION = "faces"


def init_collection():
    collections = client.get_collections().collections
    if COLLECTION not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=512,  # InsightFace embedding
                distance=Distance.COSINE
            )
        )


def insert_face(embedding, user_id: str):
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"user_id": user_id}
            )
        ]
    )


def search_face(embedding, limit=1):
    result = client.query_points(
        collection_name=COLLECTION,
        query=embedding,
        limit=limit
    )
    return result.points
# เรียกใช้ตอนเริ่มระบบ