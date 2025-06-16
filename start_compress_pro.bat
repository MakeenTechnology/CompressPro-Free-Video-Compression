@echo off
setlocal enabledelayedexpansion

REM ====================================================================
REM  CompressPro v1.2.0 - Professional Video Compression Tool
REM  Automatic Setup and Launcher Script
REM  
REM  Features: Universal GPU Acceleration, Comprehensive Hover Help
REM  Author: AlharthyDev (https://paypal.me/AlharthyDev)
REM ====================================================================

title CompressPro v1.2.0 Setup and Launcher

echo.
echo ===============================================
echo    🎬 CompressPro v1.2.0 Setup & Launcher
echo ===============================================
echo.
echo Professional Video Compression Tool
echo Universal GPU Acceleration + Hover Help System
echo.
echo Author: AlharthyDev
echo Support: https://paypal.me/AlharthyDev
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo Please run this script from the CompressPro folder
    pause
    exit /b 1
)

REM Check GPU acceleration capabilities
echo [INFO] Detecting system capabilities...
echo [INFO] Checking GPU acceleration support...

REM Check for NVIDIA GPU
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] [+] NVIDIA GPU detected - NVENC acceleration available
    set GPU_NVENC=1
) else (
    echo [INFO] [-] NVIDIA GPU not detected
    set GPU_NVENC=0
)

REM Features summary
echo.
echo [INFO] CompressPro v1.2.0 Features:
echo [INFO] [+] Universal GPU Acceleration
echo [INFO] [+] Comprehensive Hover Help System
echo [INFO] [+] Smart Encoder Fallback
echo [INFO] [+] H.264/H.265/VP9/AV1 Support
echo [INFO] [+] Real-time Progress Tracking
echo [INFO] [+] Professional PyQt6 Interface
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo [INFO] Virtual environment found
    call venv\Scripts\activate.bat
    echo [INFO] Activated virtual environment
) else (
    echo [INFO] Creating virtual environment for CompressPro...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        echo Continuing with global Python installation...
    ) else (
        echo [INFO] Virtual environment created successfully
        call venv\Scripts\activate.bat
        echo [INFO] Activated virtual environment
    )
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [WARNING] requirements.txt not found, creating default requirements...
    echo PyQt6^>=6.5.0 > requirements.txt
    echo av^>=12.0.0 >> requirements.txt
    echo psutil^>=5.9.0 >> requirements.txt
    echo numpy^>=1.21.0 >> requirements.txt
    echo opencv-python^>=4.5.0 >> requirements.txt
    echo tqdm^>=4.64.0 >> requirements.txt
    echo [INFO] Created requirements.txt with flexible versioning
)

REM Install or upgrade dependencies
echo [INFO] Installing/updating Python dependencies...
echo [INFO] This may take a few minutes on first run...

pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install some dependencies
    echo [INFO] Trying with alternative PyAV installation...
    
    REM Try alternative PyAV installation methods
    pip install av >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] PyAV installation failed
        echo [INFO] Please install PyAV manually:
        echo [INFO] pip install av
        pause
        exit /b 1
    )
    
    REM Install other dependencies individually
    pip install PyQt6 psutil numpy opencv-python tqdm >nul 2>&1
)

echo [INFO] [+] Dependencies installed successfully

REM Test PyAV availability
echo [INFO] Testing PyAV functionality...
python -c "import av; print(f'PyAV {av.__version__} ready')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] PyAV test failed, but continuing anyway...
) else (
    echo [INFO] [+] PyAV is working correctly
)

REM Test PyQt6 availability
echo [INFO] Testing PyQt6 GUI framework...
python -c "import PyQt6.QtWidgets; print('PyQt6 ready')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PyQt6 is not working correctly
    echo [INFO] Trying to reinstall PyQt6...
    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip >nul 2>&1
    pip install PyQt6 >nul 2>&1
    
    python -c "import PyQt6.QtWidgets; print('PyQt6 ready')" 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] PyQt6 installation failed
        pause
        exit /b 1
    )
)

echo [INFO] [+] PyQt6 is working correctly

REM Summary of system capabilities
echo.
echo ===============================================
echo    🚀 CompressPro System Status
echo ===============================================
echo.

REM Check available encoders
echo [INFO] Checking video encoder availability...
python -c "import av; encoders = av.codec.codecs_available; print(f'Total encoders: {len(encoders)}'); nvenc_count = len([e for e in encoders if 'nvenc' in e]); print(f'NVENC encoders: {nvenc_count}'); print('Sample NVENC:', [e for e in encoders if 'nvenc' in e][:3])" 2>nul

echo.
echo [READY] 🎬 CompressPro v1.2.0 is ready to launch!
echo.
echo Key Features Available:
echo • 🔍 Hover Help: Detailed tooltips on every UI element
echo • ⚡ Smart Fallback: Automatic encoder switching
echo • 🚀 GPU Acceleration: Hardware encoding when available
echo • 📊 Real-time Progress: Frame-based tracking
echo • 💾 Settings Memory: Preferences saved automatically
echo.

REM Ask user if they want to continue
choice /c YN /m "Launch CompressPro now? (Y/N)"
if %errorlevel% equ 2 (
    echo.
    echo Setup completed. Run this script again to launch CompressPro.
    pause
    exit /b 0
)

echo.
echo [INFO] 🚀 Launching CompressPro v1.2.0...
echo [INFO] 💡 Hover over any UI element for detailed help!
echo.

REM Launch the application
python main.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] CompressPro exited with an error
    echo [INFO] Please check the error messages above
    pause
) else (
    echo.
    echo [INFO] CompressPro closed successfully
)

echo.
echo ===============================================
echo    Thanks for using CompressPro v1.2.0!
echo    💖 Support: https://paypal.me/AlharthyDev
echo ===============================================
echo.
pause 