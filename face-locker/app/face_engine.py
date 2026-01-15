import cv2
import numpy as np
from insightface.app import FaceAnalysis
import numpy as np

import torch

class AntiSpoofModel:
    def __init__(self, model_path, device="cpu"):
        # โหลดโมเดล Torch Script
        self.device = device
        self.model = torch.jit.load(model_path, map_location=device)
        self.model.eval()

    def preprocess(self, face_crop):
        """เตรียมรูปภาพให้พร้อมสำหรับเข้าโมเดล (สำคัญมาก)"""
        # 1. Resize เป็นขนาดที่โมเดลต้องการ (เช่น 80x80 สำหรับ MiniFASNet ส่วนใหญ่)
        # หมายเหตุ: ลองเช็ค Spec โมเดลที่คุณโหลดมาว่าใช้ input size เท่าไหร่
        img = cv2.resize(face_crop, (80, 80)) 
        
        # 2. แปลงสี BGR (OpenCV) -> RGB (Torch) (บางโมเดลอาจไม่ต้องใช้ บรรทัดนี้ขึ้นอยู่กับโมเดล)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 3. Transpose (H, W, C) -> (C, H, W) ตาม format ของ PyTorch
        img = img.transpose((2, 0, 1))
        
        # 4. แปลงเป็น Tensor และ Normalize (0-1)
        img = torch.from_numpy(img).float().div(255.0).unsqueeze(0)
        return img.to(self.device)

    def is_real(self, face_crop):
        # ป้องกันกรณี crop แล้วได้ภาพว่างเปล่า
        if face_crop is None or face_crop.size == 0:
            return False

        input_tensor = self.preprocess(face_crop)
        
        with torch.no_grad():
            pred = self.model(input_tensor)
            # โมเดลส่วนใหญ่: class 0 = Spoof, class 1 = Real
            score = torch.softmax(pred, dim=1)[0][1].item()
        
        # คืนค่า True ถ้าความมั่นใจว่าเป็น "คนจริง" เกิน 0.7
        return score > 0.7

class FaceEngine:
    def __init__(self):
        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def analyze_face(self, img_array):
        """
        รับภาพ OpenCV (numpy) แล้วส่งคืน list ของ Face Objects
        เพื่อให้ข้างนอกเลือกว่าจะเอา face ไหนไปตรวจ Liveness
        """
        faces = self.app.get(img_array)
        return faces
