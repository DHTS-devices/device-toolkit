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
``powershell
ffmpeg -version```

--
### macOS
1. Install via Homebrew (recommended):

Verify installation (PowerShell):
```powershell
brew install ffmpeg```
