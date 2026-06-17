param(
    [string]$PythonExe = "",
    [string]$VenvDir = "",
    [switch]$SkipInstall,
    [switch]$SkipModelPrepare
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "== Formula OCR Tool: build single-file offline exe =="

if (-not $VenvDir) {
    $VenvDir = Join-Path $env:LOCALAPPDATA "FormulaOcrTool\venv313"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment was not found. Creating CPU-only environment first..."
    $setupArgs = @("-ExecutionPolicy", "Bypass", "-File", (Join-Path $ProjectRoot "setup_env.ps1"), "-VenvDir", $VenvDir, "-CpuOnly")
    if ($PythonExe) {
        $setupArgs += @("-PythonExe", $PythonExe)
    }
    & powershell -NoProfile @setupArgs
}

if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment python was not found: $VenvPython"
}

Write-Host "Using Python: $VenvPython"
& $VenvPython --version

if (-not $SkipInstall) {
    Write-Host "Installing build tools and CPU runtime dependencies..."
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install --upgrade pyinstaller pyinstaller-hooks-contrib
    & $VenvPython -m pip install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cpu
    & $VenvPython -m pip uninstall -y torchaudio
    & $VenvPython -m pip install --upgrade -r requirements.txt
}

if (-not $SkipModelPrepare) {
    Write-Host "Preparing pix2tex model files..."
    & $VenvPython scripts\prepare_model_cache.py
}

Write-Host "Building FormulaOcrTool.exe with PyInstaller..."
& $VenvPython -m PyInstaller --clean --noconfirm FormulaOcrTool.spec

$ExePath = Join-Path $ProjectRoot "dist\FormulaOcrTool.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build finished but exe was not found: $ExePath"
}

Write-Host ""
Write-Host "Build finished:"
Write-Host "  $ExePath"
