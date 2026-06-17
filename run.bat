@echo off
setlocal
cd /d "%~dp0"

set "APP_DIR=%~dp0"
if "%FORMULA_OCR_VENV%"=="" (
    set "VENV_DIR=%LOCALAPPDATA%\FormulaOcrTool\venv313"
) else (
    set "VENV_DIR=%FORMULA_OCR_VENV%"
)
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Virtual environment was not found:
    echo   %VENV_PY%
    echo.
    echo Please run setup_env.bat first.
    pause
    exit /b 1
)

"%VENV_PY%" -m app.main

if errorlevel 1 (
    echo.
    echo App exited with an error. Please send the messages above to Codex.
    pause
)
