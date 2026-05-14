import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

MAX_DISAPPEARED = 5  # frames before object is deregistered

class SimpleTracker:
    """
    Lightweight multi-object tracker using centroid-based matching.
    Simulates DeepSORT-style tracking without deep learning dependency.
    """

    def __init__(self):
        self.tracks = {}         # object_id -> track info
        self.disappeared = {}    # object_id -> frames since last seen
        self.track_history = []  # full history for analysis

    def register(self, object_id, centroid, object_type, speed):
        self.tracks[object_id] = {
            "object_id": object_id,
            "object_type": object_type,
            "centroids": [centroid],
            "speeds": [speed],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "frame_count": 1,
            "max_speed": speed,
            "avg_speed": speed
        }
        self.disappeared[object_id] = 0

    def update(self, object_id, centroid, speed):
        if object_id in self.tracks:
            self.tracks[object_id]["centroids"].append(centroid)
            self.tracks[object_id]["speeds"].append(speed)
            self.tracks[object_id]["last_seen"] = datetime.now().isoformat()
            self.tracks[object_id]["frame_count"] += 1
            self.tracks[object_id]["max_speed"] = max(
                self.tracks[object_id]["speeds"]
            )
            self.tracks[object_id]["avg_speed"] = round(
                np.mean(self.tracks[object_id]["speeds"]), 2
            )
            self.disappeared[object_id] = 0

    def deregister(self, object_id):
        if object_id in self.tracks:
            self.track_history.append(self.tracks[object_id])
            del self.tracks[object_id]
            del self.disappeared[object_id]

    def process_frame(self, frame_detections):
        current_ids = set(frame_detections['object_id'].tolist())
        tracked_ids = set(self.tracks.keys())

        # Update existing or register new
        for _, det in frame_detections.iterrows():
            oid = det['object_id']
            centroid = (det['bbox_center_x'], det['bbox_center_y'])
            speed = det['speed_kmh']

            if oid in tracked_ids:
                self.update(oid, centroid, speed)
            else:
                self.register(oid, centroid, det['object_type'], speed)

        # Mark disappeared objects
        for oid in tracked_ids - current_ids:
            self.disappeared[oid] += 1
            if self.disappeared[oid] > MAX_DISAPPEARED:
                self.deregister(oid)

    def get_summary(self):
        all_tracks = list(self.tracks.values()) + self.track_history
        return {
            "total_objects_tracked": len(all_tracks),
            "currently_active": len(self.tracks),
            "tracks": all_tracks
        }


def run_tracking(processed_path="data/processed/processed_detections.csv",
                 output_dir="data/processed"):
    print("\n--- Running Tracking Pipeline ---")

    df = pd.read_csv(processed_path)
    tracker = SimpleTracker()

    for frame_id in sorted(df['frame_id'].unique()):
        frame_data = df[df['frame_id'] == frame_id]
        tracker.process_frame(frame_data)

    summary = tracker.get_summary()
    print(f"✓ Tracked {summary['total_objects_tracked']} unique objects")
    print(f"✓ Currently active tracks: {summary['currently_active']}")

    # Save tracking results
    tracks_df = pd.DataFrame(summary['tracks'])
    if not tracks_df.empty:
        tracks_df = tracks_df[['object_id', 'object_type',
                                'frame_count', 'avg_speed', 'max_speed']]
        tracks_df.to_csv(f"{output_dir}/tracking_results.csv", index=False)
        print(f"✓ Tracking results saved")

    with open(f"{output_dir}/tracking_summary.json", 'w') as f:
        json.dump({
            "total_objects_tracked": summary['total_objects_tracked'],
            "currently_active": summary['currently_active']
        }, f, indent=2)

    return summary


if __name__ == "__main__":
    run_tracking()
