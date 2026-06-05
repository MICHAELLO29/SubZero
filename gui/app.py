import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import os
import sys
import shutil

# Ensure core can be imported when running from main.py or gui/app.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

from core.input_handler import resolve_audio_path, AUDIO_FORMATS, VIDEO_FORMATS
from core.transcriber import transcribe
from core.srt_writer import write_srt
from core.utils import format_timestamp

# Set modern default theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SubZero - Japanese Subtitle Generator")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Grid layout config
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        
        self.input_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.language_var = ctk.StringVar(value="Auto-Detect")
        self.model_size = ctk.StringVar(value="large-v3")
        self.task_type = ctk.StringVar(value="Translate to English")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Top Frame - Title
        title_font = ctk.CTkFont(size=20, weight="bold")
        self.title_label = ctk.CTkLabel(self.root, text="SubZero Subtitles", font=title_font)
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        # Main container for settings
        self.settings_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_frame.grid_columnconfigure(1, weight=1)
        
        # Input row
        ctk.CTkLabel(self.settings_frame, text="Media File:").grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.entry_input = ctk.CTkEntry(self.settings_frame, textvariable=self.input_path, placeholder_text="Select video or audio file...")
        self.entry_input.grid(row=0, column=1, padx=(0, 10), pady=15, sticky="ew")
        self.btn_browse_in = ctk.CTkButton(self.settings_frame, text="Browse", width=80, fg_color="transparent", border_width=1, command=self.browse_input)
        self.btn_browse_in.grid(row=0, column=2, padx=(0, 20), pady=15)
        
        # Output row
        ctk.CTkLabel(self.settings_frame, text="Output Folder:").grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        self.entry_output = ctk.CTkEntry(self.settings_frame, textvariable=self.output_path, placeholder_text="Default is same as input file...")
        self.entry_output.grid(row=1, column=1, padx=(0, 10), pady=(0, 15), sticky="ew")
        self.btn_browse_out = ctk.CTkButton(self.settings_frame, text="Browse", width=80, fg_color="transparent", border_width=1, command=self.browse_output)
        self.btn_browse_out.grid(row=1, column=2, padx=(0, 20), pady=(0, 15))
        
        # Options row
        ctk.CTkLabel(self.settings_frame, text="Settings:").grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        options_subframe = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        options_subframe.grid(row=2, column=1, columnspan=2, padx=(0, 20), pady=(0, 20), sticky="w")
        
        self.lang_combo = ctk.CTkOptionMenu(options_subframe, variable=self.language_var, values=["Auto-Detect", "Japanese", "Korean", "Chinese", "Spanish", "French", "English", "German", "Russian"], width=130)
        self.lang_combo.pack(side="left", padx=(0, 10))

        self.model_combo = ctk.CTkOptionMenu(options_subframe, variable=self.model_size, values=["tiny", "base", "small", "medium", "large-v2", "large-v3", "large-v3-turbo"], width=110)
        self.model_combo.pack(side="left", padx=(0, 10))
        
        self.task_combo = ctk.CTkOptionMenu(options_subframe, variable=self.task_type, values=["Translate to English", "Transcribe (keep original)"], width=180)
        self.task_combo.pack(side="left")
        
        # Log Textbox
        self.log_textbox = ctk.CTkTextbox(self.root, corner_radius=10, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Bottom Actions Frame
        self.action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        
        self.generate_btn = ctk.CTkButton(self.action_frame, text="Generate Subtitles", height=40, font=ctk.CTkFont(weight="bold"), command=self.start_generation)
        self.generate_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.open_folder_btn = ctk.CTkButton(self.action_frame, text="Open Output Folder", height=40, fg_color="transparent", border_width=1, state="disabled", command=self.open_output_folder)
        self.open_folder_btn.grid(row=0, column=1, sticky="e")
        
        # Initial Log Message
        self.log("Ready. Select an audio or video file to begin.")
        
    def log(self, message: str):
        # Update text log from thread safely
        self.root.after(0, self._append_log, message)
        
    def _append_log(self, message: str):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        
    def browse_input(self):
        all_exts = AUDIO_FORMATS + VIDEO_FORMATS
        filetypes = [
            ("Audio/Video Files", " ".join(f"*{ext}" for ext in all_exts)),
            ("Audio Files", " ".join(f"*{ext}" for ext in AUDIO_FORMATS)),
            ("Video Files", " ".join(f"*{ext}" for ext in VIDEO_FORMATS)),
            ("All Files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Media File", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            # Default output directory to input file's directory
            if not self.output_path.get():
                self.output_path.set(str(Path(filename).parent))
                
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Folder")
        if directory:
            self.output_path.set(directory)
            
    def open_output_folder(self):
        folder = self.output_path.get()
        if os.path.exists(folder):
            if os.name == 'nt':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

    def start_generation(self):
        input_file = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return
            
        self.generate_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="disabled")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
        # Run process in background thread
        thread = threading.Thread(target=self.process_file, args=(input_file, output_dir), daemon=True)
        thread.start()
        
    def process_file(self, input_file: str, output_dir: str):
        temp_wav_path = None
        try:
            input_p = Path(input_file)
            if not input_p.exists():
                self.log("Error: File not found. Please check the path.")
                return

            ext = input_p.suffix.lower()
            if ext not in AUDIO_FORMATS and ext not in VIDEO_FORMATS:
                self.log(f"Error: Unsupported format. Supported: {', '.join(AUDIO_FORMATS + VIDEO_FORMATS)}")
                return
                
            task_str = "translate" if "Translate" in self.task_type.get() else "transcribe"
            
            lang_map = {
                "Auto-Detect": None,
                "Japanese": "ja",
                "Korean": "ko",
                "Chinese": "zh",
                "Spanish": "es",
                "French": "fr",
                "English": "en",
                "German": "de",
                "Russian": "ru"
            }
            lang_code = lang_map.get(self.language_var.get(), None)
            
            # 1. Resolve path (audio extraction if needed)
            audio_path_str, is_temp = resolve_audio_path(input_file)
            
            if is_temp:
                temp_wav_path = audio_path_str
                self.log("Video file detected — extracting audio first...")
                self.log(f"Transcribing audio with Whisper (language: {self.language_var.get()}, model: {self.model_size.get()})...")
            else:
                self.log("Audio file detected — processing directly...")
                self.log(f"Transcribing audio with Whisper (language: {self.language_var.get()}, model: {self.model_size.get()})...")
            
            self.log("This may take a while for long files. Please wait...\n")

            # 2. Transcribe using Whisper
            segments = transcribe(audio_path_str, model_size=self.model_size.get(), task=task_str, language=lang_code)
            
            # 3. Write SRT file
            self.log("\nWriting subtitle file...")
            
            out_dir_path = Path(output_dir) if output_dir else input_p.parent
            srt_filename = input_p.with_suffix(".srt").name
            final_output_path = out_dir_path / srt_filename
            
            write_srt(segments, str(final_output_path))
            
            self.log(f"Done! Subtitle saved to: {final_output_path}")
            
            # Enable Open Folder button on success
            self.root.after(0, lambda: self.open_folder_btn.configure(state="normal"))
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            # Always clean up temp .wav file 
            if temp_wav_path and Path(temp_wav_path).exists():
                try:
                    Path(temp_wav_path).unlink()
                except Exception as cleanup_error:
                    self.log(f"Warning: Failed to clean up temp file: {cleanup_error}")
            
            # Re-enable generate button
            self.root.after(0, lambda: self.generate_btn.configure(state="normal"))

def run_gui():
    app_root = ctk.CTk()
    app = SubtitleApp(app_root)
    app_root.mainloop()

if __name__ == "__main__":
    run_gui()
