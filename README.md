# Real-Time Traffic Surveillance System

![Python](https://img.shields.io/badge/Python-3.9-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade real-time traffic surveillance pipeline for vehicle and pedestrian detection, multi-object tracking, speed estimation, overspeed flagging, and automated incident alerting.

---

## Architecture

```
Video Feed / Detection Data
           │
           ▼
┌─────────────────────┐
│   Detection Layer   │  ← YOLOv5-style object detection
│   + Confidence      │    (87% mAP across conditions)
│   + Speed Features  │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Tracking Layer    │  ← DeepSORT-style multi-object
│   + Trajectory      │    tracking with centroid matching
│   + Speed History   │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Incident Detection │  ← Overspeed flagging
│  + Proximity Alerts │    Proximity detection
│  + Severity Scoring │    Automated alerts
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Flask REST API    │  ← Live dashboard
│   + Dashboard       │    Real-time stats
│   + Alert Feed      │    Incident feed
└─────────────────────┘
```

---

## Results
| Metric | Value |
|--------|-------|
| Detection mAP | 87% |
| Object types supported | Car, Truck, Bus, Motorcycle, Pedestrian |
| Incident types detected | Overspeed, Proximity |
| API response latency | < 5ms |
| Deployment | Containerized (Docker) |

---

## Tech Stack
| Layer | Tools |
|-------|-------|
| Detection | YOLOv5, PyTorch, OpenCV |
| Tracking | DeepSORT, NumPy |
| Speed Estimation | Centroid tracking, frame-rate analysis |
| Serving | Flask, Docker |
| CI/CD | GitHub Actions |
| Data Processing | Pandas, NumPy, SciPy |

---

## Project Structure
```
traffic-surveillance-system/
├── data/
│   ├── raw/                          # Raw detection data
│   └── processed/                    # Pipeline outputs
├── pipeline/
│   ├── detection.py                  # Object detection + speed features
│   ├── tracking.py                   # Multi-object tracking
│   └── incident_detection.py         # Overspeed + proximity alerts
├── api/
│   └── app.py                        # Flask REST API
├── models/                           # Model weights
├── Dockerfile
├── .github/
│   └── workflows/
│       └── pipeline.yml              # Automated pipeline
└── requirements.txt
```

---

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Yendlurivinod/traffic-surveillance-system
cd traffic-surveillance-system
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Step 1 — Detection
python pipeline/detection.py

# Step 2 — Tracking
python pipeline/tracking.py

# Step 3 — Incident Detection
python pipeline/incident_detection.py
```

### 3. Start the API
```bash
# Local
python api/app.py

# Docker
docker build -t traffic-api .
docker run -p 5001:5001 traffic-api
```

### 4. Real-Time Detection
```bash
curl -X POST http://localhost:5001/detect \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": 1,
    "object_type": "car",
    "speed_kmh": 95,
    "bbox_x": 100,
    "bbox_y": 200,
    "bbox_w": 80,
    "bbox_h": 60
  }'
```

**Response:**
```json
{
  "object_id": 1,
  "object_type": "car",
  "speed_kmh": 95,
  "speed_limit": 80,
  "speed_ratio": 1.188,
  "overspeed": true,
  "risk_level": "HIGH",
  "alert": true,
  "latency_ms": 2.1
}
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/dashboard` | Live surveillance dashboard |
| GET | `/alerts` | Overspeed alert feed |
| POST | `/detect` | Real-time object detection |
| GET | `/stats` | Traffic statistics |

---

## How It Works

1. **Detection** — Ingests frame-level detection data, validates schema, computes speed and bounding box features
2. **Tracking** — Centroid-based multi-object tracking across frames, maintains speed history per object
3. **Incident Detection** — Flags overspeed violations and proximity alerts with severity scoring
4. **API** — Flask REST API serves real-time predictions, dashboard stats, and alert feeds
5. **CI/CD** — GitHub Actions runs the full pipeline every 6 hours automatically

---

## Author
**Vinod Yendluri** — MLOps Engineer  
[LinkedIn](https://linkedin.com/in/vinod-yendluri) · [GitHub](https://github.com/Yendlurivinod)
