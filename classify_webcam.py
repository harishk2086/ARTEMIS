from ultralytics import YOLO
import cv2
import serial
import time

# -----------------------------
# Arduino Serial Port
# -----------------------------
arduino = serial.Serial("COM3", 115200, timeout=0.1)
time.sleep(2)

# -----------------------------
# Load YOLO Model
# -----------------------------
model = YOLO("model/best.pt")

# -----------------------------
# Open Webcam
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Webcam not found.")
    exit()

# -----------------------------
# Variables
# -----------------------------
last_command = ""
vibration = 0
status = "SAFE"

while True:

    # ------------------------------------
    # Read MPU6050 vibration from Arduino
    # ------------------------------------
    while arduino.in_waiting:
        try:
            line = arduino.readline().decode().strip()

            if line.startswith("VIB:"):
                vibration = int(line.split(":")[1])

        except:
            pass

    # -----------------------------
    # Read webcam frame
    # -----------------------------
    ret, frame = cap.read()

    if not ret:
        break

    # -----------------------------
    # Run YOLO Classification
    # -----------------------------
    results = model.predict(frame, verbose=False)

    probs = results[0].probs

    class_id = probs.top1
    confidence = probs.top1conf.item()

    class_name = model.names[class_id]

    # -----------------------------
    # Sensor Fusion Logic
    # -----------------------------
    if class_name.lower() == "crack":

        if vibration > 5000:
            status = "DANGER"
            command = "R"
        else:
            status = "WARNING"
            command = "Y"

    elif class_name.lower() == "vegetation":

        status = "WARNING"
        command = "Y"

    else:

        status = "SAFE"
        command = "G"

    # -----------------------------
    # Send command to Arduino
    # -----------------------------
    if command != last_command:
        arduino.write(command.encode())
        last_command = command
        print("Sent:", command)

    # -----------------------------
    # Display Information
    # -----------------------------
    cv2.putText(
        frame,
        f"{class_name} ({confidence*100:.1f}%)",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Vibration : {vibration}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    if status == "SAFE":
        color = (0, 255, 0)

    elif status == "WARNING":
        color = (0, 255, 255)

    else:
        color = (0, 0, 255)

    cv2.putText(
        frame,
        f"Status : {status}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )

    cv2.imshow("ARTEMIS AI", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()