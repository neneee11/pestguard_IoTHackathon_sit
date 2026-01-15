from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

#client = QdrantClient(host="localhost", port=6333)
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "face_vectors"

def init_collection():
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        )

def upsert_face(user_id: str, locker_id: str, embedding):
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=user_id,
                vector=embedding.tolist(),
                payload={"locker_id": locker_id}
            )
        ]
    )

def search_face(embedding, threshold=0.8):
    result = client.query_points(
        collection_name=COLLECTION,
        query=embedding.tolist(),
        limit=1,
        score_threshold=threshold
    ).points

    if not result:
        return None

    hit = result[0]
    if hit.score >= threshold:
        return hit
    return None
