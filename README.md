# SubZero - Universal Audio/Video Subtitle Generator

An application that accepts an **audio file (mp3, wav, m4a, flac) or video file (mp4, mkv, avi, mov)** as input, uses **Faster-Whisper** to transcribe and translate the audio, and outputs a perfectly timed `.srt` subtitle file.

## Key Features

* **Auto-Detect Language Support:** Recognizes and translates over 90 languages natively into English.
* **Optimized Performance:** Uses `faster-whisper` with 8-bit quantization (`int8_float16`) to maintain `large-v3` accuracy while significantly reducing VRAM requirements.
* **VAD Filtering:** Integrates Voice Activity Detection to filter out silence and background noise. `condition_on_previous_text` is disabled to prevent generation loops.
* **Native GUI:** Built with `customtkinter` for a minimal, functional dark-mode interface.
* **FFmpeg Path Resolution:** Automatically resolves `winget` FFmpeg installation paths on Windows.

## Setup Instructions

### 1. Clone or download the project
```bash
git clone https://github.com/yourname/SubZero.git
cd SubZero
```

### 2. Install Python Dependencies
Requires Python 3.10+.
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Required for audio extraction)
The application requires FFmpeg installed on your system to process media files.
* **Windows (Using Winget):** Open a fresh PowerShell and run:
  `winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`
* **Mac:** `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

### 4. Run the Application

**Launch the GUI:**
```bash
python main.py --gui
```

**Run via Command-Line:**
```bash
# Process a video file
python main.py --input ./movies/my_movie.mp4

# Process an audio file
python main.py --input ./audio/my_movie.mp3
```

## System Requirements
* **GPU:** NVIDIA GPU with CUDA support recommended.
* **RAM:** 8GB+ System RAM.
* **Internet:** Required on the first run to download the Whisper models.
