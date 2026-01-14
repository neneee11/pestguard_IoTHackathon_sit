import cv2, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from face_model import get_embedding

client = QdrantClient("http://localhost:6333")

img = cv2.imread("person.jpg")
embedding = get_embedding(img)

if embedding is None:
    raise Exception("No face detected")

client.upsert(
    collection_name="faces",
    points=[
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={
                "person_id": "EMP001",
                "name": "Somchai",
                "role": "staff",
                "active": True
            }
        )
    ]
)

print("Face registered")
