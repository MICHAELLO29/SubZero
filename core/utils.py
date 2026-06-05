from pathlib import Path

def validate_file(file_path: Path) -> bool:
    """Check if file exists."""
    return file_path.exists() and file_path.is_file()

def get_default_output_path(input_path: Path) -> Path:
    """Get the default output .srt path based on input path."""
    return input_path.with_suffix(".srt")

def format_timestamp(seconds: float) -> str:
    """Format seconds into SRT timestamp HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    
    # Handle rounding edge case (if millis rounds up to 1000)
    if millis == 1000:
        secs += 1
        millis = 0
        if secs == 60:
            secs = 0
            minutes += 1
            if minutes == 60:
                minutes = 0
                hours += 1
                
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
