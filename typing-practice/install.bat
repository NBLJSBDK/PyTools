@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo === typing-practice install (Windows) ===
echo.

rem ---- 1. Locate a Python interpreter ----
set "PY="
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY=python"
  )
)
if not defined PY (
  echo ERROR: no usable Python found.
  echo.
  echo Install Python 3.10 or newer and check "Add python.exe to PATH"
  echo during setup, then run this script again.
  echo.
  pause
  exit /b 1
)

%PY% -c "import sys; print('Python: ' + sys.version.split()[0] + '  ' + sys.executable)"
echo.

rem ---- 2. Recreate the virtual environment ----
rem A venv left over from a failed attempt must not break the retry.
if exist venv (
  echo Removing existing venv ...
  rmdir /s /q venv
)

echo Creating venv ...
%PY% -m venv venv
if errorlevel 1 (
  echo.
  echo ERROR: failed to create the virtual environment.
  echo Make sure your Python installation is complete.
  echo.
  pause
  exit /b 2
)

rem ---- 3. Install dependencies ----
echo Installing PyQt5 ...
echo.
venv\Scripts\python.exe -m pip install --disable-pip-version-check "PyQt5==5.15.10"
if errorlevel 1 (
  echo.
  echo ERROR: failed to install PyQt5. Check your network connection.
  echo.
  pause
  exit /b 3
)

rem ---- 4. Verify ----
venv\Scripts\python.exe -c "from PyQt5.QtWidgets import QApplication; from PyQt5.QtMultimedia import QMediaPlayer" >nul 2>nul
if errorlevel 1 (
  echo.
  echo WARNING: PyQt5 is installed but QtWidgets or QtMultimedia failed to import.
  echo Sound effects need QtMultimedia; without it the app runs silently.
  echo.
)

echo.
echo Done. Run:  run.bat
echo.
pause
