import insightface
import cv2

class FaceDetector:
    def __init__(self):
        self.app = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )
        self.app.prepare(ctx_id=-1)

    def detect(self, frame):
        faces = self.app.get(frame)
        if not faces:
            return None

        face = faces[0]
        x1, y1, x2, y2 = map(int, face.bbox)
        face_crop = frame[y1:y2, x1:x2]
        return face_crop
