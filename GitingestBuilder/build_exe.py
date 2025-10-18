"""
Build script to create Windows executable.
Run this script to generate the .exe file.
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    packages = [
        "gitingest",
        "pyinstaller"
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✓ All packages installed")

def build_exe():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name=GitingestDigester",  # Name of the executable
        "--icon=NONE",  # You can add an icon file here if you have one
        "--add-data", "README.txt;.",  # Add any additional files
        "--hidden-import=gitingest",
        "--hidden-import=tiktoken",
        "--hidden-import=pathspec",
        "--collect-all=gitingest",
        "--collect-all=tiktoken",
        "gitingest_gui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*60)
        print("✓ Build successful!")
        print("="*60)
        print("\nYour executable is located at:")
        print("  dist/GitingestDigester.exe")
        print("\nYou can now:")
        print("  1. Copy this .exe file anywhere you want")
        print("  2. Double-click it to run")
        print("  3. Create a desktop shortcut")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

def create_readme():
    """Create a README file for the executable."""
    readme_content = """
Gitingest Folder Digester
=========================

This application converts any folder into a prompt-friendly text digest,
perfect for feeding into AI language models.

HOW TO USE:
-----------
1. Double-click GitingestDigester.exe
2. Click "Browse..." to select a folder
3. Choose where to save the output (optional)
4. Click "Create Digest"
5. Wait for processing to complete
6. Find your digest.txt file!

FEATURES:
---------
- Analyzes entire folder structures
- Respects .gitignore files
- Creates organized file tree
- Estimates token counts for LLMs
- Handles binary files gracefully

REQUIREMENTS:
-------------
- Windows 7 or later
- No Python installation needed!

SUPPORT:
--------
For issues or questions, visit:
https://github.com/coderamp-labs/gitingest

Version: 1.0
"""
    
    Path("README.txt").write_text(readme_content)
    print("✓ README.txt created")

def main():
    print("="*60)
    print("Gitingest Windows Executable Builder")
    print("="*60)
    
    # Check if GUI script exists
    if not Path("gitingest_gui.py").exists():
        print("\n❌ Error: gitingest_gui.py not found!")
        print("Please save the GUI script as 'gitingest_gui.py' first.")
        sys.exit(1)
    
    try:
        # Create README
        create_readme()
        
        # Install requirements
        install_requirements()
        
        # Build executable
        build_exe()
        
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()