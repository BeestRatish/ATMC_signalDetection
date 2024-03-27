import cv2

# Load the Haar cascade classifiers
stop_cascade = cv2.CascadeClassifier('stop_sign.xml')
light_cascade = cv2.CascadeClassifier('traffic_light.xml')

# Initialize the camera (adjust camera index if needed)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Reduce frame resolution for faster processing
    resized_frame = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)

    # Detect stop signs
    stop_signs = stop_cascade.detectMultiScale(resized_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Detect traffic lights
    lights = light_cascade.detectMultiScale(resized_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected stop signs and traffic lights
    for (x, y, w, h) in stop_signs:
        cv2.rectangle(frame, (2*x, 2*y), (2*(x+w), 2*(y+h)), (255, 0, 0), 2)
        cv2.putText(frame, 'Stop Sign', (2*x, 2*y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    for (x, y, w, h) in lights:
        cv2.rectangle(frame, (2*x, 2*y), (2*(x+w), 2*(y+h)), (0, 255, 0), 2)
        cv2.putText(frame, 'Traffic Light', (2*x, 2*y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Detection', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
