-----------------------------------------------------
🚆 ARTEMIS

Autonomous Railway Track Evaluation &
Monitoring Intelligent System

YOLOv8 • Computer Vision • Python
-----------------------------------------------------
# 🚆 ARTEMIS

AI-powered railway track defect detection using YOLOv8 and Computer Vision.

ARTEMIS is an AI-powered railway track inspection system that utilizes **Computer Vision** and **YOLOv8** to detect railway track defects in real time. The project aims to automate railway track monitoring, enabling faster, safer, and more efficient inspections while reducing dependence on manual inspection methods.

---

## 📖 Overview

Railway infrastructure requires regular inspection to ensure operational safety and prevent accidents. Traditional inspection methods are time-consuming, labour-intensive, and susceptible to human error.

ARTEMIS addresses these challenges by leveraging deep learning and computer vision to identify railway track conditions through live camera input. The current version classifies railway tracks into different categories using a trained YOLOv8 classification model.

---

## ✨ Features

- 🚆 Real-time railway track inspection
- 🤖 AI-powered defect classification using YOLOv8
- 📷 Live webcam inference
- 🔴 Detects railway track cracks
- 🌿 Detects vegetation on railway tracks
- 🟢 Identifies defect-free tracks
- 📊 Displays prediction confidence
- ⚡ Lightweight and real-time performance

---

## 🛠️ Tech Stack

### Programming Language
- Python 3.11

### AI Framework
- Ultralytics YOLOv8

### Libraries
- OpenCV
- NumPy
- Ultralytics

### Development Environment
- Visual Studio Code
- Git & GitHub

---

## 📂 Project Structure

```
ARTEMIS/
│
├── classify_webcam.py
├── best.pt
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── images/
│
└── detections/
```

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or later
- Webcam

Clone the repository

```bash
git clone https://github.com/harishk2086/ARTEMIS.git
```

Navigate to the project directory

```bash
cd ARTEMIS
```

Install the required dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python classify_webcam.py
```

---

## 🎯 Detection Classes

The current model classifies railway tracks into the following categories:

| Class | Description |
|--------|-------------|
| 🔴 Crack | Railway track crack detected |
| 🌿 Vegetation | Vegetation covering or obstructing the railway track |
| 🟢 Defectless | Healthy railway track |

---

## 📸 Sample Output

```
Prediction : Crack
Confidence : 97.4%

Prediction : Vegetation
Confidence : 94.8%

Prediction : Defectless
Confidence : 99.2%
```

---

## 🎯 Applications

- Railway track inspection
- Smart railway maintenance
- Railway safety monitoring
- AI-assisted infrastructure inspection
- Predictive maintenance systems
- Railway research projects

---

## 🚀 Future Scope

The upcoming versions of ARTEMIS aim to include:

- YOLOv8 Object Detection
- Multi-class railway defect detection
- GPS-based defect localization
- Edge AI deployment using NVIDIA Jetson Orin Nano
- Smart monitoring dashboard
- Automatic defect logging
- Cloud-based monitoring
- Predictive maintenance analytics
- Railway health monitoring system

---

## 📊 Project Status

**Current Version:** v1.0

### Completed
- ✅ YOLOv8 classification model
- ✅ Real-time webcam inference
- ✅ Railway defect classification
- ✅ Live confidence display

### Planned
- 🚧 Object detection
- 🚧 Edge deployment
- 🚧 Dashboard integration
- 🚧 GPS mapping
- 🚧 Automated reporting

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

If you'd like to contribute:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Harish K**

B.E. Electronics and Communication Engineering

**Interests:** Embedded Systems • Computer Vision • Artificial Intelligence • Edge AI

---

## ⭐ Support

If you found this project interesting or helpful, consider giving this repository a ⭐ on GitHub.

It helps support the project and encourages future development.
