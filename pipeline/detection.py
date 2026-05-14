import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Speed limits by object type (km/h)
SPEED_LIMITS = {
    "car": 80,
    "truck": 60,
    "motorcycle": 80,
    "pedestrian": 10,
    "bus": 60
}

CONFIDENCE_THRESHOLD = 0.85

def load_detections(input_path):
    df = pd.read_csv(input_path)
    print(f"✓ Loaded {len(df)} detections from {input_path}")
    return df

def filter_by_confidence(df):
    before = len(df)
    df = df[df['confidence'] >= CONFIDENCE_THRESHOLD]
    print(f"✓ Confidence filter — kept {len(df)}/{before} detections (>= {CONFIDENCE_THRESHOLD})")
    return df

def validate_schema(df):
    expected = ['frame_id', 'timestamp', 'object_id', 'object_type',
                'confidence', 'bbox_x', 'bbox_y', 'bbox_w', 'bbox_h',
                'speed_kmh', 'overspeed']
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    print(f"✓ Schema validated")
    return df

def compute_speed_features(df):
    df['speed_limit'] = df['object_type'].map(SPEED_LIMITS).fillna(80)
    df['speed_excess'] = (df['speed_kmh'] - df['speed_limit']).clip(lower=0)
    df['speed_ratio'] = (df['speed_kmh'] / df['speed_limit']).round(3)
    df['overspeed_flag'] = (df['speed_kmh'] > df['speed_limit']).astype(int)
    df['risk_level'] = pd.cut(
        df['speed_ratio'],
        bins=[0, 0.8, 1.0, 1.2, float('inf')],
        labels=['LOW', 'NORMAL', 'HIGH', 'CRITICAL']
    )
    print(f"✓ Speed features computed")
    return df

def compute_bbox_features(df):
    df['bbox_area'] = df['bbox_w'] * df['bbox_h']
    df['bbox_center_x'] = df['bbox_x'] + df['bbox_w'] / 2
    df['bbox_center_y'] = df['bbox_y'] + df['bbox_h'] / 2
    print(f"✓ Bounding box features computed")
    return df

def generate_alerts(df):
    alerts = df[df['overspeed_flag'] == 1][[
        'frame_id', 'timestamp', 'object_id',
        'object_type', 'speed_kmh', 'speed_limit',
        'speed_excess', 'risk_level'
    ]].copy()
    print(f"⚠ {len(alerts)} overspeed alerts generated")
    return alerts

def save_outputs(df, alerts, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f"{output_dir}/processed_detections.csv", index=False)
    alerts.to_csv(f"{output_dir}/overspeed_alerts.csv", index=False)
    summary = {
        "total_detections": len(df),
        "total_alerts": len(alerts),
        "overspeed_rate": round(len(alerts) / len(df), 4) if len(df) > 0 else 0,
        "object_counts": {str(k): int(v) for k, v in df["object_type"].value_counts().items()},
        "avg_speed_kmh": float(round(df["speed_kmh"].mean(), 2)),
        "max_speed_kmh": float(round(df["speed_kmh"].max(), 2)),
        "processed_at": datetime.now().isoformat()
    }
    with open(f"{output_dir}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Outputs saved to {output_dir}")
    return summary

def run_detection_pipeline(input_path="data/raw/sample_detections.csv",
                           output_dir="data/processed"):
    print("\n--- Running Detection Pipeline ---")
    df = load_detections(input_path)
    df = validate_schema(df)
    df = filter_by_confidence(df)
    df = compute_speed_features(df)
    df = compute_bbox_features(df)
    alerts = generate_alerts(df)
    summary = save_outputs(df, alerts, output_dir)
    print(f"\n✓ Pipeline complete")
    print(f"  Total detections : {summary['total_detections']}")
    print(f"  Overspeed alerts : {summary['total_alerts']}")
    print(f"  Avg speed        : {summary['avg_speed_kmh']} km/h")
    print(f"  Max speed        : {summary['max_speed_kmh']} km/h")
    return df, alerts, summary

if __name__ == "__main__":
    run_detection_pipeline()
