"""
Azure Kinect DK - Body Tracking Export (Python)

Goal:
- Run body tracking
- Export 3D joints per frame to CSV/JSON

Notes:
- Requires Azure Kinect Body Tracking SDK installed
- Requires wrapper that supports body tracking
"""

import csv
import time
from pathlib import Path

def main(out_csv="skeleton_joints.csv"):
    import pykinect_azure as pykinect

    pykinect.initialize_libraries(track_body=True)

    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
    device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

    device = pykinect.start_device(config=device_config)
    tracker = pykinect.start_body_tracker()

    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # A simple, flat CSV:
    # timestamp, body_id, joint_name, x, y, z, confidence
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "body_id", "joint", "x", "y", "z", "confidence"])

        print("Tracking... Ctrl+C to stop.")
        try:
            while True:
                capture = device.update()
                body_frame = tracker.update(capture)

                ts = time.time()

                # Iterate bodies
                num_bodies = body_frame.get_num_bodies()
                for i in range(num_bodies):
                    body = body_frame.get_body(i)
                    body_id = body.id

                    # Iterate joints
                    for joint_name in body.joints:
                        j = body.joints[joint_name]
                        x, y, z = j.position  # meters (depends on wrapper)
                        conf = j.confidence
                        writer.writerow([ts, body_id, str(joint_name), x, y, z, conf])

        except KeyboardInterrupt:
            print("Done.")

if __name__ == "__main__":
    main()

