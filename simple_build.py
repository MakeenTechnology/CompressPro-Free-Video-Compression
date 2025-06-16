#!/usr/bin/env python3
"""
Simple CompressPro Standalone Builder
Creates a single executable using basic PyInstaller
"""

import subprocess
import sys
import shutil
from pathlib import Path

def main():
    print("🎬 Building CompressPro Standalone...")
    print()
    
    # Clean up any previous builds
    for cleanup_dir in ['build', 'dist']:
        if Path(cleanup_dir).exists():
            shutil.rmtree(cleanup_dir)
            print(f"🧹 Cleaned {cleanup_dir}/")
    
    # Basic PyInstaller command for GUI app with embedded libraries
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name=CompressPro",           # Executable name
        "--add-data=requirements.txt;.", # Include requirements for reference
        "main.py"                       # Main script
    ]
    
    print("🔨 Running PyInstaller...")
    print("Command:", " ".join(cmd))
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check executable
            exe_path = Path("dist/CompressPro.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable: {exe_path}")
                print(f"📊 Size: {size_mb:.1f} MB")
                
                # Create simple installer
                installer_dir = Path("Standalone_Installer")
                if installer_dir.exists():
                    shutil.rmtree(installer_dir)
                installer_dir.mkdir()
                
                # Copy executable
                shutil.copy2(exe_path, installer_dir / "CompressPro.exe")
                
                # Create installer batch
                installer_bat = installer_dir / "Install.bat"
                with open(installer_bat, 'w') as f:
                    f.write('''@echo off
echo Installing CompressPro to Desktop...
copy CompressPro.exe "%USERPROFILE%\\Desktop\\CompressPro.exe"
echo Done! Check your Desktop for CompressPro.exe
pause
''')
                
                print("✅ Installer created in Standalone_Installer/")
                return True
            else:
                print("❌ Executable not found")
                return False
        else:
            print("❌ Build failed!")
            print("Error:", result.stderr[-1000:])  # Last 1000 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Standalone build completed!")
        print("📁 Check Standalone_Installer/ folder")
    else:
        print("\n❌ Build failed")
    input("\nPress Enter to continue...") 