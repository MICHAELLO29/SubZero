from faster_whisper import WhisperModel
import warnings

def transcribe(audio_path: str, model_size: str = "large-v3", task: str = "translate") -> list:
    """
    Transcribes/translates audio using faster-whisper.
    Returns list of segment dicts.
    """
    # Initialize the faster-whisper model
    # compute_type="int8_float16" shrinks the large-v3 model to ~4GB VRAM so it runs perfectly on RTX 4060
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    except Exception as e:
        raise RuntimeError(f"Failed to load Whisper model. Detailed error: {str(e)}") from e

    # Transcribe the audio
    try:
        # VAD filter is the magic sauce that deletes silence, moaning, and breathing to prevent hallucinations
        segments_generator, info = model.transcribe(
            audio_path, 
            language="ja", 
            task=task,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Convert generator to list of dicts for our srt_writer
        from core.utils import format_timestamp
        segments = []
        for segment in segments_generator:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            # Print to GUI log so user sees progress in HH:MM:SS format
            start_str = format_timestamp(segment.start).replace(',', '.')
            end_str = format_timestamp(segment.end).replace(',', '.')
            print(f"[{start_str} --> {end_str}] {segment.text}")
            
    except Exception as e:
        if "out of memory" in str(e).lower():
            raise RuntimeError("CUDA Out of Memory. Try closing other apps or use a smaller model.")
        raise RuntimeError(f"Transcription failed: {str(e)}")

    return segments
