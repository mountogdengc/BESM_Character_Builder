import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean up build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    if os.path.exists('BESM_Character_Generator.spec'):
        os.remove('BESM_Character_Generator.spec')

def create_executable():
    """Create the executable using PyInstaller"""
    # Get the absolute path to the project directory
    project_dir = Path(__file__).parent.absolute()
    
    # Define the data files to include
    data_files = [
        ('data', 'data'),
        ('style.qss', '.'),
        ('project-logo.jpg', '.'),
        ('dialogs', 'dialogs'),
        ('tools', 'tools'),
        ('tabs', 'tabs'),
        ('templates', 'templates'),
    ]
    
    # Create the --add-data arguments
    add_data_args = []
    for src, dst in data_files:
        src_path = os.path.join(project_dir, src)
        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                add_data_args.extend(['--add-data', f'{src_path}{os.pathsep}{dst}'])
            else:
                add_data_args.extend(['--add-data', f'{src_path}{os.pathsep}{dst}'])
    
    # Build the PyInstaller command using python -m pyinstaller
    cmd = [
        sys.executable,  # Use the current Python interpreter
        '-m',           # Run as module
        'PyInstaller',
        '--name=BESM_Character_Generator',
        '--windowed',  # No console window
        '--onefile',   # Single executable
        '--clean',     # Clean PyInstaller cache
        '--icon=project-logo.jpg',  # Use the project logo as icon
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=reportlab',
        *add_data_args,
        'besm_app.py'  # Main script
    ]
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)

def main():
    print("Cleaning previous build directories...")
    clean_build_dirs()
    
    print("Creating executable...")
    create_executable()
    
    print("\nBuild complete! The executable can be found in the 'dist' directory.")
    print("Note: The first run may take a few moments as it extracts all resources.")

if __name__ == '__main__':
    main() 