import cv2
import serial
import time
import math
import os
import csv
from datetime import datetime
from ultralytics import YOLO


# ============================================================
# ARTEMIS
# AI RAILWAY TRACK MONITORING SYSTEM
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

MODEL_PATH = "model/best.pt"

ARDUINO_PORT = "COM6"

BAUD_RATE = 115200

CONFIDENCE_THRESHOLD = 0.40

# Arduino vibration threshold
VIBRATION_THRESHOLD = 20000

# Send CRACK command to Arduino every 0.5 seconds
CRACK_SEND_INTERVAL = 0.50

# Normal data logging interval
LOG_INTERVAL = 1.0

# Minimum time between saved abnormal images
IMAGE_COOLDOWN = 5.0

# Ultrasonic obstacle threshold
OBSTACLE_DISTANCE = 20.0


# ============================================================
# CREATE DETECTION FOLDER
# ============================================================

DETECTION_FOLDER = "detections"

os.makedirs(
    DETECTION_FOLDER,
    exist_ok=True
)


# ============================================================
# CSV FILE
# ============================================================

LOG_FILE = os.path.join(
    DETECTION_FOLDER,
    "ARTEMIS_log.csv"
)


# Create CSV with headings if it doesn't exist

if not os.path.exists(LOG_FILE):

    with open(
        LOG_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time",
            "YOLO Detection",
            "Confidence",
            "Severity",
            "IR",
            "Distance_cm",
            "Vibration",
            "Risk_Score",
            "Status",
            "Why_Alert",
            "Image"
        ])


# ============================================================
# LOAD YOLO
# ============================================================

print("Loading ARTEMIS YOLO model...")

try:

    model = YOLO(MODEL_PATH)

except Exception as e:

    print("ERROR: Could not load YOLO model")
    print(e)

    exit()


print("YOLO model loaded successfully!")


# ============================================================
# CONNECT ARDUINO
# ============================================================

arduino = None


try:

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD_RATE,
        timeout=0.1
    )

    time.sleep(2)

    print("Arduino CONNECTED")


except Exception as e:

    print("Arduino connection failed!")
    print(e)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Cannot open webcam")

    if arduino is not None:

        arduino.close()

    exit()


print("ARTEMIS SYSTEM STARTED")
print("Press Q to exit")


# ============================================================
# SENSOR VARIABLES
# ============================================================

ir_status = "WAITING"

distance = -1.0

acc_x = 0
acc_y = 0
acc_z = 0

gyro_x = 0
gyro_y = 0
gyro_z = 0


# ============================================================
# TIMERS
# ============================================================

last_crack_sent = 0

last_data_log = 0

