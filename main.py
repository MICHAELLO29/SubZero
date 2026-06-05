import argparse
import sys
import os
import shutil
from pathlib import Path

# Dynamically add FFmpeg to PATH if installed via winget but terminal hasn't restarted
if not shutil.which("ffmpeg") and os.name == 'nt':
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if local_app_data:
        winget_path = os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages')
        if os.path.exists(winget_path):
            for root, dirs, files in os.walk(winget_path):
                if 'ffmpeg.exe' in files:
                    os.environ["PATH"] += os.pathsep + root
                    break

from core.input_handler import resolve_audio_path
from core.transcriber import transcribe
from core.srt_writer import write_srt
from core.utils import get_default_output_path
from gui.app import run_gui

def main():
    parser = argparse.ArgumentParser(description="Japanese Audio/Video Subtitle Generator")
    parser.add_argument("--input", type=str, help="Path to audio (.mp3, .wav, etc.) or video")
    parser.add_argument("--output", type=str, help="Custom output path for the .srt file")
    parser.add_argument("--model", type=str, default="medium", choices=["tiny", "base", "medium", "large"], help="Whisper model size")
    parser.add_argument("--language", type=str, default="Japanese", help="Source language (default: Japanese)")
    parser.add_argument("--task", type=str, default="translate", choices=["translate", "transcribe"], help="Task to perform (translate to English or transcribe in Japanese)")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI window")

    args = parser.parse_args()

    # Launch GUI if requested
    if args.gui:
        run_gui()
        sys.exit(0)

    # CLI requires input
    if not args.input:
        print("Error: --input argument is required unless running with --gui.")
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else get_default_output_path(input_path)

    temp_wav_path = None
    try:
        # Step 1: Handle input & extract if video
        audio_path_str, is_temp = resolve_audio_path(args.input)
        
        if is_temp:
            temp_wav_path = audio_path_str
            print("[1/3] Video file detected — extracting audio first...")
            print(f"[2/3] Transcribing Japanese audio with Whisper (model: {args.model})...")
        else:
            print("[1/2] Audio file detected — skipping extraction, processing directly...")
            print(f"      Transcribing Japanese audio with Whisper (model: {args.model})...")
        
        print("      This may take a while for long files. Please wait...")
            
        # Step 2: Transcribe
        segments = transcribe(audio_path_str, model_size=args.model, task=args.task)
        
        # Step 3: Write SRT
        step_str = "[3/3]" if is_temp else "[2/2]"
        print(f"{step_str} Writing subtitle file...")
        write_srt(segments, str(output_path))
        
        print(f"Done! Subtitle saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Guarantee temp file cleanup
        if temp_wav_path and Path(temp_wav_path).exists():
            try:
                Path(temp_wav_path).unlink()
            except Exception:
                pass

if __name__ == "__main__":
    main()
