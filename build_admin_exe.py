"""
Build script for creating Windows executable of Fabric Admin App
"""
import os
import shutil
import PyInstaller.__main__

print("Building Fabric Admin App EXE...")
print("="*60)

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# PyInstaller arguments
PyInstaller.__main__.run([
    'admin_app/main.py',              # Entry point
    '--name=FabricAdmin',              # EXE name
    '--onefile',                       # Single executable
    '--windowed',                      # No console window
    '--icon=NONE',                     # No icon (can add later)
    '--add-data=backend;backend',      # Include backend module
    '--hidden-import=PyQt6',           # Ensure PyQt6 is included
    '--hidden-import=qrcode',
    '--hidden-import=gspread',
    '--hidden-import=google.oauth2',
    '--hidden-import=googleapiclient',
    '--hidden-import=PIL',
    '--clean',                         # Clean cache
])

print()
print("="*60)
print("Build complete!")
print()
print("Executable location: dist/FabricAdmin.exe")
print()
print("IMPORTANT: You must place credentials.json in the same")
print("directory as FabricAdmin.exe before running it.")
print("="*60)
