"""
Azure Kinect DK - Minimal Live Capture (Python)

Goal:
- Open device
- Grab frames: color / depth / ir
- Display basic preview

Notes:
- Requires Azure Kinect Sensor SDK installed on Windows
- Requires a Python wrapper library for k4a (choose one your lab standardizes on)
"""

import sys
import time

def main():
    try:
        # One common wrapper style (example):
        import pykinect_azure as pykinect
    except Exception as e:
        print("Python wrapper not found.")
        print("Install a k4a Python wrapper (e.g., pykinect_azure) and try again.")
        print("Error:", e)
        sys.exit(1)

    # Initialize the wrapper / SDK
    pykinect.initialize_libraries(track_body=False)

    # Device configuration (you can tune later)
    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
    device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

    device = pykinect.start_device(config=device_config)

    print("Device started. Press Ctrl+C to exit.")

    # Optional: simple preview (requires OpenCV)
    try:
        import cv2
        use_cv2 = True
    except Exception:
        use_cv2 = False
        print("OpenCV not installed; will run without preview.")

    try:
        while True:
            capture = device.update()
            ret_color, color_image = capture.get_color_image()
            ret_depth, depth_image = capture.get_depth_image()
            ret_ir, ir_image = capture.get_ir_image()

            if use_cv2:
                if ret_color:
                    cv2.imshow("Color", color_image)
                if ret_depth:
                    # Depth is usually uint16; normalize for display
                    depth_vis = (depth_image / depth_image.max() * 255).astype("uint8") if depth_image.max() > 0 else depth_image.astype("uint8")
                    cv2.imshow("Depth", depth_vis)
                if ret_ir:
                    ir_vis = (ir_image / ir_image.max() * 255).astype("uint8") if ir_image.max() > 0 else ir_image.astype("uint8")
                    cv2.imshow("IR", ir_vis)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            else:
                # headless mode: just print a heartbeat
                if ret_color or ret_depth or ret_ir:
                    print("Frame OK", time.time())
                time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        if use_cv2:
            import cv2
            cv2.destroyAllWindows()
        print("Stopped.")

if __name__ == "__main__":
    main()

