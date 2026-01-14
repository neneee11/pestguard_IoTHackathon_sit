import cv2
import requests
import numpy as np

# --- CONFIGURATION ---
# URL ของกล้อง IP Camera (ตามที่คุณให้มา)
IP_CAMERA_URL = "rtsp://10.250.80.155:8080/h264_ulaw.sdp"

# URL ของ Server API (ตรวจสอบ IP และ Port ให้ถูกต้อง)
# ถ้า Run Server เครื่องเดียวกันใช้ localhost, ถ้าคนละเครื่องต้องใช้ IP ของเครื่อง Server
API_URL = "http://127.0.0.1:8000/identify" 

# --- MAIN PROGRAM ---
cap = cv2.VideoCapture(IP_CAMERA_URL)

if not cap.isOpened():
    print("Error: Cannot connect to IP camera")
    exit()

print("Camera connected.")
print("Press 's' to SCAN face.")
print("Press 'q' to QUIT.")

last_result_text = "Ready"
last_color = (255, 255, 255) # White

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # แสดงข้อความสถานะบนหน้าจอ
    cv2.putText(frame, last_result_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1, last_color, 2, cv2.LINE_AA)

    cv2.imshow("IP Camera Stream", frame)

    key = cv2.waitKey(1) & 0xFF

    # กด 'q' เพื่อออก
    if key == ord('q'):
        break
    
    # กด 's' เพื่อส่งรูปไปตรวจ (Scan)
    elif key == ord('s'):
        print("Sending image to server...")
        last_result_text = "Scanning..."
        
        # 1. แปลงภาพ OpenCV (Array) เป็นไฟล์ JPG (Bytes)
        success, encoded_image = cv2.imencode('.jpg', frame)
        
        if success:
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

cap.release()
cv2.destroyAllWindows()