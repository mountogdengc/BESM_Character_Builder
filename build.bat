@echo off
echo Building BESM Character Generator...

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

:: Install/upgrade required packages
pip install -r requirements.txt

:: Run the build script
python build.py

:: Deactivate virtual environment
if exist venv\Scripts\deactivate.bat (
    call venv\Scripts\deactivate.bat
) else if exist .venv\Scripts\deactivate.bat (
    call .venv\Scripts\deactivate.bat
)

echo.
echo Build process complete!
echo The executable can be found in the 'dist' directory.
pause 