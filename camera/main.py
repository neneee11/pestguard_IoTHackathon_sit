import uvicorn
import numpy as np
import cv2
import threading
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse

app = FastAPI()

# ==========================================
# CONFIGURATION
# ==========================================
HOST_IP = '0.0.0.0'
HOST_PORT = 8080
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
EXPECTED_SIZE = IMG_WIDTH * IMG_HEIGHT * 2 

# ตัวแปร Global สำหรับเก็บภาพล่าสุดที่ได้รับมา
latest_frame = None
frame_lock = threading.Lock() # ป้องกันการอ่าน/เขียนพร้อมกัน

# ==========================================
# ส่วนรับภาพจาก ESP32 (POST)
# ==========================================
@app.post("/upload")
async def upload_image(request: Request):
    global latest_frame
    
    # 1. รับข้อมูล Raw
    raw_data = await request.body()
    
    if len(raw_data) != EXPECTED_SIZE:
        raise HTTPException(status_code=400, detail="Data size mismatch")

    try:
        # 2. แปลงเป็น Image
        arr = np.frombuffer(raw_data, dtype=np.uint8)
        arr = arr.reshape((IMG_HEIGHT, IMG_WIDTH, 2))
        bgr_img = cv2.cvtColor(arr, cv2.COLOR_YUV2BGR_YUYV)

        # ---------------------------------------------------------
        # [จุดใส่ AI] คุณสามารถนำ YOLO/InsightFace มาใส่ตรงนี้
        # ---------------------------------------------------------
        # ตัวอย่าง: วาดสี่เหลี่ยมจำลอง (สมมติว่าเป็นหน้าคนที่ detect ได้)
        # cv2.rectangle(bgr_img, (100, 100), (500, 500), (0, 255, 0), 3)
        # cv2.putText(bgr_img, "User Detected", (100, 90), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # ---------------------------------------------------------

        # 3. อัปเดตภาพล่าสุดใส่ตัวแปร Global
        with frame_lock:
            latest_frame = bgr_img.copy()

        return {"status": "ok"}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

# ==========================================
# ส่วนแสดงผลบนเว็บ (GET)
# ==========================================
def generate_frames():
    """ฟังก์ชัน Generator สำหรับส่งภาพต่อเนื่องแบบ MJPEG"""
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            
            # Encode ภาพเป็น JPEG เพื่อส่งผ่านเว็บ
            # ลดคุณภาพลงนิดหน่อย (quality=50) เพื่อความลื่นไหล
            ret, buffer = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            frame_bytes = buffer.tobytes()

        # ส่งข้อมูลตามมาตรฐาน Multipart MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    """Endpoint สำหรับดึง Video Stream"""
    return StreamingResponse(generate_frames(), 
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
async def index():
    """หน้าเว็บหลัก HTML"""
    return """
    <html>
        <head>
            <title>ESP32 AI Camera Stream</title>
            <style>
                body { background-color: #1a1a1a; color: white; text-align: center; font-family: sans-serif; }
                img { border: 5px solid #4CAF50; max-width: 90%; height: auto; }
            </style>
        </head>
        <body>
            <h1>Live Feed: ESP32 + FastAPI</h1>
            <img src="/video_feed" />
        </body>
    </html>
    """

if __name__ == "__main__":
    # รัน Server
    uvicorn.run(app, host=HOST_IP, port=HOST_PORT)