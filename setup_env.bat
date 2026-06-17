@echo off
setlocal
cd /d "%~dp0"

echo == Formula OCR Tool: setup ==
echo.
echo If Python is not found, please install Python 3.13 and enable:
echo   Add python.exe to PATH
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_env.ps1"
set "SETUP_EXIT=%ERRORLEVEL%"

echo.
if not "%SETUP_EXIT%"=="0" (
    echo Setup failed. Please send the messages above to Codex.
    pause
    exit /b %SETUP_EXIT%
)

echo Setup finished. You can double-click run.bat to start the app.
pause
