import cv2

# Replace with your camera's RTSP or HTTP stream URL
# Example: "rtsp://username:password@192.168.1.100:554/stream"
ip_camera_url = "rtsp://10.250.80.155:8080/h264_ulaw.sdp"

# Open the video stream
cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print("Error: Cannot connect to IP camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("IP Camera Stream", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
