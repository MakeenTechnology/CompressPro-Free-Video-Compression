# 🎬 CompressPro v1.2.0

**Professional Video Compression Made Simple**

A professional-grade video compression application with **universal GPU acceleration** support and **comprehensive hover help**. Built with PyAV for maximum compatibility and performance without requiring external FFmpeg installation.

✨ **NEW**: Complete hover help system with tooltips on every UI element!

![CompressPro](https://img.shields.io/badge/CompressPro-v1.2.0-blue)
![PyAV](https://img.shields.io/badge/PyAV-14.4.0-green)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)
![License](https://img.shields.io/badge/License-MIT-red)

---

## 🌟 **Key Features**

### 🚀 **Universal GPU Acceleration**
- **NVIDIA NVENC**: H.264, H.265, AV1 hardware encoding
- **Intel QuickSync**: Integrated graphics acceleration
- **AMD VAAPI**: AMD GPU acceleration support
- **Apple VideoToolbox**: macOS hardware acceleration
- **Smart Fallback**: Automatically switches to working encoders

### 🎯 **Professional Codec Support**
- **H.264**: Best compatibility, works on all devices
- **H.265 (HEVC)**: 50% smaller files than H.264
- **VP9**: Open source, YouTube standard
- **AV1**: Next-generation compression (experimental)

### 🎛️ **Advanced Quality Control**
- **CRF Mode**: Constant quality, variable file size (recommended)
- **Bitrate Mode**: Fixed file size, variable quality
- **Smart Presets**: Ultrafast to veryslow encoding speeds
- **Resolution Scaling**: Original, 1080p, 720p, 480p options

### 💡 **Comprehensive User Experience**
- **🔍 Hover Help on Everything**: Detailed tooltips on every UI element - perfect for beginners!
- **📊 Real-time Progress**: Frame-based progress tracking with detailed status updates
- **📝 Detailed Logging**: Complete encoder attempt history and error details
- **⚡ Smart Encoder Selection**: Automatic fallback system (tries multiple encoders if one fails)
- **💾 Settings Memory**: Remembers your preferences between sessions
- **🛠️ Robust Error Handling**: Graceful fallback when hardware encoders fail

### 🔧 **Technical Excellence**
- **No External Dependencies**: Self-contained PyAV engine
- **Multi-threaded Processing**: Utilizes all CPU cores
- **Memory Efficient**: Handles large video files
- **Format Support**: MP4, MKV, AVI, MOV, WebM, and more

---

## 🚀 **Quick Start**

### **Option 1: Ready-to-Use Executable (Instant!)** ⚡
**📥 [Download from Releases](../../releases/latest)** - Get `CompressPro.exe` (75MB)

1. **Go to** [Releases page](../../releases/latest)
2. **Download** `CompressPro.exe` from the latest release
3. **Double-click** to run immediately
4. **Start compressing videos!**

*✅ No Python, no installation, no setup required - just download and go!*

### **Option 2: Build Your Own Executable** 🔨
1. **Clone** this repository
2. **Run** `BUILD_STANDALONE.bat` (installs dependencies automatically)
3. **Get** your fresh `CompressPro.exe` in `Standalone_Installer/`

### **Option 3: Python Source (Developers)** 🐍
1. **Clone** the repository:
   ```bash
   git clone https://github.com/yourusername/CompressPro.git
   cd CompressPro
   ```
2. **Run** the auto-installer:
   ```bash
   start_compress_pro.bat    # Windows
   # or
   pip install -r requirements.txt && python main.py
   ```

### **Option 4: Manual Source Installation** 📋
```bash
# Install dependencies manually
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 📋 **Requirements**

### **System Requirements**
- **OS**: Windows 10/11 (executable), macOS/Linux (source code)
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 80MB for executable + space for video files
- **GPU**: Optional but recommended for acceleration
- **Python**: Not required for executable, 3.8+ for source code

### **Python Dependencies**
```txt
PyQt6>=6.5.0
PyAV>=12.0.0
psutil>=5.9.0
numpy>=1.21.0
opencv-python>=4.5.0
tqdm>=4.64.0
```

**For Executable Users**: No dependencies needed - everything is embedded!

**For Source Code Users**: The installer (`start_compress_pro.bat`) automatically handles all dependencies with flexible versioning for maximum compatibility.

---

## 🎯 **How to Use CompressPro**

### **1. 📁 File Selection**
- **Input File**: Browse and select your video file
  - *Supports: MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V*
- **Output File**: Choose where to save compressed video
  - *Auto-generates filename with "_compressed" suffix*

### **2. ⚙️ Compression Settings**

#### **Video Codec Selection**
- **H.264**: Best for compatibility (plays everywhere)
- **H.265**: Better compression (50% smaller files)
- **VP9**: Open source standard (used by YouTube)
- **AV1**: Cutting-edge technology (experimental)

#### **Quality Control**
- **CRF Mode** *(Recommended)*:
  - `18`: Visually lossless quality
  - `23`: Default, excellent quality
  - `28`: Good quality, smaller file
  - `32`: Lower quality, very small file

- **Bitrate Mode**:
  - `500K-1M`: Low quality, small files
  - `2M-5M`: Good quality (1080p standard)
  - `8M-15M`: High quality, larger files

#### **Resolution & Frame Rate**
- **Resolution**: Keep original or downscale (1080p→720p→480p)
- **Frame Rate**: Keep original or set specific (24/30/60 fps)

### **3. 🚀 Hardware Acceleration**

#### **GPU Options**
- **Auto (Recommended)**: Smart selection of best available
- **NVIDIA NVENC**: Use NVIDIA GPU (GTX 1050+)
- **Intel QuickSync**: Use Intel integrated graphics
- **AMD VAAPI**: Use AMD GPU acceleration
- **CPU Only**: Software encoding (slower but universal)

### **4. 🎮 Start Processing**
- Click **🚀 Start Compression**
- Monitor progress in real-time
- View detailed logs of the process
- Cancel anytime if needed

---

## 🎯 **Hover Help System**

**Every UI element has detailed hover tooltips!** Simply hover your mouse over any:

- 🔘 **Buttons** - Learn what each button does
- 📝 **Input Fields** - See format examples and tips
- 📋 **Dropdown Menus** - Understand each option
- 📊 **Progress Bars** - Know what's being tracked
- ℹ️ **Labels** - Get context about settings

**Perfect for beginners** - learn as you go without reading manuals!

---

## 🔧 **Advanced Features**

### **Smart Encoder Fallback**
CompressPro automatically tries multiple encoders if one fails:
1. **Primary encoder** (based on your GPU)
2. **Hardware fallbacks** (alternative GPU encoders)
3. **Software fallback** (guaranteed to work)

### **Multi-threading**
- **Auto-detect**: Uses optimal CPU core count
- **Manual**: Set specific thread count (1-16)
- **Scaling**: More threads = faster encoding (up to hardware limits)

### **Preset Optimization**
- **ultrafast**: Fastest encoding, larger files
- **fast**: Good speed, reasonable compression
- **medium**: Balanced performance (recommended)
- **slow**: Better compression, takes longer
- **veryslow**: Maximum compression, very slow

### **Settings Persistence**
- Automatically saves your preferences
- Restores settings on next launch
- Per-project settings memory

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"Encoder Failed" Error**
- **Solution**: CompressPro automatically tries fallback encoders
- **Check**: GPU Status in Hardware Acceleration section
- **Fallback**: Use "CPU Only" for guaranteed compatibility

#### **GPU Not Detected**
- **NVIDIA**: Ensure drivers are up to date (Game Ready 471.0+)
- **Intel**: Update Intel Graphics drivers
- **AMD**: Install latest AMD Adrenalin drivers

#### **Slow Encoding**
- **Enable GPU acceleration** in Hardware section
- **Lower preset** (ultrafast/fast) for speed
- **Reduce resolution** if file size allows
- **Check CPU usage** - close other applications

#### **Large Output Files**
- **Increase CRF value** (23→28) for smaller files
- **Use H.265** instead of H.264 (50% smaller)
- **Lower resolution** (1080p→720p)
- **Reduce bitrate** in bitrate mode

---

## 💻 **System Information Display**

CompressPro shows real-time system information:

- **CPU**: Core count and threading capability
- **RAM**: Total memory available for processing
- **GPU Status**: Hardware acceleration availability
- **Engine**: PyAV version and codec support

---

## 📦 **What's Included in This Repository**

```
CompressPro/
├── 🐍 Source Code/
│   ├── main.py (Main application)
│   ├── requirements.txt (Dependencies)
│   └── start_compress_pro.bat (Auto-installer)
├── 🔨 Build Tools/
│   ├── simple_build.py (Build executable)
│   ├── BUILD_STANDALONE.bat (One-click builder)
│   └── build_requirements.txt (Build dependencies)
├── 📖 README.md (This file)
└── 🎬 Releases/ (Executables available separately)
```

**🎯 Choose your path:**
- **Just want to use it?** → [Download from Releases](../../releases/latest)
- **Want to modify/develop?** → Use the source code
- **Want to build your own?** → Use the build tools

---

## 🔄 **Update History**

### **v1.2.0** *(Current)*
- ✅ **Standalone Executable**: 75MB self-contained .exe included
- ✅ **Comprehensive hover help** on every UI element
- ✅ **Smart encoder fallback** system
- ✅ **Improved NVENC support** with proper H.264 handling
- ✅ **Enhanced error handling** and user feedback
- ✅ **Better system detection** and GPU status display
- ✅ **Robust PyAV integration** with universal codec support

### **v1.1.0**
- ✅ PyAV-based compression engine
- ✅ Universal GPU acceleration
- ✅ Multi-codec support (H.264, H.265, VP9, AV1)
- ✅ Professional Qt6 interface

### **v1.0.0**
- ✅ Initial release with basic compression

---

## 🤝 **Support & Donations**

If CompressPro has helped you compress videos efficiently, consider supporting development:

**💖 [Support via PayPal](https://paypal.me/AlharthyDev)**

Your support helps maintain and improve CompressPro with new features and better compatibility.

---

## 📄 **License**

MIT License - see LICENSE file for details.

**Free for personal and commercial use** ✅

---

## 🔗 **Technical Details**

### **Architecture**
- **Frontend**: PyQt6 with Nord theme
- **Backend**: PyAV (Python FFmpeg bindings)
- **Threading**: Multi-threaded compression worker
- **GPU**: Direct hardware encoder integration

### **Supported Formats**
- **Input**: MP4, MKV, AVI, MOV, WebM, FLV, WMV, M4V, 3GP
- **Output**: MP4, MKV (with proper container selection)
- **Codecs**: H.264, H.265, VP9, AV1, + 500+ others via PyAV

### **Performance**
- **GPU Acceleration**: 5-10x faster than CPU-only
- **Multi-threading**: Scales with CPU core count
- **Memory Efficient**: Streams processing for large files
- **Smart Caching**: Optimized for repeated operations

---

**🎬 Happy Compressing with CompressPro! 🚀** 