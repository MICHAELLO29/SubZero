# SubZero - Japanese Audio/Video Subtitle Generator

An application that accepts a Japanese **audio file (mp3, wav, m4a, flac) or video file (mp4, mkv, avi, mov)** as input, uses **Faster-Whisper** to transcribe and translate the audio, and outputs a perfectly timed `.srt` subtitle file.

Built with **Voice Activity Detection (VAD)** to automatically filter out background noise, heavy breathing, and silence to eliminate translation hallucinations.

## Setup Instructions

### 1. Clone or download the project
```bash
git clone https://github.com/yourname/SubZero.git
cd SubZero
```

### 2. Install Python Dependencies
Make sure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Required for audio extraction)
The application requires FFmpeg installed on your system to process media files.
* **Windows (Using Winget):** Open a fresh PowerShell and run:
  `winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`
  *(Note: You must restart your terminal and IDE after installing so the system recognizes FFmpeg in your PATH)*
* **Mac:** `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

### 4. Run the Application
You can use the command-line interface or launch the simple GUI.

**Launch the GUI (Recommended):**
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
* **GPU:** An NVIDIA GPU (e.g. RTX series) is highly recommended for hardware acceleration (`cuda`), as it significantly speeds up translation.
* **RAM:** 8GB+ System RAM.
* **Internet:** Required on the first run to automatically download the Whisper AI models and VAD filter from HuggingFace.
