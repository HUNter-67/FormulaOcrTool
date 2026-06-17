param(
    [string]$PythonExe = "",
    [string]$VenvDir = "",
    [switch]$CpuOnly
)

$ErrorActionPreference = "Stop"

Write-Host "== Formula OCR Tool: setup =="

function Test-PythonExe {
    param([string]$Exe)
    try {
        $output = & $Exe --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        return ($output -match "Python 3\.")
    } catch {
        return $false
    }
}

if (-not $PythonExe) {
    $candidates = @(
        "python",
        "py",
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "C:\Python314\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-PythonExe $candidate) {
            $PythonExe = $candidate
            break
        }
    }
}

if (-not $PythonExe -or -not (Test-PythonExe $PythonExe)) {
    Write-Host ""
    Write-Host "Python was not found."
    Write-Host "Please install Python 3.13 and enable: Add python.exe to PATH."
    Write-Host "Then close and reopen PowerShell, or run:"
    Write-Host '.\setup_env.ps1 -PythonExe "C:\Path\To\python.exe"'
    exit 1
}

Write-Host "Python executable: $PythonExe"
& $PythonExe --version

if (-not $VenvDir) {
    $VenvDir = Join-Path $env:LOCALAPPDATA "FormulaOcrTool\venv313"
}

Write-Host "Virtual environment: $VenvDir"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    $parent = Split-Path -Parent $VenvDir
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    & $PythonExe -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host ""
    Write-Host "Virtual environment was not created successfully."
    Write-Host "Please verify this command works in a new PowerShell window:"
    Write-Host "python --version"
    exit 1
}

Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip

if ($CpuOnly) {
    Write-Host "Installing CPU PyTorch..."
    & $VenvPython -m pip install torch torchvision torchaudio
} else {
    Write-Host "Installing CUDA PyTorch..."
    try {
        & $VenvPython -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    } catch {
        Write-Host "CUDA PyTorch install failed. Falling back to CPU PyTorch..."
        & $VenvPython -m pip install torch torchvision torchaudio
    }
}

Write-Host "Installing app dependencies..."
& $VenvPython -m pip install -r requirements.txt

Write-Host "Running environment check..."
& $VenvPython -m app.check_env

Write-Host ""
Write-Host "Setup finished. Run run.bat to start the app."
Write-Host "The first recognition may download the model. Later use can be offline."
