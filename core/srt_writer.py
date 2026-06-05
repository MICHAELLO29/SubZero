from pathlib import Path
from .utils import format_timestamp

def write_srt(segments: list, output_path: str) -> None:
    """Converts segment list to .srt format and saves to output_path."""
    out_path = Path(output_path)
    
    # Ensure parent directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, start=1):
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
    except Exception as e:
        raise IOError("Could not write subtitle file. Check folder permissions.") from e
