@echo off
REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment and install requirements
call .venv\Scripts\activate.bat

REM Update pip to latest version
python -m pip install --upgrade pip

REM Install PyQt5 and other requirements
pip install PyQt5
pip install -r requirements.txt

REM Run the application
python besm_app.py

REM Keep the window open
pause 