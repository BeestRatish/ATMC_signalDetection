import cv2
import threading

class DetectorThread(threading.Thread):
    def __init__(self, cascade_file, frame, roi):
        super().__init__()
        self.cascade = cv2.CascadeClassifier(cascade_file)
        self.frame = frame
        self.roi = roi
        self.results = []

    def run(self):
        gray_roi = cv2.cvtColor(self.frame[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]], cv2.COLOR_BGR2GRAY)
        objects = self.cascade.detectMultiScale(gray_roi, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in objects:
            self.results.append((x+self.roi[0], y+self.roi[1], x+w+self.roi[0], y+h+self.roi[1]))

# Initialize camera (adjust camera index if needed)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Define ROIs for stop sign and traffic light detection
    stop_roi = (0, 0, frame.shape[1]//2, frame.shape[0]//2)
    light_roi = (frame.shape[1]//2, 0, frame.shape[1], frame.shape[0]//2)

    # Create detector threads for stop signs and traffic lights
    stop_thread = DetectorThread('stop_sign.xml', frame, stop_roi)
    light_thread = DetectorThread('traffic_light.xml', frame, light_roi)

    # Start detection threads
    stop_thread.start()
    light_thread.start()

    # Wait for threads to finish
    stop_thread.join()
    light_thread.join()

    # Get results from threads
    stop_signs = stop_thread.results
    traffic_lights = light_thread.results

    # Draw rectangles for detected objects
    for (x1, y1, x2, y2) in stop_signs:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, 'Stop Sign', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    for (x1, y1, x2, y2) in traffic_lights:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, 'Traffic Light', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Detection', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
