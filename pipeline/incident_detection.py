import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

OVERSPEED_THRESHOLD = 1.0      # speed_ratio > 1.0 = overspeed
CRITICAL_SPEED_RATIO = 1.2     # speed_ratio > 1.2 = critical
PROXIMITY_THRESHOLD = 100      # pixels — objects closer than this flagged

def detect_overspeed_incidents(df):
    incidents = []
    overspeed = df[df['overspeed_flag'] == 1]
    for _, row in overspeed.iterrows():
        incidents.append({
            "incident_type": "OVERSPEED",
            "severity": "CRITICAL" if row['speed_ratio'] > CRITICAL_SPEED_RATIO else "HIGH",
            "frame_id": row['frame_id'],
            "timestamp": row['timestamp'],
            "object_id": row['object_id'],
            "object_type": row['object_type'],
            "speed_kmh": row['speed_kmh'],
            "speed_limit": row['speed_limit'],
            "speed_excess_kmh": row['speed_excess'],
            "description": f"{row['object_type'].title()} #{row['object_id']} "
                           f"travelling at {row['speed_kmh']}km/h "
                           f"({row['speed_excess']}km/h over limit)"
        })
    print(f"✓ Detected {len(incidents)} overspeed incidents")
    return incidents

def detect_proximity_incidents(df):
    incidents = []
    for frame_id in df['frame_id'].unique():
        frame = df[df['frame_id'] == frame_id]
        objects = frame[['object_id', 'object_type',
                          'bbox_center_x', 'bbox_center_y']].values

        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                oid1, type1, x1, y1 = objects[i]
                oid2, type2, x2, y2 = objects[j]
                distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

                if distance < PROXIMITY_THRESHOLD:
                    incidents.append({
                        "incident_type": "PROXIMITY_ALERT",
                        "severity": "MEDIUM",
                        "frame_id": int(frame_id),
                        "object_1": f"{type1} #{int(oid1)}",
                        "object_2": f"{type2} #{int(oid2)}",
                        "distance_px": round(float(distance), 2),
                        "description": f"Close proximity between "
                                       f"{type1} #{int(oid1)} and "
                                       f"{type2} #{int(oid2)} "
                                       f"({round(float(distance), 1)}px apart)"
                    })

    print(f"✓ Detected {len(incidents)} proximity incidents")
    return incidents

def save_incidents(all_incidents, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(all_incidents) if all_incidents else pd.DataFrame()

    if not df.empty:
        df.to_csv(f"{output_dir}/incidents.csv", index=False)

    summary = {
        "total_incidents": len(all_incidents),
        "by_type": df['incident_type'].value_counts().to_dict() if not df.empty else {},
        "by_severity": df['severity'].value_counts().to_dict() if not df.empty else {},
        "generated_at": datetime.now().isoformat()
    }

    with open(f"{output_dir}/incident_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Incident report saved — {len(all_incidents)} total incidents")
    return summary

def run_incident_detection(processed_path="data/processed/processed_detections.csv",
                           output_dir="data/processed"):
    print("\n--- Running Incident Detection ---")
    df = pd.read_csv(processed_path)
    overspeed = detect_overspeed_incidents(df)
    proximity = detect_proximity_incidents(df)
    all_incidents = overspeed + proximity
    summary = save_incidents(all_incidents, output_dir)

    print(f"\n✓ Incident detection complete")
    print(f"  Total incidents  : {summary['total_incidents']}")
    print(f"  By type          : {summary['by_type']}")
    print(f"  By severity      : {summary['by_severity']}")
    return all_incidents, summary

if __name__ == "__main__":
    run_incident_detection()
