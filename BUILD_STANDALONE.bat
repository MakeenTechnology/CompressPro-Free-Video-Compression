@echo off
title CompressPro Standalone Builder

echo.
echo ===============================================
echo    🎬 CompressPro v1.2.0 Standalone Builder
echo ===============================================
echo.
echo This will create a single executable with ALL libraries embedded!
echo Users won't need Python or any dependencies installed.
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from: https://python.org
    pause
    exit /b 1
)

echo [INFO] Installing build dependencies...
pip install -r build_requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install build dependencies
    echo [INFO] Try running as Administrator or check your internet connection
    pause
    exit /b 1
)

echo.
echo [INFO] Starting standalone build process...
echo [INFO] This may take 5-10 minutes depending on your system...
echo.

python build_standalone.py

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo    🎉 BUILD COMPLETED SUCCESSFULLY!
    echo ===============================================
    echo.
    echo Your standalone installer is ready:
    echo.
    echo 📁 CompressPro_Installer/
    echo ├── CompressPro.exe (Ready to distribute!)
    echo └── Install_CompressPro.bat (User installer)
    echo.
    echo 🚀 To distribute to users:
    echo   1. Zip the 'CompressPro_Installer' folder
    echo   2. Send to users
    echo   3. Users run 'Install_CompressPro.bat'
    echo.
    echo 💡 The .exe includes ALL dependencies!
    echo    No Python installation required by users.
    echo.
    
    REM Ask if user wants to test the executable
    choice /c YN /m "Test the standalone executable now? (Y/N)"
    if %errorlevel% equ 1 (
        echo.
        echo [INFO] Testing standalone executable...
        if exist "CompressPro_Installer\CompressPro.exe" (
            "CompressPro_Installer\CompressPro.exe"
        ) else (
            echo [ERROR] CompressPro.exe not found!
        )
    )
) else (
    echo.
    echo ===============================================
    echo    ❌ BUILD FAILED!
    echo ===============================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo • Missing dependencies (run: pip install -r requirements.txt)
    echo • Insufficient disk space (needs ~500MB)
    echo • Antivirus blocking PyInstaller
    echo.
)

echo.
echo Thanks for using CompressPro Standalone Builder!
echo 💖 Support: https://paypal.me/AlharthyDev
echo.
pause 