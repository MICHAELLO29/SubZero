from pathlib import Path

AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]
VIDEO_FORMATS = [".mp4", ".mkv", ".avi", ".mov"]

def resolve_audio_path(input_path: str) -> tuple[str, bool]:
    """
    Returns (audio_path, is_temp).
    - If input is audio: return (input_path, False) — use directly, no temp file
    - If input is video: extract audio, return (temp_wav_path, True) — clean up after
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError("File not found. Please check the path.")

    ext = path.suffix.lower()
    
    if ext in AUDIO_FORMATS:
        return (str(path), False)
    elif ext in VIDEO_FORMATS:
        # Import inside to prevent circular dependency if any, and keep it modular
        from .extractor import extract_audio
        temp_audio_path = extract_audio(str(path))
        return (temp_audio_path, True)
    else:
        raise ValueError(f"Unsupported format. Supported: {', '.join(AUDIO_FORMATS + VIDEO_FORMATS)}")
