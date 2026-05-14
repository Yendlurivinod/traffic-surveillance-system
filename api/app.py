from flask import Flask, request, jsonify
import pandas as pd
import json
import os
import time

app = Flask(__name__)

def load_latest_summary():
    path = "data/processed/summary.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def load_latest_incidents():
    path = "data/processed/incident_summary.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def load_alerts():
    path = "data/processed/overspeed_alerts.csv"
    if os.path.exists(path):
        return pd.read_csv(path).to_dict(orient="records")
    return []

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "traffic-surveillance"})

@app.route("/dashboard", methods=["GET"])
def dashboard():
    summary = load_latest_summary()
    incidents = load_latest_incidents()
    return jsonify({
        "detection_summary": summary,
        "incident_summary": incidents,
        "status": "live"
    })

@app.route("/alerts", methods=["GET"])
def get_alerts():
    alerts = load_alerts()
    severity = request.args.get("severity")
    object_type = request.args.get("object_type")

    if severity:
        alerts = [a for a in alerts if a.get("risk_level") == severity.upper()]
    if object_type:
        alerts = [a for a in alerts if a.get("object_type") == object_type.lower()]

    return jsonify({
        "total": len(alerts),
        "alerts": alerts
    })

@app.route("/detect", methods=["POST"])
def detect():
    start = time.time()
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data"}), 400

        required = ['object_id', 'object_type', 'speed_kmh',
                    'bbox_x', 'bbox_y', 'bbox_w', 'bbox_h']
        missing = set(required) - set(data.keys())
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        speed_limits = {
            "car": 80, "truck": 60,
            "motorcycle": 80, "pedestrian": 10, "bus": 60
        }
        speed_limit = speed_limits.get(data['object_type'], 80)
        speed_ratio = round(data['speed_kmh'] / speed_limit, 3)
        overspeed = data['speed_kmh'] > speed_limit
        risk = "CRITICAL" if speed_ratio > 1.2 else \
               "HIGH" if speed_ratio > 1.0 else \
               "NORMAL" if speed_ratio > 0.8 else "LOW"

        latency_ms = round((time.time() - start) * 1000, 2)

        return jsonify({
            "object_id": data['object_id'],
            "object_type": data['object_type'],
            "speed_kmh": data['speed_kmh'],
            "speed_limit": speed_limit,
            "speed_ratio": speed_ratio,
            "overspeed": overspeed,
            "risk_level": risk,
            "alert": overspeed,
            "latency_ms": latency_ms
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stats", methods=["GET"])
def stats():
    alerts = load_alerts()
    summary = load_latest_summary()
    return jsonify({
        "total_detections": summary.get("total_detections", 0),
        "total_alerts": len(alerts),
        "avg_speed_kmh": summary.get("avg_speed_kmh", 0),
        "max_speed_kmh": summary.get("max_speed_kmh", 0),
        "object_counts": summary.get("object_counts", {})
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
