# Spine BTC Miner Windows Setup Script (Enhanced with GPU Support)
Write-Host "========================================" -ForegroundColor Blue
Write-Host "   SPINE BTC MINER - WINDOWS SETUP      " -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    return
}

# 2. Install dependencies
Write-Host "[*] Installing Python dependencies..."
pip install rich flask requests

# 3. Create bin directory
if (!(Test-Path bin)) {
    New-Item -ItemType Directory -Path bin
}

# 4. Download XMRig
$xmrigVersion = "6.21.0"
$url = "https://github.com/xmrig/xmrig/releases/download/v$xmrigVersion/xmrig-$xmrigVersion-msvc-win64.zip"
$zipFile = "bin\xmrig.zip"

Write-Host "[*] Downloading XMRig v$xmrigVersion..."
Invoke-WebRequest -Uri $url -OutFile $zipFile

# 5. Extract XMRig
Write-Host "[*] Extracting XMRig..."
Expand-Archive -Path $zipFile -DestinationPath bin\tmp -Force
Move-Item bin\tmp\xmrig-$xmrigVersion\xmrig.exe bin\xmrig.exe -Force
Remove-Item $zipFile
Remove-Item bin\tmp -Recurse

# 6. Download CUDA Plugin (For NVIDIA GPUs)
Write-Host "[*] Downloading XMRig CUDA Plugin..."
$cudaVersion = "6.21.0"
$cudaUrl = "https://github.com/xmrig/xmrig-cuda/releases/download/v$cudaVersion/xmrig-cuda-$cudaVersion-cuda12_0-win64.zip"
$cudaZip = "bin\cuda.zip"

try {
    Invoke-WebRequest -Uri $cudaUrl -OutFile $cudaZip
    Write-Host "[*] Extracting CUDA Plugin..."
    Expand-Archive -Path $cudaZip -DestinationPath bin\tmp -Force
    Move-Item bin\tmp\xmrig-cuda.dll bin\xmrig-cuda.dll -Force
    Remove-Item $cudaZip
    Remove-Item bin\tmp -Recurse
} catch {
    Write-Host "[!] Could not download CUDA plugin automatically. GPU mining might require manual setup." -ForegroundColor Yellow
}

Write-Host "[+] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Windows Defender might flag 'xmrig.exe' or 'xmrig-cuda.dll' as a threat."
Write-Host "You must add an exclusion for the 'bin' folder in Windows Security settings."
Write-Host ""
Write-Host "To start mining with TUI, run: python miner_tui.py"
Write-Host "To start the Web Dashboard, run: python miner_web_unified.py"
