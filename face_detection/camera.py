import cv2
from ultralytics import YOLO

class FaceCropper:
    def __init__(self, model_path):
        # โหลดโมเดล YOLO (ใช้ path ของคุณ)
        self.model = YOLO(model_path)

    def process_and_crop(self, frame):
        # 1. ให้ YOLO หาตำแหน่ง (ปรับ conf ตามต้องการ)
        results = self.model(frame, conf=0.5, verbose=False)
        
        cropped_faces = [] # ลิสต์เก็บภาพใบหน้าที่ตัดมาได้
        annotated_frame = frame.copy() # ภาพสำหรับโชว์ (วาดกรอบ)

        # 2. วนลูปตามจำนวนหน้าที่เจอ
        for box in results[0].boxes:
            # ดึงพิกัด (x1, y1, x2, y2)
            coords = box.xyxy[0].cpu().numpy() # แปลงเป็น numpy array
            x1, y1, x2, y2 = map(int, coords)  # แปลงเป็น int

            # --- จุดสำคัญ: การ Crop ภาพ ---
            # ต้องเช็คขอบเขตไม่ให้ติดลบหรือเกินขนาดภาพ (กัน Error)
            h, w, _ = frame.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # ตัดภาพ: image[start_y:end_y, start_x:end_x]
            face_img = frame[y1:y2, x1:x2]
            
            # เก็บใส่ List ไว้ (เผื่อเอาไปส่ง API)
            if face_img.size > 0:
                cropped_faces.append(face_img)

            # วาดกรอบสี่เหลี่ยมบนภาพหลัก (เพื่อความสวยงามตอนโชว์)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return annotated_frame, cropped_faces

def open_camera():
    # เปลี่ยน Path เป็นโมเดลของคุณ
    model_path = r'C:\Users\chinn\Desktop\nene\pestguard_IoTHackathon_sit\ai\models\yolov8_face_detection.pt'
    
    cropper = FaceCropper(model_path)
    cap = cv2.VideoCapture(0)

    print("Opening camera... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # เรียกฟังก์ชันประมวลผล
        main_frame, faces = cropper.process_and_crop(frame)

        # แสดงภาพหลัก (ที่มีกรอบเขียว)
        cv2.imshow("YOLO Face Detection", main_frame)

        # --- แสดงภาพที่ Crop มาได้ (แยกหน้าต่าง) ---
        for i, face in enumerate(faces):
            # โชว์หน้าต่างแยกของแต่ละหน้าที่เจอ
            cv2.imshow(f"Cropped Face {i+1}", face)
            
            # [Tips] ตรงนี้แหละครับที่คุณจะเอา 'face' ไปส่ง API
            # send_to_api(face) 

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()