import torch
import cv2
import numpy as np

class AntiSpoofService:
    def __init__(self):
        self.device = "cpu"
        self.model = torch.jit.load(
            "models/antispoof/antispoof_cpu.pt",
            map_location=self.device
        )
        self.model.eval()

    def _preprocess(self, face_crop):
        face = cv2.resize(face_crop, (80, 80))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = face.astype(np.float32) / 255.0
        face = np.transpose(face, (2, 0, 1))  # CHW
        return face

    def check(self, face_crop) -> float:
        x = self._preprocess(face_crop)
        with torch.no_grad():
            tensor = torch.from_numpy(x).unsqueeze(0)
            out = self.model(tensor)
            prob_real = torch.softmax(out, dim=1)[0][1].item()
        return prob_real