last_image_saved = 0


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # ========================================================
    # READ CAMERA
    # ========================================================

    ret, frame = cap.read()


    if not ret:

        print("Failed to capture frame")

        break


    # ========================================================
    # YOLO INFERENCE
    # ========================================================

    results = model(
        frame,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )


    # ========================================================
    # MAKE WRITABLE COPY
    # ========================================================

    annotated_frame = frame.copy()


    frame_height, frame_width = (
        annotated_frame.shape[:2]
    )


    # ========================================================
    # YOLO VARIABLES
    # ========================================================

    detected_classes = []

    crack_detected = False

    crack_confidence = 0.0

    crack_box_area = 0

    best_crack_box = None


    # ========================================================
    # PROCESS YOLO BOXES
    # ========================================================

    if results[0].boxes is not None:

        for box in results[0].boxes:

            class_id = int(
                box.cls[0]
            )

            class_name = str(
                model.names[class_id]
            )

            confidence = float(
                box.conf[0]
            )


            # ------------------------------------------------
            # STORE CLASS
            # ------------------------------------------------

            if class_name not in detected_classes:

                detected_classes.append(
                    class_name
                )


            # ------------------------------------------------
            # BOX COORDINATES
            # ------------------------------------------------

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)


            # ------------------------------------------------
            # CRACK DETECTION
            # ------------------------------------------------

            if class_name.lower() == "crack":

                crack_detected = True


                if confidence > crack_confidence:

                    crack_confidence = confidence

                    crack_box_area = int(
                        max(0, x2 - x1)
                        *
                        max(0, y2 - y1)
                    )

                    best_crack_box = (
                        x1,
                        y1,
                        x2,
                        y2
                    )


    # ========================================================
    # DRAW YOLO BOXES MANUALLY
    #
    # This prevents the normal YOLO text labels
    # such as:
    #
    # vegetation 0.33
    # defectless 0.14
    #
    # from covering the screen.
    # ========================================================

    if results[0].boxes is not None:

        for box in results[0].boxes:

            class_id = int(
                box.cls[0]
            )

            class_name = str(
                model.names[class_id]
            )

            confidence = float(
                box.conf[0]
            )


            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)


            # Crack gets red box
            if class_name.lower() == "crack":

                box_color = (
                    0,
                    0,
                    255
                )

            else:

                box_color = (
                    255,
                    255,
                    0
                )


            # Draw bounding box

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                box_color,
                2
            )


            # Only display CRACK label.
            # Other classes are intentionally hidden.

            if class_name.lower() == "crack":

                label = (
                    "CRACK "
                    +
                    str(
                        round(
                            confidence * 100,
                            1
                        )
                    )
                    +
                    "%"
                )


                (
                    label_width,
                    label_height
                ), _ = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    2
                )


                label_y1 = max(
                    0,
                    y1 - label_height - 8
                )


                cv2.rectangle(
                    annotated_frame,
                    (x1, label_y1),
                    (
                        x1 + label_width + 10,
                        y1
                    ),
                    (0, 0, 255),
                    -1
                )


                cv2.putText(
                    annotated_frame,
                    label,
                    (
                        x1 + 5,
                        y1 - 5
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )


    # ========================================================
    # CRACK SEVERITY
    # ========================================================

    crack_severity = "NONE"


    if crack_detected:

        # Confidence-based severity

        if crack_confidence >= 0.85:

            crack_severity = "HIGH"

        elif crack_confidence >= 0.65:

            crack_severity = "MEDIUM"

        else:

            crack_severity = "LOW"


        # Bounding-box area can increase severity

        frame_area = (
            frame_width *
            frame_height
        )


        if frame_area > 0:

            crack_area_ratio = (
                crack_box_area /
                frame_area
            )


            if crack_area_ratio > 0.20:

                crack_severity = "HIGH"

            elif (
                crack_area_ratio > 0.08
                and
                crack_severity == "LOW"
            ):

                crack_severity = "MEDIUM"


    # ========================================================
    # READ ARDUINO
    # ========================================================

    if arduino is not None:

        try:

            while arduino.in_waiting > 0:

                data = (
                    arduino
                    .readline()
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                    .strip()
                )


                # ------------------------------------------------
                # SENSOR DATA
                # ------------------------------------------------

                if data.startswith("IR:"):

                    parts = data.split(",")


                    if len(parts) >= 8:

                        try:

                            # IR

                            ir_value = (
                                parts[0]
                                .split(":")[1]
                            )


                            if ir_value == "0":

                                ir_status = (
                                    "OBJECT DETECTED"
                                )

                            else:

                                ir_status = "CLEAR"


                            # Distance

                            distance = float(
                                parts[1]
                                .split(":")[1]
                            )


                            # Accelerometer

                            acc_x = int(
                                parts[2]
                                .split(":")[1]
                            )

                            acc_y = int(
                                parts[3]
                            )

                            acc_z = int(
                                parts[4]
                            )


                            # Gyroscope

                            gyro_x = int(
                                parts[5]
                                .split(":")[1]
                            )

                            gyro_y = int(
                                parts[6]
                            )

                            gyro_z = int(
                                parts[7]
                            )


                        except Exception:

                            pass


        except Exception:

            pass


    # ========================================================
    # SENSOR CONDITIONS
    # ========================================================

    obstacle_detected = False

    vibration_detected = False


    # ========================================================
    # IR
    # ========================================================

    if ir_status == "OBJECT DETECTED":

        obstacle_detected = True


    # ========================================================
    # ULTRASONIC
    # ========================================================

    if (
        distance > 0
        and
        distance < OBSTACLE_DISTANCE
    ):

        obstacle_detected = True


    # ========================================================
    # MPU6050 VIBRATION
    #
    # Use the same calculation as Arduino.
    # ========================================================

    vibration_value = (
        abs(acc_x)
        +
        abs(acc_y)
        +
        abs(acc_z)
    )


    if vibration_value > VIBRATION_THRESHOLD:

        vibration_detected = True


    # ========================================================
    # SEND YOLO CRACK TO ARDUINO
    # ========================================================

    current_time = time.time()


    if crack_detected:

        if (
            arduino is not None
            and
            current_time - last_crack_sent
            >= CRACK_SEND_INTERVAL
        ):

            try:

                arduino.write(
                    b"CRACK\n"
                )

                arduino.flush()

                last_crack_sent = (
                    current_time
                )

            except Exception:

                pass


    # ========================================================
    # SENSOR-FUSION RISK SCORE
    # ========================================================

    risk_score = 0


    # --------------------------------------------------------
    # YOLO CRACK
    # Maximum 50 points
    # --------------------------------------------------------

    if crack_detected:

        crack_points = int(
            crack_confidence * 50
        )

        risk_score += crack_points


    # --------------------------------------------------------
    # HIGH VIBRATION
    # 25 points
    # --------------------------------------------------------

    if vibration_detected:

        risk_score += 25


    # --------------------------------------------------------
    # OBSTACLE
    # 25 points
    # --------------------------------------------------------

    if obstacle_detected:

        risk_score += 25


    # Maximum 100

    risk_score = min(
        risk_score,
        100
    )


    # ========================================================
    # RISK STATUS
    # ========================================================

    if risk_score >= 75:

        risk_status = "CRITICAL"

    elif risk_score >= 50:

        risk_status = "HIGH RISK"

    elif risk_score >= 25:

        risk_status = "WARNING"

    else:

        risk_status = "NORMAL"


    # ========================================================
    # WHY ALERT
    # ========================================================

    reasons = []


    if crack_detected:

        reasons.append(
            "AI CRACK"
        )


    if obstacle_detected:

        reasons.append(
            "OBSTACLE"
        )


    if vibration_detected:

        reasons.append(
            "HIGH VIBRATION"
        )


    if len(reasons) == 0:

        why_alert = "NO ALERT"

    else:

        why_alert = " + ".join(
            reasons
        )


    # ========================================================
    # RIGHT SIDE INFORMATION PANEL
    # ========================================================

    panel_width = min(
        410,
        frame_width - 20
    )


    panel_height = min(
        430,
        frame_height - 20
    )


    panel_x1 = (
        frame_width
        -
        panel_width
        -
        10
    )


    panel_y1 = 10


    panel_x2 = (
        frame_width - 10
    )


    panel_y2 = (
        panel_y1 +
        panel_height
    )


    # ========================================================
    # PANEL BACKGROUND
    # ========================================================

    overlay = annotated_frame.copy()


    cv2.rectangle(
        overlay,
        (
            panel_x1,
            panel_y1
        ),
        (
            panel_x2,
            panel_y2
        ),
        (0, 0, 0),
        -1
    )


    # IMPORTANT:
    # addWeighted result goes into a NEW array

    annotated_frame = cv2.addWeighted(
        overlay,
        0.55,
        annotated_frame,
        0.45,
        0
    )


    # ========================================================
    # TEXT SETTINGS
    # ========================================================

    text_x = panel_x1 + 15

    y = panel_y1 + 30


    # ========================================================
    # TITLE
    # ========================================================

    cv2.putText(
        annotated_frame,
        "A.R.T.E.M.I.S",
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.68,
        (255, 255, 255),
        2
    )


    y += 28


    cv2.putText(
        annotated_frame,
        "AI RAILWAY TRACK MONITORING",
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        2
    )


    y += 32


    # ========================================================
    # ARDUINO STATUS
    # ========================================================

    if arduino is not None:

        cv2.putText(
            annotated_frame,
            "Arduino: CONNECTED",
            (
                text_x,
                y
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            annotated_frame,
            "Arduino: DISCONNECTED",
            (
                text_x,
                y
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 0, 255),
            2
        )


    y += 30


    # ========================================================
    # IR
    # ========================================================

    if ir_status == "OBJECT DETECTED":

        ir_color = (
            0,
            0,
            255
        )

    elif ir_status == "CLEAR":

        ir_color = (
            0,
            255,
            0
        )

    else:

        ir_color = (
            0,
            255,
            255
        )


    cv2.putText(
        annotated_frame,
        "IR: " + ir_status,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        ir_color,
        2
    )


    y += 30


    # ========================================================
    # DISTANCE
    # ========================================================

    if (
        distance > 0
        and
        distance < OBSTACLE_DISTANCE
    ):

        distance_color = (
            0,
            0,
            255
        )

    elif distance > 0:

        distance_color = (
            0,
            255,
            0
        )

    else:

        distance_color = (
            0,
            255,
            255
        )


    if distance > 0:

        distance_text = (
            "Distance: "
            +
            str(round(distance, 1))
            +
            " cm"
        )

    else:

        distance_text = (
            "Distance: NO DATA"
        )


    cv2.putText(
        annotated_frame,
        distance_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        distance_color,
        2
    )


    y += 30


    # ========================================================
    # VIBRATION
    # ========================================================

    if vibration_detected:

        vibration_text = (
            "Vibration: HIGH"
        )

        vibration_color = (
            0,
            0,
            255
        )

    else:

        vibration_text = (
            "Vibration: NORMAL"
        )

        vibration_color = (
            0,
            255,
            0
        )


    cv2.putText(
        annotated_frame,
        vibration_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        vibration_color,
        2
    )


    y += 29


    # ========================================================
    # ACCELEROMETER
    # ========================================================

    acc_text = (
        "ACC: "
        +
        str(acc_x)
        +
        ", "
        +
        str(acc_y)
        +
        ", "
        +
        str(acc_z)
    )


    cv2.putText(
        annotated_frame,
        acc_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        2
    )


    y += 29


    # ========================================================
    # GYROSCOPE
    # ========================================================

    gyro_text = (
        "GYRO: "
        +
        str(gyro_x)
        +
        ", "
        +
        str(gyro_y)
        +
        ", "
        +
        str(gyro_z)
    )


    cv2.putText(
        annotated_frame,
        gyro_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        2
    )


    y += 31


    # ========================================================
    # YOLO STATUS
    # ========================================================

    if crack_detected:

        yolo_text = "YOLO: CRACK"

        yolo_color = (
            0,
            0,
            255
        )

    elif len(detected_classes) > 0:

        # Don't display vegetation / defectless etc.
        # Only show that YOLO detected something else.

        yolo_text = "YOLO: DETECTION"

        yolo_color = (
            0,
            255,
            255
        )

    else:

        yolo_text = "YOLO: NO DEFECT"

        yolo_color = (
            0,
            255,
            0
        )


    cv2.putText(
        annotated_frame,
        yolo_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        yolo_color,
        2
    )


    y += 29


    # ========================================================
    # CONFIDENCE
    # ========================================================

    if crack_detected:

        confidence_text = (
            "Confidence: "
            +
            str(
                round(
                    crack_confidence * 100,
                    1
                )
            )
            +
            "%"
        )

    else:

        confidence_text = (
            "Confidence: --"
        )


    cv2.putText(
        annotated_frame,
        confidence_text,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (255, 255, 255),
        2
    )


    y += 29


    # ========================================================
    # SEVERITY
    # ========================================================

    if crack_severity == "HIGH":

        severity_color = (
            0,
            0,
            255
        )

    elif crack_severity == "MEDIUM":

        severity_color = (
            0,
            165,
            255
        )

    elif crack_severity == "LOW":

        severity_color = (
            0,
            255,
            255
        )

    else:

        severity_color = (
            0,
            255,
            0
        )


    cv2.putText(
        annotated_frame,
        "Severity: " + crack_severity,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        severity_color,
        2
    )


    y += 32


    # ========================================================
    # RISK SCORE
    # ========================================================

    cv2.putText(
        annotated_frame,
        "RISK: "
        +
        str(risk_score)
        +
        "/100 "
        +
        risk_status,
        (
            text_x,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (
            0,
            0,
            255
        )
        if risk_score >= 75
        else
        (
            0,
            165,
            255
        )
        if risk_score >= 50
        else
        (
            0,
            255,
            255
        )
        if risk_score >= 25
        else
        (
            0,
            255,
            0
        ),
        2
    )


    # ========================================================
    # WHY ALERT
    # ========================================================

    why_y = panel_y2 - 18


    # If too long, shorten

    display_why = why_alert


    if len(display_why) > 38:

        display_why = (
            display_why[:35]
            +
            "..."
        )


    cv2.putText(
        annotated_frame,
        "WHY: " + display_why,
        (
            text_x,
            why_y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        (255, 255, 255),
        2
    )


    # ========================================================
    # BOTTOM-RIGHT DETECTION STATUS
    # ========================================================

    if crack_detected:

        detection_text = (
            "Detected: CRACK"
        )

    elif len(detected_classes) > 0:

        detection_text = (
            "Detected: OBJECT"
        )

    else:

        detection_text = (
            "Detected: No detection"
        )


    (
        detection_width,
        detection_height
    ), _ = cv2.getTextSize(
        detection_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        2
    )


    detection_x2 = (
        frame_width - 10
    )


    detection_x1 = max(
        10,
        detection_x2
        -
        detection_width
        -
        30
    )


    detection_y2 = (
        frame_height - 75
    )


    detection_y1 = (
        detection_y2 - 42
    )


    detection_overlay = (
        annotated_frame.copy()
    )


    cv2.rectangle(
        detection_overlay,
        (
            detection_x1,
            detection_y1
        ),
        (
            detection_x2,
            detection_y2
        ),
        (0, 0, 0),
        -1
    )


    annotated_frame = cv2.addWeighted(
        detection_overlay,
        0.65,
        annotated_frame,
        0.35,
        0
    )


    cv2.putText(
        annotated_frame,
        detection_text,
        (
            detection_x1 + 15,
            detection_y1 + 28
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (
            0,
            0,
            255
        )
        if crack_detected
        else
        (
            0,
            255,
            255
        )
        if len(detected_classes) > 0
        else
        (
            0,
            255,
            0
        ),
        2
    )


    # ========================================================
    # ALERT BAR
    # ========================================================

    if risk_score >= 25:


        if (
            crack_detected
            and
            obstacle_detected
            and
            vibration_detected
        ):

            alert_text = (
                "CRITICAL: CRACK + OBSTACLE + VIBRATION"
            )

        elif crack_detected and vibration_detected:

            alert_text = (
                "ALERT: CRACK + HIGH VIBRATION"
            )

        elif crack_detected and obstacle_detected:

            alert_text = (
                "ALERT: CRACK + OBSTACLE"
            )

        elif crack_detected:

            alert_text = (
                "ALERT: CRACK DETECTED"
            )

        elif obstacle_detected and vibration_detected:

            alert_text = (
                "ALERT: OBSTACLE + HIGH VIBRATION"
            )

        elif obstacle_detected:

            alert_text = (
                "ALERT: OBSTACLE DETECTED"
            )

        else:

            alert_text = (
                "ALERT: HIGH VIBRATION"
            )


        # Fit alert bar to screen

        (
            alert_width,
            alert_height
        ), _ = cv2.getTextSize(
            alert_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            2
        )


        alert_x1 = 10

        alert_y1 = (
            frame_height - 58
        )

        alert_x2 = min(
            frame_width - 10,
            alert_x1
            +
            alert_width
            +
            30
        )

        alert_y2 = (
            frame_height - 10
        )


        alert_overlay = (
            annotated_frame.copy()
        )


        cv2.rectangle(
            alert_overlay,
            (
                alert_x1,
                alert_y1
            ),
            (
                alert_x2,
                alert_y2
            ),
            (0, 0, 0),
            -1
        )


        annotated_frame = cv2.addWeighted(
            alert_overlay,
            0.70,
            annotated_frame,
            0.30,
            0
        )


        cv2.putText(
            annotated_frame,
            alert_text,
            (
                alert_x1 + 15,
                frame_height - 28
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 0, 255),
            2
        )


    # ========================================================
    # AUTOMATIC IMAGE LOGGING
    #
    # Save image whenever there is an abnormal condition.
    # ========================================================

    abnormal_condition = (
        crack_detected
        or
        obstacle_detected
        or
        vibration_detected
    )


    if (
        abnormal_condition
        and
        current_time - last_image_saved
        >= IMAGE_COOLDOWN
    ):


        timestamp_string = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        if crack_detected:

            image_prefix = "crack"

        elif vibration_detected:

            image_prefix = "vibration"

        else:

            image_prefix = "obstacle"


        image_filename = (
            image_prefix
            +
            "_"
            +
            timestamp_string
            +
            ".jpg"
        )


        image_path = os.path.join(
            DETECTION_FOLDER,
            image_filename
        )


        cv2.imwrite(
            image_path,
            annotated_frame
        )


        print(
            "EVENT IMAGE SAVED:",
            image_filename
        )


        last_image_saved = (
            current_time
        )


    # ========================================================
    # CONTINUOUS CSV LOGGING
    #
    # Logs sensor/AI information every 1 second.
    # ========================================================

    if (
        current_time - last_data_log
        >= LOG_INTERVAL
    ):


        readable_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # -----------------------------------------------
        # YOLO LOG DATA
        # -----------------------------------------------

        if crack_detected:

            log_detection = "CRACK"

            log_confidence = round(
                crack_confidence * 100,
                2
            )

            log_severity = crack_severity

        elif len(detected_classes) > 0:

            log_detection = "OTHER DETECTION"

            log_confidence = 0

            log_severity = "NONE"

        else:

            log_detection = "NO DEFECT"

            log_confidence = 0

            log_severity = "NONE"


        # -----------------------------------------------
        # VIBRATION
        # -----------------------------------------------

        if vibration_detected:

            log_vibration = "HIGH"

        else:

            log_vibration = "NORMAL"


        # -----------------------------------------------
        # IMAGE COLUMN
        # -----------------------------------------------

        image_log = ""


        # We don't save a new image every second.
        # Only abnormal events get image files.


        # -----------------------------------------------
        # WRITE CSV
        # -----------------------------------------------

        try:

            with open(
                LOG_FILE,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(
                    file
                )


                writer.writerow([

                    readable_time,

                    log_detection,

                    log_confidence,

                    log_severity,

                    ir_status,

                    (
                        round(distance, 2)
                        if distance > 0
                        else ""
                    ),

                    log_vibration,

                    risk_score,

                    risk_status,

                    why_alert,

                    image_log

                ])


                file.flush()


            print(
                "DATA LOGGED |",
                readable_time,
                "|",
                log_detection,
                "| Risk:",
                risk_score
            )


        except PermissionError:

            print(
                "CSV ERROR: Close ARTEMIS_log.csv "
                "in Excel before running."
            )


        except Exception as e:

            print(
                "CSV LOGGING ERROR:",
                e
            )


        last_data_log = (
            current_time
        )


    # ========================================================
    # DISPLAY WINDOW
    # ========================================================

    cv2.imshow(
        "ARTEMIS - AI Railway Monitoring",
        annotated_frame
    )


    # ========================================================
    # Q TO EXIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()


if arduino is not None:

    arduino.close()


cv2.destroyAllWindows()


print("ARTEMIS SYSTEM STOPPED")
