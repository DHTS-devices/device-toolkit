# Marshall CV506 – Recording Guide (HDMI → Capture Card → Computer)

This guide shows how to preview and record video from the **Marshall CV506** using:
- **HDMI output**
- an **HDMI capture card** (USB or PCIe)
- a **computer** (Windows / macOS / Linux)

The CV506 outputs a **real-time HDMI video signal**.
- The camera **does NOT store video files** internally.
- All recording happens on the **computer/recorder side**.

---

## 1. Typical research use cases
- Behavioral observation / task recording (fixed camera)
- Lab or clinical fixed-position capture
- Synchronization with other sensor data (EDA, HR, wearables)

---

## 2. Requirements

| Item     | Description |
|----------|-------------|
| Camera   | Marshall CV506 |
| Output   | HDMI |
| Capture  | HDMI capture card (USB or PCIe) |
| OS       | Windows / macOS / Linux |
| Software | FFmpeg (recommended) or OBS |

---

## 3. Install FFmpeg

### Windows
1. Download FFmpeg: https://ffmpeg.org/download.html  
2. Extract the files  
3. Add `ffmpeg.exe` to your system PATH

Verify installation (PowerShell):
```powershell
ffmpeg -version
```

--

### macOS
1. Install via Homebrew (recommended):

Verify installation (PowerShell):
```powershell
brew install ffmpeg
```

## 4. Detect the HDMI Capture Device

## Windows
``FFmpeg uses DirectShow``
You must identify the exact name of the video capture device.

Run:
```
ffmpeg -list_devices true -f dshow -i dummy
```
| Device Name Example | Description |
|---------------------|-------------|
| USB Video           | Generic USB HDMI capture device |
| HDMI Capture        | HDMI capture card (varies by vendor) |
| Elgato HD60         | Elgato HDMI capture device |

### 5. Test Recording (Recommended)
Before starting a full recording, perform a short test (e.g., 5 seconds):
```
ffmpeg -f dshow -i video="USB Video" -t 5 test.mp4
```
| confirm | ----|
| ------- |-----|
|Video is visible|
|No black screen|
|No major frame drops|

### 6. Start Recording
A basic and stable recording command is:
```
ffmpeg -f dshow -i video="USB Video" -r 30 -c:v libx264 output.mp4
```
| This configuration is suitable for||
| ----------------------------------|-|
Fixed camera recording
Behavioral observation
Lab or clinical documentation
