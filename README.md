# 🚆 ARTEMIS

## Autonomous Railway Track Evaluation & Monitoring Intelligent System

ARTEMIS is an AI-powered railway track inspection system that leverages **Computer Vision** and **YOLOv8** to detect railway track defects in real time. The project is designed to assist railway maintenance by automating the inspection process, reducing manual effort, and enabling faster identification of potential hazards.

---

## 📌 Features

- 🚆 Real-time railway track inspection
- 🤖 YOLOv8-based AI classification
- 📷 Live webcam inference
- 🔴 Detects railway track cracks
- 🌿 Identifies vegetation on tracks
- 🟢 Recognizes defect-free railway tracks
- 📊 Displays prediction confidence in real time
- ⚡ Fast and lightweight inference

---

## 🛠️ Tech Stack

- Python 3.11
- Ultralytics YOLOv8
- OpenCV
- NumPy

---

## 📁 Project Structure

```
ARTEMIS/
│
├── classify_webcam.py
├── best.pt
├── requirements.txt
├── README.md
└── images/
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/ARTEMIS.git
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python classify_webcam.py
```

---

## 🎯 Defect Classes

The model is trained to classify the following railway track conditions:

- 🔴 Crack
- 🌿 Vegetation
- 🟢 Defectless

---

## 📈 Future Enhancements

- YOLOv8 Object Detection
- GPS-based defect localization
- Edge AI deployment (Jetson Orin Nano)
- Smart monitoring dashboard
- Automatic report generation
- Multi-class railway defect detection

---

## 🎓 Applications

- Railway infrastructure inspection
- Predictive railway maintenance
- AI-assisted track monitoring
- Railway safety enhancement
- Smart transportation systems

---

## 👨‍💻 Author

**Harish K**

B.E. Electronics and Communication Engineering

**ARTEMIS – Autonomous Railway Track Evaluation & Monitoring Intelligent System**

⭐ **If you found this project useful, consider giving it a star!**
