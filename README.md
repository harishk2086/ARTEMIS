# 🚆 A.R.T.E.M.I.S.

**AI Railway Track Evaluation & Monitoring System**\
AI-powered railway track condition classification with YOLOv8,
Arduino-based sensing, and real-time alerts.

A.R.T.E.M.I.S. is a prototype railway-track monitoring system that
combines computer vision with physical sensor measurements. A webcam
provides live track images to a Python application running a trained
YOLOv8 classification model. An Arduino reads the MPU6050 vibration
sensor and, in the expanded hardware setup, the IR and ultrasonic
sensors. The software combines available readings to classify the
current condition and send alert commands to the Arduino.

> **Prototype notice:** A.R.T.E.M.I.S. is an educational/research
> prototype. It is not a railway-certified safety system and must not be
> used to make operational railway-safety decisions.

------------------------------------------------------------------------

## 📖 Overview

Manual railway inspection can be time-consuming and requires regular
effort. A.R.T.E.M.I.S. explores how computer vision and low-cost
embedded sensing can support preliminary track-condition monitoring.

The current vision model classifies a camera frame into one of three
trained classes:

-   **Crack** --- a frame classified as showing a crack
-   **Vegetation** --- vegetation detected/classified on or near the
    track
-   **Defectless** --- a frame classified as a normal/healthy track

The Python application reads vibration values from the Arduino over
serial communication. The vision prediction and vibration reading are
used by the decision logic to select a status and send a command to the
Arduino for the connected indicators.

The IR and ultrasonic sensors can provide supplementary
proximity/obstacle information when their readings are implemented in
both the Arduino sketch and Python serial protocol.

------------------------------------------------------------------------

## ✨ Features

-   🚆 Live railway-track monitoring using a webcam
-   🤖 YOLOv8 image classification using a custom-trained `best.pt`
    model
-   🔴 Three classification labels: `crack`, `vegetation`, and
    `defectless`
-   📊 Displays predicted class and model confidence
-   📈 Displays the vibration value received from the MPU6050/Arduino
-   🔗 Serial communication between Python and Arduino
-   🚦 Status logic for `SAFE`, `WARNING`, and `DANGER`
-   🔔 Arduino-controlled buzzer/LED alerts, subject to the uploaded
    Arduino sketch
-   📡 Optional IR and ultrasonic sensing for supplementary
    proximity/obstacle checks
-   ⚡ Live inference with OpenCV

**Important:** The classification model is a *classification* model, not
a bounding-box detector. It assigns a class to the frame; it does not
locate a crack with a bounding box. Bounding boxes require a separately
trained YOLO object-detection model and corresponding inference code.

------------------------------------------------------------------------

## 🧠 System Architecture

``` text
                  USB WEBCAM
                      |
                      v
              Python + OpenCV
                      |
                      v
              YOLOv8 Classification
                      |
             crack / vegetation /
                  defectless
                      |
                      v
               Decision Logic <-------------------+
                      |                            |
                      |                       Serial data
                      |                            |
                      |                      ARDUINO NANO
                      |                            |
                      |                 +----------+----------+
                      |                 |          |          |
                      |              MPU6050       IR     Ultrasonic
                      |              vibration   sensor     sensor
                      |                 |
                      +-----------------+
                      |
                      v
              SAFE / WARNING / DANGER
                      |
                Serial command
                      |
                      v
             Arduino LED / buzzer
```

The webcam connects to the computer running Python; it does **not**
connect directly to the Arduino Nano. In the current laptop-based
arrangement, the Nano communicates with Python over USB serial.
Standalone operation would require moving the Python/YOLO workload to a
suitable edge computer and validating performance on that device.

------------------------------------------------------------------------

## 🔎 Detection Classes

  -----------------------------------------------------------------------
  Class                   Meaning                 Typical prototype
                                                  status
  ----------------------- ----------------------- -----------------------
  `crack`                 The model classifies    `WARNING` or `DANGER`,
                          the frame as showing a  depending on vibration
                          crack                   logic

  `vegetation`            The model classifies    `WARNING`
                          the frame as showing    
                          vegetation              

  `defectless`            The model classifies    `SAFE`, provided no
                          the frame as            other rule raises an
                          normal/defect-free      alert
  -----------------------------------------------------------------------

The labels and results depend on the images and annotations used to
train `model/best.pt`. Model predictions are not proof that a track is
safe or defective.

------------------------------------------------------------------------

