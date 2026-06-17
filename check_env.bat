@echo off
setlocal
cd /d "%~dp0"

if "%FORMULA_OCR_VENV%"=="" (
    set "VENV_DIR=%LOCALAPPDATA%\FormulaOcrTool\venv313"
) else (
    set "VENV_DIR=%FORMULA_OCR_VENV%"
)

set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if exist "%VENV_PY%" (
    "%VENV_PY%" -m app.check_env
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m app.check_env
) else (
    echo Virtual environment was not found.
    echo Please run setup_env.bat first.
)

pause
