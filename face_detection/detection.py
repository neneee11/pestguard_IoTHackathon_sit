import cv2
from ultralytics import YOLO

class RealTimeDetector:
    def __init__(self, model=r'C:\Users\chinn\Desktop\nene\pestguard_IoTHackathon_sit\ai\models\yolov8_face_detection.pt', conf=0.5):
        self.model = YOLO(model)
        self.conf_threshold = conf
        
    def process_frame(self, frame):
        results = self.model(frame, conf=self.conf_threshold)
        annotated_frame = results[0].plot()
        return annotated_frame
    
def open_camera(camera_index=0):
    detector = RealTimeDetector()
    # Try to open the camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return

    print("Press 'q' to exit the camera window.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to read frame from camera.")
            break
        
        processsed = detector.process_frame(frame)
        # Display the frame
        cv2.imshow("Live Camera Feed", processsed)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()