## ⚙️ Prototype Decision Logic

The earlier Python logic uses the following rules:

  Vision prediction              Vibration reading Result      Arduino command
  ---------------------------- ------------------- ----------- -----------------
  `crack`                               Above 5000 `DANGER`    `R`
  `crack`                            5000 or below `WARNING`   `Y`
  `vegetation`                                 Any `WARNING`   `Y`
  `defectless` / other class                   Any `SAFE`      `G`

The value `5000` is an example threshold from the prototype code, not a
validated railway safety limit. Calibrate the threshold against measured
data and the mounting arrangement. Also ensure that the model's actual
class names match the names used in the code.

The IR and ultrasonic readings should only affect the status after their
data format, sensor behavior, and decision rules have been implemented
and tested. Do not assume they are included in the Python decision logic
merely because the sensors are physically connected.

------------------------------------------------------------------------

## 🛠️ Hardware

  -----------------------------------------------------------------------
  Component                           Purpose
  ----------------------------------- -----------------------------------
  Arduino Nano                        Reads sensors and controls alert
                                      outputs

  MPU6050                             Measures acceleration and angular
                                      velocity; used for prototype
                                      vibration monitoring

  IR sensor module                    Supplementary object/proximity
                                      indication, depending on module
                                      type and setup

  HC-SR04 ultrasonic sensor           Measures distance to a nearby
                                      object within its usable range

  USB webcam                          Captures track images for computer
                                      vision

  Buzzer module                       Audible prototype alert

  Red and green LEDs                  Visual status indication, if fitted
                                      and supported by the Arduino sketch

  Computer running Python             Runs OpenCV, YOLOv8 and the
                                      decision logic
  -----------------------------------------------------------------------

Check the voltage requirements of each module. Keep all required grounds
common. Do not connect the webcam directly to the Arduino Nano.

### Example Arduino pin mapping

Use this table only if it matches your actual Arduino sketch and wiring.

  Component                                 Arduino Nano connection
  ----------------------------------------- -------------------------------------------
  MPU6050 SDA                               A4
  MPU6050 SCL                               A5
  IR sensor OUT                             D2
  HC-SR04 TRIG                              D4
  HC-SR04 ECHO                              D5
  Buzzer signal                             D6
  Red LED (through a suitable resistor)     D7
  Green LED (through a suitable resistor)   D8
  Sensor VCC/GND                            According to each module's specifications

Keep D0/D1 available for USB serial communication unless your design
specifically requires otherwise.

------------------------------------------------------------------------

## 💻 Software Stack

-   Python 3.11 or later
-   Ultralytics YOLOv8
-   OpenCV
-   PySerial
-   NumPy (if required by the installed model/runtime)
-   Arduino IDE for the microcontroller sketch
-   Git and GitHub

------------------------------------------------------------------------

## 📂 Project Structure

The structure below matches the simple laptop-based project layout. If
your script is inside `src/`, adjust the run command accordingly.

