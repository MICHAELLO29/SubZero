import tempfile
from pathlib import Path
import ffmpeg

def extract_audio(video_path: str) -> str:
    """Extracts audio from video file. Returns path to temp .wav file."""
    temp_dir = tempfile.gettempdir()
    video_name = Path(video_path).stem
    temp_wav_path = Path(temp_dir) / f"{video_name}_temp_audio.wav"
    
    try:
        # Extract audio to 16kHz mono wav
        (
            ffmpeg
            .input(video_path)
            .output(str(temp_wav_path), ac=1, ar='16k', vn=None, format='wav', loglevel='error')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed. Download it from ffmpeg.org")
    except ffmpeg.Error as e:
        stderr_output = e.stderr.decode('utf-8') if e.stderr else ""
        if "Stream map" in stderr_output and "Audio" not in stderr_output:
            raise RuntimeError("No audio track detected in this video file.")
        elif "does not contain any stream" in stderr_output.lower():
            raise RuntimeError("No audio track detected in this video file.")
        raise RuntimeError(f"FFmpeg extraction failed: {stderr_output}")

    return str(temp_wav_path)
