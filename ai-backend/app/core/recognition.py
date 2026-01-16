import insightface
import numpy as np

class FaceRecognizer:
    def __init__(self):
        self.app = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )
        self.app.prepare(ctx_id=-1)

    def get_embedding(self, face_crop):
        faces = self.app.get(face_crop)
        if not faces:
            return None
        emb = faces[0].embedding
        return emb / np.linalg.norm(emb)
