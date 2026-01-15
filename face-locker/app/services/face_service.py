import cv2
import numpy as np
import torch
import logging
import os
from insightface.app import FaceAnalysis
from app.config import settings

# Setup Logger
logger = logging.getLogger(__name__)

class AntiSpoofModel:
    """Class สำหรับจัดการโมเดลตรวจสอบคนจริง/รูปถ่าย"""
    def __init__(self):
        self.model = None
        self.device = torch.device(settings.DEVICE if torch.cuda.is_available() else "cpu")

    def load(self, model_path: str):
        if not os.path.exists(model_path):
            logger.warning(f"⚠️ Anti-spoof model not found at {model_path}. Liveness check might fail.")
            # ใน Production อาจจะ throw error หรือปล่อยผ่านโดย disable liveness
            return

        try:
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
            logger.info(f"✅ Anti-Spoof model loaded on {self.device}")
        except Exception as e:
            logger.error(f"❌ Failed to load Anti-Spoof model: {e}")
            raise e

    def preprocess(self, face_crop):
        """เตรียมรูปภาพให้เข้ากับโมเดล (Resize -> Transpose -> Normalize)"""
        # MiniFASNet ส่วนใหญ่ใช้ 80x80
        img = cv2.resize(face_crop, (80, 80)) 
        img = img.transpose((2, 0, 1)) # HWC -> CHW
        img = torch.from_numpy(img).float().div(255.0).unsqueeze(0)
        return img.to(self.device)

    def is_real(self, face_crop) -> bool:
        if self.model is None:
            logger.warning("Anti-Spoof model is not loaded! Skipping check (Returning True).")
            return True # Fail-safe: ถ้าไม่มีโมเดล ยอมให้ผ่านไปก่อน (หรือจะ False ก็ได้แล้วแต่นโยบาย)

        try:
            inp = self.preprocess(face_crop)
            with torch.no_grad():
                pred = self.model(inp)
                score = torch.softmax(pred, dim=1)[0][1].item()
            
            return score > settings.ANTI_SPOOF_THRESHOLD
        except Exception as e:
            logger.error(f"Error during liveness check: {e}")
            return False

class FaceService:
    """Service หลักที่รวบรวมฟังก์ชันเกี่ยวกับใบหน้า"""
    def __init__(self):
        self.app = None
        self.anti_spoof = AntiSpoofModel()
    
    def load_models(self):
        """โหลดโมเดลทั้งหมด (ถูกเรียกจาก main.py ตอน start server)"""
        logger.info(f"Loading InsightFace model with device: {settings.DEVICE}...")
        
        # เลือก Provider ตาม Hardware
        providers = ['CUDAExecutionProvider'] if settings.DEVICE == 'cuda' else ['CPUExecutionProvider']
        
        try:
            # โหลด InsightFace (Buffalo_L คือโมเดลที่มีความแม่นยำสูง)
            self.app = FaceAnalysis(name="buffalo_l", providers=providers)
            self.app.prepare(ctx_id=0 if settings.DEVICE == 'cuda' else -1, det_size=(640, 640))
            logger.info("✅ InsightFace model loaded.")

            # โหลด Anti-Spoof Model
            self.anti_spoof.load(settings.ANTI_SPOOF_MODEL_PATH)
            
        except Exception as e:
            logger.error(f"❌ Critical Error loading models: {e}")
            raise e

    def bytes_to_image(self, image_bytes: bytes):
        """Helper: แปลง Bytes เป็น OpenCV Image"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None

    def detect_one_face(self, img):
        """
        หาใบหน้าในรูป 
        Return: (face_object, face_crop_image) หรือ (None, None)
        """
        if self.app is None:
            raise RuntimeError("Face Models are not loaded! Check startup logs.")

        faces = self.app.get(img)
        
        if not faces:
            return None, None

        # เลือกใบหน้าที่ใหญ่ที่สุด (กรณีมีหลายคนในเฟรม)
        target_face = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)[0]
        
        # Crop ภาพใบหน้าเพื่อส่งไปตรวจ Liveness
        bbox = target_face.bbox.astype(int)
        h, w, _ = img.shape
        x1, y1 = max(0, bbox[0]), max(0, bbox[1])
        x2, y2 = min(w, bbox[2]), min(h, bbox[3])
        face_crop = img[y1:y2, x1:x2]

        return target_face, face_crop

    def check_liveness(self, face_crop) -> bool:
        """Wrapper สำหรับเรียก Anti-Spoof"""
        return self.anti_spoof.is_real(face_crop)

# Create Singleton Instance
# บรรทัดนี้สำคัญ: เราสร้าง object ไว้เลยเพื่อให้ไฟล์อื่น import ไปใช้ตัวเดียวกัน
face_service = FaceService()