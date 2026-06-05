import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import sys
import os

# Add the project root to sys.path so we can import core
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.utils import format_timestamp, get_default_output_path
from core.input_handler import resolve_audio_path
from core.extractor import extract_audio
from core.transcriber import transcribe
from core.srt_writer import write_srt

class TestSubtitleGenerator(unittest.TestCase):

    def test_format_timestamp(self):
        # 0 seconds
        self.assertEqual(format_timestamp(0), "00:00:00,000")
        # 1.5 seconds
        self.assertEqual(format_timestamp(1.5), "00:00:01,500")
        # 60.05 seconds
        self.assertEqual(format_timestamp(60.05), "00:01:00,050")
        # 3661.999 seconds (1 hour, 1 min, 1 sec, 999 ms)
        self.assertEqual(format_timestamp(3661.999), "01:01:01,999")
        # Rounding edge case
        self.assertEqual(format_timestamp(1.9999), "00:00:02,000")

    def test_get_default_output_path(self):
        input_p = Path("movies/video.mp4")
        expected = Path("movies/video.srt")
        self.assertEqual(get_default_output_path(input_p), expected)

    @patch('core.input_handler.Path.exists')
    def test_resolve_audio_path_audio(self, mock_exists):
        mock_exists.return_value = True
        audio_path, is_temp = resolve_audio_path("test.mp3")
        self.assertEqual(audio_path, "test.mp3")
        self.assertFalse(is_temp)

    @patch('core.extractor.extract_audio')
    @patch('core.input_handler.Path.exists')
    def test_resolve_audio_path_video(self, mock_exists, mock_extract):
        mock_exists.return_value = True
        mock_extract.return_value = "temp.wav"
        audio_path, is_temp = resolve_audio_path("test.mp4")
        self.assertEqual(audio_path, "temp.wav")
        self.assertTrue(is_temp)
        mock_extract.assert_called_once_with("test.mp4")

    @patch('core.input_handler.Path.exists')
    def test_resolve_audio_path_invalid(self, mock_exists):
        mock_exists.return_value = True
        with self.assertRaises(ValueError):
            resolve_audio_path("test.txt")

    @patch('core.extractor.ffmpeg.run')
    def test_extract_audio_success(self, mock_ffmpeg_run):
        # Mock successful extraction
        mock_ffmpeg_run.return_value = (b"", b"")
        with patch('core.extractor.ffmpeg.input') as mock_input:
            mock_node = MagicMock()
            mock_input.return_value = mock_node
            mock_node.output.return_value = mock_node
            mock_node.overwrite_output.return_value = mock_node
            mock_node.run = mock_ffmpeg_run
            
            out_path = extract_audio("test.mp4")
            self.assertTrue(out_path.endswith("_temp_audio.wav"))

    @patch('core.transcriber.WhisperModel')
    def test_transcribe(self, mock_whisper_model):
        mock_model_instance = MagicMock()
        mock_whisper_model.return_value = mock_model_instance
        
        # Create a mock segment object that acts like faster-whisper's segment
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 2.0
        mock_segment.text = " Hello world "
        
        # Transcribe returns an iterator/generator of segments and info
        mock_model_instance.transcribe.return_value = ([mock_segment], None)
        
        segments = transcribe("test.wav", model_size="large-v3", task="translate")
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["text"], " Hello world ")
        mock_model_instance.transcribe.assert_called_once_with(
            "test.wav", language="ja", task="translate", vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500)
        )

    def test_write_srt(self):
        segments = [
            {"start": 0.0, "end": 1.5, "text": "Hello"}
        ]
        
        m_open = mock_open()
        with patch('builtins.open', m_open):
            # Also patch Path.mkdir to avoid actual filesystem operation
            with patch('pathlib.Path.mkdir'):
                write_srt(segments, "output.srt")
                
        m_open.assert_called_once_with(Path("output.srt"), 'w', encoding='utf-8')
        handle = m_open()
        
        # Check that it writes the index, timestamp, and text
        handle.write.assert_any_call("1\n")
        handle.write.assert_any_call("00:00:00,000 --> 00:00:01,500\n")
        handle.write.assert_any_call("Hello\n\n")

if __name__ == '__main__':
    unittest.main()
