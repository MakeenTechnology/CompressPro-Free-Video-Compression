#!/usr/bin/env python3
"""
CompressPro - Universal GPU-Accelerated Video Compression Tool
Built with PyAV for universal hardware acceleration support
"""

import sys
import os
import json
import time
import psutil
import av
import gc
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import subprocess
import webbrowser

# Application metadata
APP_NAME = "CompressPro"
APP_VERSION = "2.0.0"
AUTHOR = "AlharthyDev"
DONATION_URL = "https://paypal.me/AlharthyDev"

@dataclass
class CompressionSettings:
    """Settings for video compression"""
    input_file: str = ""
    output_file: str = ""
    codec: str = "h264"  # h264, h265, vp9, av1
    quality_mode: str = "crf"  # crf, bitrate
    crf_value: int = 23
    bitrate: str = "1M"
    resolution: str = "original"  # original, 1080p, 720p, 480p
    fps: str = "original"  # original, 30, 24, 60
    gpu_acceleration: str = "auto"  # auto, nvenc, qsv, vaapi, cpu
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    threads: int = 0  # 0 = auto

class SystemDetector:
    """Detects system capabilities and hardware acceleration support"""
    
    def __init__(self):
        self.gpu_info = self.detect_gpu_capabilities()
        self.cpu_info = self.get_cpu_info()
        self.memory_info = self.get_memory_info()
        
    def detect_gpu_capabilities(self) -> Dict[str, Any]:
        """Detect available GPU acceleration methods"""
        capabilities = {
            'nvenc': False,
            'qsv': False, 
            'vaapi': False,
            'videotoolbox': False,
            'supported_codecs': []
        }
        
        try:
            # Check available encoders and decoders in PyAV
            encoders = av.codec.codecs_available
            
            # NVIDIA NVENC support
            nvenc_codecs = ['h264_nvenc', 'hevc_nvenc', 'av1_nvenc']
            capabilities['nvenc'] = any(codec in encoders for codec in nvenc_codecs)
            
            # Intel QuickSync support
            qsv_codecs = ['h264_qsv', 'hevc_qsv', 'av1_qsv']
            capabilities['qsv'] = any(codec in encoders for codec in qsv_codecs)
            
            # VAAPI support (Linux)
            vaapi_codecs = ['h264_vaapi', 'hevc_vaapi']
            capabilities['vaapi'] = any(codec in encoders for codec in vaapi_codecs)
            
            # VideoToolbox support (macOS)
            vt_codecs = ['h264_videotoolbox', 'hevc_videotoolbox']
            capabilities['videotoolbox'] = any(codec in encoders for codec in vt_codecs)
            
            # Get supported codecs
            supported = []
            for codec in ['h264', 'h265', 'vp9', 'av1']:
                if codec in encoders or f'lib{codec}' in encoders:
                    supported.append(codec)
            capabilities['supported_codecs'] = supported
            
        except Exception as e:
            print(f"GPU detection error: {e}")
            
        return capabilities
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        return {
            'count': psutil.cpu_count(logical=True),
            'physical': psutil.cpu_count(logical=False),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
    
    def get_optimal_encoder(self, codec: str) -> str:
        """Get the optimal encoder for given codec based on available hardware"""
        encoder_priority = {
            'h264': ['libx264', 'h264_nvenc', 'h264_qsv', 'h264_vaapi', 'h264_videotoolbox'],  # Software first for stability
            'h265': ['libx265', 'hevc_nvenc', 'hevc_qsv', 'hevc_vaapi', 'hevc_videotoolbox'],  # Software first for stability
            'vp9': ['libvpx-vp9', 'vp9_vaapi'],
            'av1': ['libsvtav1', 'av1_qsv', 'av1_vaapi', 'av1_nvenc']  # Software AV1 first, more stable
        }
        
        available_encoders = av.codec.codecs_available
        
        for encoder in encoder_priority.get(codec, []):
            if encoder in available_encoders:
                return encoder
                
        # Fallback to software encoding
        fallback = {
            'h264': 'libx264',
            'h265': 'libx265', 
            'vp9': 'libvpx-vp9',
            'av1': 'libsvtav1'
        }
        return fallback.get(codec, 'libx264')
    
    def get_fallback_encoders(self, codec: str) -> List[str]:
        """Get fallback encoders for the given codec"""
        fallback_lists = {
            'h264': ['libx264', 'h264_nvenc'],
            'h265': ['libx265', 'hevc_nvenc'], 
            'vp9': ['libvpx-vp9'],
            'av1': ['libsvtav1', 'libaom-av1']
        }
        return fallback_lists.get(codec, ['libx264'])

class VideoCompressionWorker(QThread):
    """Worker thread for video compression using PyAV with GPU acceleration"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, settings: CompressionSettings, system_detector: SystemDetector):
        super().__init__()
        self.settings = settings
        self.system_detector = system_detector
        self.is_cancelled = False
        
    def cancel(self):
        """Cancel the compression process"""
        self.is_cancelled = True
        
    def run(self):
        """Main compression logic"""
        try:
            self.status_updated.emit("Initializing compression...")
            
            # Validate input file
            if not os.path.exists(self.settings.input_file):
                raise FileNotFoundError(f"Input file not found: {self.settings.input_file}")
            
            # Open input container
            input_container = av.open(self.settings.input_file)
            
            # Get video stream
            video_stream = input_container.streams.video[0]
            if not video_stream:
                raise ValueError("No video stream found in input file")
            
            # Calculate total frames for progress tracking
            total_frames = video_stream.frames
            if total_frames == 0:
                # Estimate based on duration and frame rate
                if hasattr(video_stream, 'duration') and video_stream.duration:
                    if hasattr(video_stream, 'average_rate') and video_stream.average_rate:
                        total_frames = int(video_stream.duration * float(video_stream.average_rate))
                    else:
                        total_frames = int(video_stream.duration * 30)  # Assume 30fps
                else:
                    total_frames = 1000  # Fallback estimate
            
            self.status_updated.emit(f"Processing {total_frames} frames...")
            
            # Setup encoder with fallback logic
            encoder_name = self.system_detector.get_optimal_encoder(self.settings.codec)
            self.status_updated.emit(f"Trying encoder: {encoder_name}")
            
            # Open output container
            output_container = av.open(self.settings.output_file, mode='w')
            
            # Setup video encoding parameters with fallback
            video_output_stream = None
            fallback_encoders = self.system_detector.get_fallback_encoders(self.settings.codec)
            
            for attempt_encoder in [encoder_name] + fallback_encoders:
                try:
                    self.status_updated.emit(f"Attempting encoder: {attempt_encoder}")
                    video_output_stream = self.setup_video_encoder(
                        output_container, attempt_encoder, video_stream
                    )
                    self.status_updated.emit(f"✅ Using encoder: {attempt_encoder}")
                    break
                except Exception as e:
                    self.status_updated.emit(f"❌ Encoder {attempt_encoder} failed: {str(e)}")
                    continue
            
            if not video_output_stream:
                raise RuntimeError("No working video encoder found")
            
            # Setup audio encoding if audio stream exists
            audio_output_stream = None
            if input_container.streams.audio:
                audio_output_stream = self.setup_audio_encoder(
                    output_container, input_container.streams.audio[0]
                )
            
            # Process frames
            processed_frames = 0
            
            # Decode and encode video frames
            for frame in input_container.decode(video=0):
                if self.is_cancelled:
                    break
                    
                # Resize frame if needed
                if self.settings.resolution != "original":
                    frame = self.resize_frame(frame)
                
                # Encode frame
                for packet in video_output_stream.encode(frame):
                    output_container.mux(packet)
                
                processed_frames += 1
                progress = min(100, int((processed_frames / total_frames) * 100))
                self.progress_updated.emit(progress)
                
                if processed_frames % 30 == 0:  # Update status every 30 frames
                    self.status_updated.emit(f"Processed {processed_frames}/{total_frames} frames")
            
            # Process audio if available
            if audio_output_stream:
                self.status_updated.emit("Processing audio...")
                for frame in input_container.decode(audio=0):
                    if self.is_cancelled:
                        break
                    for packet in audio_output_stream.encode(frame):
                        output_container.mux(packet)
            
            # Flush encoders
            if not self.is_cancelled:
                self.status_updated.emit("Finalizing...")
                
                # Flush video encoder
                for packet in video_output_stream.encode():
                    output_container.mux(packet)
                
                # Flush audio encoder
                if audio_output_stream:
                    for packet in audio_output_stream.encode():
                        output_container.mux(packet)
            
            # Close containers
            input_container.close()
            output_container.close()
            
            if self.is_cancelled:
                self.finished.emit(False, "Compression cancelled by user")
            else:
                self.status_updated.emit("Compression completed successfully!")
                self.progress_updated.emit(100)
                self.finished.emit(True, "Compression completed successfully!")
                
        except Exception as e:
            error_msg = f"Compression failed: {str(e)}"
            self.status_updated.emit(error_msg)
            self.finished.emit(False, error_msg)
        finally:
            # Cleanup
            gc.collect()
    
    def setup_video_encoder(self, output_container, encoder_name: str, input_stream):
        """Setup video encoder with GPU acceleration"""
        try:
            # Create output video stream
            output_stream = output_container.add_stream(encoder_name)
        except Exception as e:
            raise RuntimeError(f"Failed to create stream with encoder {encoder_name}: {str(e)}")
        
        # Set resolution
        if self.settings.resolution == "original":
            output_stream.width = input_stream.width
            output_stream.height = input_stream.height
        else:
            width, height = self.get_resolution_dimensions(self.settings.resolution)
            output_stream.width = width
            output_stream.height = height
        
        # Set frame rate
        if self.settings.fps == "original":
            if hasattr(input_stream, 'average_rate') and input_stream.average_rate:
                output_stream.rate = input_stream.average_rate
            elif hasattr(input_stream, 'base_rate') and input_stream.base_rate:
                output_stream.rate = input_stream.base_rate
            else:
                output_stream.rate = 30  # Default fallback
        else:
            output_stream.rate = int(self.settings.fps)
        
        # Set pixel format
        output_stream.pix_fmt = 'yuv420p'
        
        # Configure codec options
        codec_context = output_stream.codec_context
        
        # Quality settings
        if self.settings.quality_mode == "crf":
            if 'nvenc' in encoder_name:
                # Use different CRF parameter for NVENC
                if 'h264_nvenc' in encoder_name:
                    codec_context.options['crf'] = str(self.settings.crf_value)
                else:
                    codec_context.options['cq'] = str(self.settings.crf_value)
                codec_context.options['preset'] = 'medium'  # Use fixed preset for stability
            elif 'qsv' in encoder_name:
                codec_context.options['global_quality'] = str(self.settings.crf_value)
            else:
                codec_context.options['crf'] = str(self.settings.crf_value)
                codec_context.options['preset'] = self.settings.preset
        else:
            codec_context.bit_rate = self.parse_bitrate(self.settings.bitrate)
        
        # Threading
        if self.settings.threads > 0:
            codec_context.thread_count = self.settings.threads
        
        return output_stream
    
    def setup_audio_encoder(self, output_container, input_stream):
        """Setup audio encoder"""
        output_stream = output_container.add_stream(self.settings.audio_codec)
        
        # Set audio properties safely
        if hasattr(input_stream, 'sample_rate'):
            output_stream.sample_rate = input_stream.sample_rate
        elif hasattr(input_stream, 'rate'):
            output_stream.sample_rate = input_stream.rate
        else:
            output_stream.sample_rate = 44100  # Default fallback
            
        if hasattr(input_stream, 'layout'):
            output_stream.layout = input_stream.layout
        else:
            output_stream.layout = 'stereo'  # Default fallback
        
        # Set bitrate
        output_stream.codec_context.bit_rate = self.parse_bitrate(self.settings.audio_bitrate)
        
        return output_stream
    
    def resize_frame(self, frame):
        """Resize frame to target resolution"""
        width, height = self.get_resolution_dimensions(self.settings.resolution)
        return frame.reformat(width=width, height=height)
    
    def get_resolution_dimensions(self, resolution: str) -> Tuple[int, int]:
        """Get width and height for resolution preset"""
        resolutions = {
            "1080p": (1920, 1080),
            "720p": (1280, 720),
            "480p": (854, 480)
        }
        return resolutions.get(resolution, (1920, 1080))
    
    def parse_bitrate(self, bitrate_str: str) -> int:
        """Parse bitrate string to integer (bps)"""
        bitrate_str = bitrate_str.upper()
        if bitrate_str.endswith('K'):
            return int(float(bitrate_str[:-1]) * 1000)
        elif bitrate_str.endswith('M'):
            return int(float(bitrate_str[:-1]) * 1000000)
        else:
            return int(bitrate_str)

class CompressProMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.system_detector = SystemDetector()
        self.compression_worker = None
        self.settings = CompressionSettings()
        self.settings_file = Path.home() / ".comprespro_settings.json"
        
        self.setup_ui()
        self.load_settings()
        self.update_gpu_info()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(900, 700)
        
        # Apply Nord theme
        self.setStyleSheet("""QMainWindow {
            background-color: #2E3440;
        }
        QWidget {
            background-color: #2E3440;
            color: #ECEFF4;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #4C566A;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #88C0D0;
        }
        QLabel {
            color: #D8DEE9;
        }
        QPushButton {
            background-color: #5E81AC;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            color: #ECEFF4;
        }
        QPushButton:hover {
            background-color: #81A1C1;
        }
        QPushButton:pressed {
            background-color: #4C566A;
        }
        QPushButton:disabled {
            background-color: #4C566A;
            color: #6C7B95;
        }
        QLineEdit, QComboBox, QSpinBox {
            background-color: #3B4252;
            border: 2px solid #4C566A;
            border-radius: 4px;
            padding: 6px;
            color: #ECEFF4;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border-color: #88C0D0;
        }
        QProgressBar {
            border: 2px solid #4C566A;
            border-radius: 8px;
            text-align: center;
            background-color: #3B4252;
        }
        QProgressBar::chunk {
            background-color: #A3BE8C;
            border-radius: 6px;
        }
        QTextEdit {
            background-color: #3B4252;
            border: 2px solid #4C566A;
            border-radius: 4px;
            color: #ECEFF4;
            font-family: 'Consolas', 'Monaco', monospace;
        }""")
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        self.create_header(main_layout)
        
        # Content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Settings
        settings_widget = self.create_settings_panel()
        splitter.addWidget(settings_widget)
        
        # Right panel - Processing and logs
        processing_widget = self.create_processing_panel()
        splitter.addWidget(processing_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 500])
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_header(self, layout):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5E81AC, stop:1 #88C0D0);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # App info
        app_label = QLabel(f"🎬 {APP_NAME}")
        app_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        app_label.setToolTip("Professional video compression tool with universal GPU acceleration")
        header_layout.addWidget(app_label)
        
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("font-size: 14px; color: #E5E9F0; margin-top: 8px;")
        version_label.setToolTip(f"Current version: {APP_VERSION}\nBuilt with PyAV for maximum compatibility")
        header_layout.addWidget(version_label)
        
        header_layout.addStretch()
        
        # Donation button
        donate_btn = QPushButton("💖 Support Development")
        donate_btn.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        donate_btn.setToolTip("Support the developer via PayPal\nClick to open donation page in browser")
        donate_btn.clicked.connect(lambda: webbrowser.open(DONATION_URL))
        header_layout.addWidget(donate_btn)
        
        layout.addWidget(header_frame)
    
    def create_settings_panel(self):
        """Create settings panel"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # File Selection Group
        file_group = QGroupBox("📁 File Selection")
        file_group.setToolTip("Select input video file and choose output location")
        file_layout = QVBoxLayout(file_group)
        
        # Input file
        input_layout = QHBoxLayout()
        input_label = QLabel("Input File:")
        input_label.setToolTip("Select the video file you want to compress")
        input_layout.addWidget(input_label)
        
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setToolTip("Path to your input video file (supports MP4, MOV, AVI, MKV, etc.)")
        self.input_file_edit.setPlaceholderText("Select a video file to compress...")
        input_layout.addWidget(self.input_file_edit)
        
        input_browse_btn = QPushButton("Browse")
        input_browse_btn.setToolTip("Click to browse and select your input video file")
        input_browse_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(input_browse_btn)
        file_layout.addLayout(input_layout)
        
        # Output file
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        output_label.setToolTip("Choose where to save the compressed video")
        output_layout.addWidget(output_label)
        
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setToolTip("Path where the compressed video will be saved")
        self.output_file_edit.setPlaceholderText("Choose output location...")
        output_layout.addWidget(self.output_file_edit)
        
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.setToolTip("Click to choose where to save the compressed video")
        output_browse_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(output_browse_btn)
        file_layout.addLayout(output_layout)
        
        settings_layout.addWidget(file_group)
        
        # Compression Settings Group
        compression_group = QGroupBox("⚙️ Compression Settings")
        compression_group.setToolTip("Configure video compression parameters\n"
                                    "These settings control output quality and file size")
        compression_layout = QFormLayout(compression_group)
        
        # Codec selection
        codec_label = QLabel("Video Codec:")
        codec_label.setToolTip("Choose the video compression format")
        
        self.codec_combo = QComboBox()
        self.codec_combo.addItems([
            "H.264 - Best compatibility",
            "H.265 - Better compression", 
            "VP9 - Open source",
            "AV1 - Next generation (experimental)"
        ])
        self.codec_combo.setToolTip("H.264: Best for compatibility (most devices)\n"
                                   "H.265: 50% smaller files than H.264\n"
                                   "VP9: Open source, used by YouTube\n"
                                   "AV1: Latest technology, experimental")
        compression_layout.addRow(codec_label, self.codec_combo)
        
        # Quality mode
        quality_mode_label = QLabel("Quality Mode:")
        quality_mode_label.setToolTip("Choose how to control video quality")
        
        self.quality_mode_combo = QComboBox()
        self.quality_mode_combo.addItems(["CRF (Constant Quality)", "Bitrate (Fixed Size)"])
        self.quality_mode_combo.setToolTip("CRF: Consistent quality, variable file size (recommended)\n"
                                          "Bitrate: Fixed file size, variable quality")
        self.quality_mode_combo.currentTextChanged.connect(self.on_quality_mode_changed)
        compression_layout.addRow(quality_mode_label, self.quality_mode_combo)
        
        # CRF value
        crf_label = QLabel("CRF Value:")
        crf_label.setToolTip("Constant Rate Factor - controls video quality")
        
        self.crf_spin = QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(23)
        self.crf_spin.setToolTip("Lower values = better quality, larger file\n"
                                "18: Visually lossless\n"
                                "23: Default, good quality\n"
                                "28: Lower quality, smaller file\n"
                                "Range: 0 (lossless) to 51 (worst)")
        compression_layout.addRow(crf_label, self.crf_spin)
        
        # Bitrate
        bitrate_label = QLabel("Bitrate:")
        bitrate_label.setToolTip("Target bitrate for fixed file size mode")
        
        self.bitrate_edit = QLineEdit("1M")
        self.bitrate_edit.setToolTip("Target bitrate for video encoding\n"
                                    "Examples: 500K, 1M, 2.5M, 5M\n"
                                    "Higher = better quality, larger file\n"
                                    "1080p typical: 2-8M | 720p typical: 1-4M")
        compression_layout.addRow(bitrate_label, self.bitrate_edit)
        
        # Resolution
        resolution_label = QLabel("Resolution:")
        resolution_label.setToolTip("Choose output video resolution")
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Original", "1080p", "720p", "480p"
        ])
        self.resolution_combo.setToolTip("Original: Keep same resolution as input\n"
                                        "1080p: 1920x1080 (Full HD)\n"
                                        "720p: 1280x720 (HD)\n"
                                        "480p: 854x480 (SD)\n"
                                        "Lower resolution = smaller file size")
        compression_layout.addRow(resolution_label, self.resolution_combo)
        
        # Frame rate
        fps_label = QLabel("Frame Rate:")
        fps_label.setToolTip("Choose output video frame rate (fps)")
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([
            "Original", "24", "30", "60"
        ])
        self.fps_combo.setToolTip("Original: Keep same frame rate as input\n"
                                 "24fps: Cinema/Film standard\n"
                                 "30fps: TV/Web standard\n"
                                 "60fps: High motion/Gaming\n"
                                 "Higher fps = smoother motion, larger file")
        compression_layout.addRow(fps_label, self.fps_combo)
        
        settings_layout.addWidget(compression_group)
        
        # Hardware Acceleration Group
        hw_group = QGroupBox("🚀 Hardware Acceleration")
        hw_group.setToolTip("Configure GPU acceleration and encoding performance\n"
                           "Hardware acceleration can significantly speed up compression")
        hw_layout = QFormLayout(hw_group)
        
        gpu_label = QLabel("Acceleration:")
        gpu_label.setToolTip("Choose hardware acceleration method")
        
        self.gpu_combo = QComboBox()
        self.gpu_combo.addItems([
            "Auto (Recommended)",
            "NVIDIA NVENC",
            "Intel QuickSync",
            "AMD VAAPI",
            "CPU Only"
        ])
        self.gpu_combo.setToolTip("Auto: Automatically selects best available\n"
                                 "NVIDIA NVENC: Uses NVIDIA GPU acceleration\n"
                                 "Intel QuickSync: Uses Intel integrated graphics\n"
                                 "AMD VAAPI: Uses AMD GPU acceleration\n"
                                 "CPU Only: Software encoding (slower but compatible)")
        hw_layout.addRow(gpu_label, self.gpu_combo)
        
        # Preset
        preset_label = QLabel("Preset:")
        preset_label.setToolTip("Balance between encoding speed and compression efficiency")
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "ultrafast", "fast", "medium", "slow", "veryslow"
        ])
        self.preset_combo.setCurrentText("medium")
        self.preset_combo.setToolTip("ultrafast: Fastest encoding, larger files\n"
                                    "fast: Good speed, reasonable compression\n"
                                    "medium: Balanced (recommended)\n"
                                    "slow: Better compression, slower\n"
                                    "veryslow: Best compression, very slow")
        hw_layout.addRow(preset_label, self.preset_combo)
        
        # Threads
        threads_label = QLabel("CPU Threads:")
        threads_label.setToolTip("Number of CPU cores to use for encoding")
        
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(0, psutil.cpu_count())
        self.threads_spin.setValue(0)
        self.threads_spin.setSpecialValueText("Auto")
        self.threads_spin.setToolTip(f"Number of CPU threads to use\n"
                                    f"Auto: Uses optimal number automatically\n"
                                    f"Your system has {psutil.cpu_count()} CPU cores available\n"
                                    f"More threads = faster encoding (up to a limit)")
        hw_layout.addRow(threads_label, self.threads_spin)
        
        # GPU info label
        gpu_status_label = QLabel("GPU Status:")
        gpu_status_label.setToolTip("Current GPU acceleration status and capabilities")
        
        self.gpu_info_label = QLabel()
        self.gpu_info_label.setToolTip("Shows detected GPU hardware and acceleration support")
        hw_layout.addRow(gpu_status_label, self.gpu_info_label)
        
        settings_layout.addWidget(hw_group)
        
        settings_layout.addStretch()
        
        return settings_widget
    
    def create_processing_panel(self):
        """Create processing panel"""
        processing_widget = QWidget()
        processing_layout = QVBoxLayout(processing_widget)
        
        # Control buttons
        control_group = QGroupBox("🎮 Controls")
        control_group.setToolTip("Start compression or cancel current operation")
        control_layout = QHBoxLayout(control_group)
        
        self.start_btn = QPushButton("🚀 Start Compression")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C;
                font-size: 16px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B8D19F;
            }
        """)
        self.start_btn.setToolTip("Start compressing the video with current settings\n"
                                 "Make sure to select input and output files first!")
        self.start_btn.clicked.connect(self.start_compression)
        control_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("⏹️ Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Stop the current compression process\n"
                                  "This will cancel the encoding and delete partial output")
        self.cancel_btn.clicked.connect(self.cancel_compression)
        control_layout.addWidget(self.cancel_btn)
        
        processing_layout.addWidget(control_group)
        
        # Progress group
        progress_group = QGroupBox("📊 Progress")
        progress_group.setToolTip("Monitor compression progress and current status")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setToolTip("Shows compression progress percentage\n"
                                    "Progress is based on frames processed")
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to compress")
        self.status_label.setWordWrap(True)
        self.status_label.setToolTip("Current status of the compression process\n"
                                    "Shows encoder being used, errors, and completion status")
        progress_layout.addWidget(self.status_label)
        
        processing_layout.addWidget(progress_group)
            
        # System Info Group
        system_group = QGroupBox("💻 System Information")
        system_group.setToolTip("Information about your system hardware and software")
        system_layout = QFormLayout(system_group)
        
        # CPU info
        cpu_label = QLabel("CPU:")
        cpu_label.setToolTip("Your system's CPU information")
        
        cpu_count = self.system_detector.cpu_info['count']
        cpu_info = f"{cpu_count} cores"
        cpu_info_label = QLabel(cpu_info)
        cpu_info_label.setToolTip(f"Your system has {cpu_count} CPU cores available for encoding")
        system_layout.addRow(cpu_label, cpu_info_label)
        
        # Memory info
        memory_label = QLabel("RAM:")
        memory_label.setToolTip("Your system's memory information")
        
        memory = self.system_detector.memory_info
        memory_gb = memory['total'] / (1024**3)
        memory_info = f"{memory_gb:.1f} GB total"
        memory_info_label = QLabel(memory_info)
        memory_info_label.setToolTip(f"Your system has {memory_gb:.1f} GB total RAM\n"
                                    f"More RAM allows processing larger videos")
        system_layout.addRow(memory_label, memory_info_label)
        
        # PyAV version
        engine_label = QLabel("Engine:")
        engine_label.setToolTip("Video processing engine information")
        
        pyav_version = f"PyAV {av.__version__}"
        pyav_version_label = QLabel(pyav_version)
        pyav_version_label.setToolTip(f"PyAV {av.__version__} - Python binding for FFmpeg\n"
                                     f"Provides universal codec support without external dependencies")
        system_layout.addRow(engine_label, pyav_version_label)
        
        processing_layout.addWidget(system_group)
        
        # Log output
        log_group = QGroupBox("📝 Processing Log")
        log_group.setToolTip("Detailed log messages from the compression process")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(200)
        self.log_output.setReadOnly(True)
        self.log_output.setToolTip("Detailed log of the compression process\n"
                                  "Shows encoder attempts, progress updates, and error details\n"
                                  "Automatically scrolls to show latest messages")
        log_layout.addWidget(self.log_output)
        
        processing_layout.addWidget(log_group)
        
        return processing_widget
    
    def update_gpu_info(self):
        """Update GPU information display"""
        gpu_info = self.system_detector.gpu_info
        
        status_parts = []
        if gpu_info['nvenc']:
            status_parts.append("✅ NVIDIA")
        if gpu_info['qsv']:
            status_parts.append("✅ Intel")
        if gpu_info['vaapi']:
            status_parts.append("✅ AMD")
        if gpu_info['videotoolbox']:
            status_parts.append("✅ Apple")
            
        if status_parts:
            status_text = " | ".join(status_parts)
        else:
            status_text = "⚠️ CPU Only"
            
        self.gpu_info_label.setText(status_text)
        self.gpu_info_label.setStyleSheet("color: #A3BE8C; font-weight: bold;")
    
    def on_quality_mode_changed(self):
        """Handle quality mode change"""
        is_crf = "CRF" in self.quality_mode_combo.currentText()
        self.crf_spin.setEnabled(is_crf)
        self.bitrate_edit.setEnabled(not is_crf)
    
    def browse_input_file(self):
        """Browse for input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input Video File", "", 
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v);;All Files (*)"
        )
        if file_path:
            self.input_file_edit.setText(file_path)
            
            # Auto-generate output filename
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_compressed.mp4"
            self.output_file_edit.setText(str(output_path))
    
    def browse_output_file(self):
        """Browse for output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed Video As", "", 
            "MP4 Files (*.mp4);;MKV Files (*.mkv);;All Files (*)"
        )
        if file_path:
            self.output_file_edit.setText(file_path)
    
    def start_compression(self):
        """Start video compression"""
        if not self.validate_settings():
            return
            
        # Update settings from UI
        self.update_settings_from_ui()
        
        # Disable start button and enable cancel
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.log_output.clear()
        
        # Create and start worker thread
        self.compression_worker = VideoCompressionWorker(self.settings, self.system_detector)
        self.compression_worker.progress_updated.connect(self.progress_bar.setValue)
        self.compression_worker.status_updated.connect(self.update_status)
        self.compression_worker.finished.connect(self.on_compression_finished)
        self.compression_worker.start()
    
    def cancel_compression(self):
        """Cancel compression"""
        if self.compression_worker:
            self.compression_worker.cancel()
            self.update_status("Cancelling compression...")
    
    def validate_settings(self):
        """Validate compression settings"""
        if not self.input_file_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Please select an input file.")
            return False
            
        if not self.output_file_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Please specify an output file.")
            return False
            
        if not os.path.exists(self.input_file_edit.text()):
            QMessageBox.warning(self, "Warning", "Input file does not exist.")
            return False
            
        return True
    
    def update_settings_from_ui(self):
        """Update settings from UI controls"""
        self.settings.input_file = self.input_file_edit.text()
        self.settings.output_file = self.output_file_edit.text()
        
        # Codec mapping
        codec_map = {
            "H.264 - Best compatibility": "h264",
            "H.265 - Better compression": "h265", 
            "VP9 - Open source": "vp9",
            "AV1 - Next generation (experimental)": "av1"
        }
        self.settings.codec = codec_map[self.codec_combo.currentText()]
        
        self.settings.quality_mode = "crf" if "CRF" in self.quality_mode_combo.currentText() else "bitrate"
        self.settings.crf_value = self.crf_spin.value()
        self.settings.bitrate = self.bitrate_edit.text()
        self.settings.resolution = self.resolution_combo.currentText().lower()
        self.settings.fps = self.fps_combo.currentText().lower()
        
        # GPU acceleration mapping
        gpu_map = {
            "Auto (Recommended)": "auto",
            "NVIDIA NVENC": "nvenc",
            "Intel QuickSync": "qsv", 
            "AMD VAAPI": "vaapi",
            "CPU Only": "cpu"
        }
        self.settings.gpu_acceleration = gpu_map[self.gpu_combo.currentText()]
        
        self.settings.preset = self.preset_combo.currentText()
        self.settings.threads = self.threads_spin.value()
    
    def update_status(self, message):
        """Update status label and log"""
        self.status_label.setText(message)
        self.log_output.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_compression_finished(self, success, message):
        """Handle compression completion"""
        # Re-enable controls
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            self.update_status("✅ " + message)
            QMessageBox.information(self, "Success", message)
        else:
            self.update_status("❌ " + message)
            QMessageBox.critical(self, "Error", message)
        
        # Save settings on successful completion
        if success:
            self.save_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings_data = {
                'codec': self.codec_combo.currentText(),
                'quality_mode': self.quality_mode_combo.currentText(),
                'crf_value': self.crf_spin.value(),
                'bitrate': self.bitrate_edit.text(),
                'resolution': self.resolution_combo.currentText(),
                'fps': self.fps_combo.currentText(),
                'gpu_acceleration': self.gpu_combo.currentText(),
                'preset': self.preset_combo.currentText(),
                'threads': self.threads_spin.value()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def load_settings(self):  
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                # Apply loaded settings
                if 'codec' in settings_data:
                    index = self.codec_combo.findText(settings_data['codec'])
                    if index >= 0:
                        self.codec_combo.setCurrentIndex(index)
                        
                if 'quality_mode' in settings_data:
                    index = self.quality_mode_combo.findText(settings_data['quality_mode'])
                    if index >= 0:
                        self.quality_mode_combo.setCurrentIndex(index)
                        
                if 'crf_value' in settings_data:
                    self.crf_spin.setValue(settings_data['crf_value'])
                    
                if 'bitrate' in settings_data:
                    self.bitrate_edit.setText(settings_data['bitrate'])
                    
                if 'resolution' in settings_data:
                    index = self.resolution_combo.findText(settings_data['resolution'])
                    if index >= 0:
                        self.resolution_combo.setCurrentIndex(index)
                        
                if 'fps' in settings_data:
                    index = self.fps_combo.findText(settings_data['fps'])
                    if index >= 0:
                        self.fps_combo.setCurrentIndex(index)
                        
                if 'gpu_acceleration' in settings_data:
                    index = self.gpu_combo.findText(settings_data['gpu_acceleration'])
                    if index >= 0:
                        self.gpu_combo.setCurrentIndex(index)
                        
                if 'preset' in settings_data:
                    index = self.preset_combo.findText(settings_data['preset'])
                    if index >= 0:
                        self.preset_combo.setCurrentIndex(index)
                        
                if 'threads' in settings_data:
                    self.threads_spin.setValue(settings_data['threads'])
                    
        except Exception as e:
            print(f"Failed to load settings: {e}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.compression_worker and self.compression_worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Compression is in progress. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.compression_worker:
                    self.compression_worker.cancel()
                    self.compression_worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(AUTHOR)
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.ico"))
    except:
        pass
    
    # Create and show main window
    window = CompressProMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 