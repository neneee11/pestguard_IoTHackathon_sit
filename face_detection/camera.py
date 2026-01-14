import cv2
from ultralytics import YOLO
import threading
import requests
import time

# --- การตั้งค่า API ---
API_URL = "http://localhost:8000/identify"

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

def send_face_to_api( face_image):
        """ฟังก์ชันสำหรับส่งภาพไป Server (รันใน Thread แยก)"""
        try:
            # 1. แปลงภาพ (Numpy) เป็นไบต์ (JPG)
            _, img_encoded = cv2.imencode('.jpg', face_image)
            image_bytes = img_encoded.tobytes()

            # 2. เตรียม Payload
            files = {'file': ('face.jpg', image_bytes, 'image/jpeg')}
            data = {'device_id': 'esp32_cam_01', 'timestamp': time.time()}

            # 3. ยิง API (POST Request)
            print(">> กำลังส่งภาพไปที่ Server...")
            response = requests.post(API_URL, files=files, data=data, timeout=5)
            
            # 4. ดูผลลัพธ์
            if response.status_code == 200:
                print(f"✅ Upload สำเร็จ: {response.text}")
            else:
                print(f"❌ Upload ล้มเหลว: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error sending API: {e}")

def open_camera():
    # เปลี่ยน Path เป็นโมเดลของคุณ
    model_path = r'C:\Users\chinn\Desktop\nene\pestguard_IoTHackathon_sit\ai\models\yolov8_face_detection.pt'
    
    cropper = FaceCropper(model_path)
    
    #ip_camera_url = "rtsp://10.250.80.155:8080/h264_ulaw.sdp"
    #cap = cv2.VideoCapture(ip_camera_url)
    cap = cv2.VideoCapture(0)

    print("Opening camera... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        if ret:
            try:
                # 2. เตรียมข้อมูลส่ง HTTP POST
                files = {'file': ('image.jpg', encoded_image.tobytes(), 'image/jpeg')}
                
                # 3. ยิงไปที่ Server
                response = requests.post(API_URL, files=files)
                
                # 4. อ่านผลลัพธ์
                if response.status_code == 200:
                    data = response.json()
                    if data.get("match"):
                        user_id = data.get("user_id", "Unknown")
                        score = data.get("score", 0.0)
                        print(f"✅ MATCH FOUND: {user_id} ({score:.2f})")
                        last_result_text = f"User: {user_id} ({int(score*100)}%)"
                        last_color = (0, 255, 0) # Green
                    else:
                        reason = data.get("reason", "Unknown")
                        print(f"❌ NO MATCH: {reason}")
                        last_result_text = "Unknown Face"
                        last_color = (0, 0, 255) # Red
                
                elif response.status_code == 400:
                    print("⚠️ Server Message: No face detected")
                    last_result_text = "No Face Detected"
                    last_color = (0, 165, 255) # Orange
                
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    last_result_text = "Server Error"
                    last_color = (0, 0, 255)

            except Exception as e:
                print(f"Connection Error: {e}")
                last_result_text = "Connection Failed"
                last_color = (0, 0, 255)

        # เรียกฟังก์ชันประมวลผล
        main_frame, faces = cropper.process_and_crop(frame)

        # แสดงภาพหลัก (ที่มีกรอบเขียว)
        cv2.imshow("YOLO Face Detection", main_frame)

        # --- แสดงภาพที่ Crop มาได้ (แยกหน้าต่าง) ---
        for i, face in enumerate(faces):
            # โชว์หน้าต่างแยกของแต่ละหน้าที่เจอ
            cv2.imshow(f"Cropped Face {i+1}", face)
            
            # [Tips] ตรงนี้แหละครับที่คุณจะเอา 'face' ไปส่ง API
            #for face in faces:
                #send_face_to_api(face)
            #thread = threading.Thread(target=res, args=(face,))
            #thread.start() 

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()