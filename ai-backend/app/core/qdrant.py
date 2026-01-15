from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333
        )
        self.collection = "faces"
        self._init_collection()

    def _init_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=512,
                    distance=Distance.COSINE
                )
            )

    def add_face(self, embedding, payload: dict):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload=payload
        )
        self.client.upsert(
            collection_name=self.collection,
            points=[point]
        )

    def search(self, embedding, limit=1):
        result = self.client.search(
            collection_name=self.collection,
            query_vector=embedding.tolist(),
            limit=limit
        )
        return result
