from qdrant_client import QdrantClient
from face_model import get_embedding
import cv2

client = QdrantClient("http://localhost:6333")

img = cv2.imread("test.jpg")
embedding = get_embedding(img)

result = client.search(
    collection_name="faces",
    query_vector=embedding.tolist(),
    limit=1
)

if result and result[0].score > 0.85:
    print("MATCH:", result[0].payload)
else:
    print("UNKNOWN")