``` text
ARTEMIS/
├── classify_webcam.py
├── model/
│   └── best.pt
├── images/
├── detections/
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

-   `classify_webcam.py` --- webcam inference, serial reading, decision
    logic and display
-   `model/best.pt` --- trained YOLOv8 classification model
-   `images/` --- optional project images and screenshots
-   `detections/` --- optional saved outputs, if saving is implemented

Do not commit private data, large datasets, virtual environments, or
files that are not permitted by their licences.

------------------------------------------------------------------------

## 🚀 Installation and Setup

### 1. Install Python

Install Python 3.11 or a compatible version supported by your installed
Ultralytics release.

### 2. Clone the repository

``` bash
git clone https://github.com/harishk2086/ARTEMIS.git
cd ARTEMIS
```

### 3. Install dependencies

If `requirements.txt` is present:

``` bash
python -m pip install -r requirements.txt
```

A minimal dependency list for the shown Python code is:

``` text
ultralytics
opencv-python
pyserial
numpy
```

Save these lines to `requirements.txt` if your repository does not
already have one. For reproducible installations, record the versions
tested on your machine.

### 4. Check the model file

Confirm that this file exists:

``` text
ARTEMIS/model/best.pt
```

The Python code loads it using the relative path `model/best.pt`, so
launch the script from the project root unless you have changed the path
handling.

### 5. Connect the Arduino

1.  Upload the matching Arduino sketch.
2.  Connect the Nano by USB.
3.  Open Windows Device Manager and check the assigned COM port.
4.  Close Arduino Serial Monitor/Plotter before running Python if it is
    using the same port.
5.  Update the serial-port setting in the Python script if necessary.

For example:

``` python
arduino = serial.Serial("COM3", 115200, timeout=0.1)
```

Change `COM3` to the port assigned to your board. The Arduino sketch and
Python application must use the same baud rate and compatible serial
message/command formats.

### 6. Run A.R.T.E.M.I.S.

``` bash
python classify_webcam.py
```

Press **`q`** in the OpenCV window to quit. If your script is located at
`src/classify_webcam.py`, use:

``` bash
python src/classify_webcam.py
```

------------------------------------------------------------------------

## 🖥️ Runtime Display

The application can display:

-   Predicted class and confidence
-   Vibration value received from Arduino
-   Current state: `SAFE`, `WARNING`, or `DANGER`
-   Live camera feed

Additional fields such as distance, IR status, gyroscope values, Arduino
connection state, or FPS should only be displayed after the
corresponding data is actually sent and handled by the current code.

------------------------------------------------------------------------

## 🧪 Testing and Evaluation

For a meaningful evaluation, test the model and sensors separately
before testing the combined system.

1.  **Vision test:** Evaluate representative images of crack, vegetation
    and defectless tracks.
2.  **Confidence test:** Record the prediction confidence and review
    low-confidence or incorrect classifications.
3.  **Vibration test:** Record normal and abnormal vibration
    measurements using the final mounting arrangement.
4.  **IR/ultrasonic test:** Check their readings at several known
    distances and under different environmental conditions.
5.  **Fusion test:** Compare the system status with a manually labelled
    test set.
6.  **Timing test:** Measure inference speed and end-to-end alert
    latency.
7.  **False-alarm test:** Record false positives and false negatives for
    each class and sensor condition.

Report metrics such as precision, recall, F1-score, confusion matrix,
inference FPS, alert latency and false-alarm rate. Do not report
performance figures unless they have been measured.

------------------------------------------------------------------------

## 🎯 Applications

-   Educational railway-inspection prototypes
-   Computer-vision research
-   Embedded sensing and sensor-fusion experiments
-   Preliminary infrastructure-condition monitoring
-   Demonstrations of AI-assisted maintenance concepts

------------------------------------------------------------------------

## 🔭 Future Scope

-   Implement and validate IR and ultrasonic readings in the complete
    serial protocol
-   Improve the sensor-fusion method and evaluate false alarms
-   Add timestamped event logging and report export
-   Build a monitoring dashboard
-   Evaluate an edge-computing platform for operation without a laptop
-   Explore object detection if bounding-box localization is required
-   Add location tagging only when supported by suitable hardware and
    validated data
-   Test across different lighting, track surfaces and environmental
    conditions

These are development goals, not claims that the features are already
implemented.

------------------------------------------------------------------------

## 📌 Project Status

**Project:** A.R.T.E.M.I.S. --- AI Railway Track Evaluation & Monitoring
System\
**Current baseline:** YOLOv8 classification + webcam inference + Arduino
serial integration

### Baseline capabilities

-   YOLOv8 classification of `crack`, `vegetation` and `defectless`
-   Live webcam inference
-   Prediction-confidence display
-   Vibration input from Arduino, subject to the connected sketch
-   Prototype status logic and serial alert commands

### Integration/validation items

-   Confirm IR and ultrasonic telemetry is included in the Arduino
    sketch and Python parser
-   Validate all sensor-fusion rules with recorded test data
-   Verify buzzer/LED behavior for every alert state
-   Measure and document performance before making quantitative claims
-   Validate any dashboard or standalone edge-computing implementation
    separately

------------------------------------------------------------------------

## 🤝 Contributing

Suggestions and improvements are welcome.

1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes with a clear message.
4.  Open a pull request describing the change and how it was tested.

------------------------------------------------------------------------

## 📄 License

This project is intended to use the MIT License if the repository's
`LICENSE` file contains the MIT License text. Ensure the licence file is
present before describing the repository as MIT-licensed.

------------------------------------------------------------------------

## 👨‍💻 Author

**Harish K**\
B.E. Electronics and Communication Engineering\
**Interests:** Embedded Systems · Computer Vision · Artificial
Intelligence · VLSI

------------------------------------------------------------------------

## ⭐ Support

If you find A.R.T.E.M.I.S. interesting, consider starring the repository
on GitHub. Feedback and contributions can help improve the prototype.
