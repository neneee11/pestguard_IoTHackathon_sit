import insightface
import cv2
import numpy as np

app = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(ctx_id=0, det_size=(640, 640))


'''def get_embedding(image):
    """
    image: numpy array (BGR, OpenCV)
    return: 512-d embedding or None
    """
    faces = app.get(image)
    if not faces:
        return None
    return faces[0].embedding'''

def get_embedding(image_bytes: bytes):
    # แปลง bytes → image
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    faces = app.get(img)

    if len(faces) == 0:
        raise ValueError("No face detected")

    # ใช้หน้าหลัก
    embedding = faces[0].embedding
    return embedding.tolist()