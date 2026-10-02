@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
  echo No virtual environment found. Run install.bat first.
  echo.
  pause
  exit /b 1
)

rem pythonw.exe starts the app without a console window.
rem To see error output instead, swap the two lines below.
start "" "venv\Scripts\pythonw.exe" "typing_practice.py"
rem "venv\Scripts\python.exe" "typing_practice.py"
