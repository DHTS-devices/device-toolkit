import json
import os
import platform
import subprocess
from datetime import datetime

# ========= CONFIG (edit these) =========
PROJECT = "CV506_recording"
TIMEZONE = "America/Phoenix"  # change if needed

# Windows: INPUT_API="dshow", VIDEO_DEVICE="USB Video"
# macOS:   INPUT_API="avfoundation", VIDEO_DEVICE="1"
INPUT_API = "dshow"
VIDEO_DEVICE = "USB Video"

FPS = 30
CODEC = "libx264"
PRESET = "veryfast"
CRF = 23
MOVFLAGS = "+faststart"

OUT_DIR = "recordings"
# ======================================


def get_ffmpeg_version() -> str:
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        first_line = (r.stdout or "").splitlines()[0].strip()
        return first_line
    except Exception:
        return "unknown"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def build_output_paths(subject_id: str, session_id: str, ts: str):
    base = f"{subject_id}_{session_id}_{ts}"
    video_path = os.path.join(OUT_DIR, base + ".mp4")
    meta_path = os.path.join(OUT_DIR, base + ".json")
    return video_path, meta_path


def write_metadata(meta_path: str, data: dict) -> None:
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    ensure_dir(OUT_DIR)

    subject_id = input("Enter subject_id (e.g., S001): ").strip()
    session_id = input("Enter session_id (e.g., session1): ").strip()
    operator = input("Enter operator initials (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time_local = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    video_path, meta_path = build_output_paths(subject_id, session_id, ts)

    meta = {
        "project": PROJECT,
        "subject_id": subject_id,
        "session_id": session_id,
        "operator": operator or None,
        "start_time_local": start_time_local,
        "timezone": TIMEZONE,
        "platform": platform.system(),
        "ffmpeg_version": get_ffmpeg_version(),
        "video": {
            "input_api": INPUT_API,
            "device_name_or_index": VIDEO_DEVICE,
            "fps": FPS,
            "codec": CODEC,
            "preset": PRESET,
            "crf": CRF,
            "movflags": MOVFLAGS,
            "container": "mp4"
        },
        "output": {
            "video_path": video_path.replace("\\", "/"),
            "metadata_path": meta_path.replace("\\", "/")
        },
        "notes": notes or None
    }

    # Write metadata BEFORE recording starts (so you always have a record)
    write_metadata(meta_path, meta)

    print(f"\nRecording to: {video_path}")
    print(f"Metadata saved: {meta_path}")
    print("Press Ctrl+C to stop recording.\n")

    # Build ffmpeg command
    if INPUT_API == "dshow":
        # Windows DirectShow
        cmd = [
            "ffmpeg",
            "-f", "dshow",
            "-i", f"video={VIDEO_DEVICE}",
            "-r", str(FPS),
            "-c:v", CODEC,
            "-preset", PRESET,
            "-crf", str(CRF),
            "-movflags", MOVFLAGS,
            video_path
        ]
    elif INPUT_API == "avfoundation":
        # macOS AVFoundation (VIDEO_DEVICE should be like "1" or "1:0" if including audio)
        cmd = [
            "ffmpeg",
            "-f", "avfoundation",
            "-framerate", str(FPS),
            "-i", str(VIDEO_DEVICE),
            "-c:v", CODEC,
            "-preset", PRESET,
            "-crf", str(CRF),
            video_path
        ]
    else:
        raise ValueError(f"Unsupported INPUT_API: {INPUT_API}")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nRecording stopped by user (Ctrl+C).")
    except subprocess.CalledProcessError as e:
        print("\nFFmpeg failed:", e)


if __name__ == "__main__":
    main()
