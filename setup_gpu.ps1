# Spine BTC Miner GPU Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SPINE BTC MINER - GPU SETUP          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    return
}

# 2. Install dependencies
Write-Host "[*] Installing Python dependencies..."
pip install rich requests

# 3. Create bin directory
if (!(Test-Path bin)) {
    New-Item -ItemType Directory -Path bin
}
if (!(Test-Path bin\gminer)) {
    New-Item -ItemType Directory -Path bin\gminer
}

# 4. Download GMiner
$gminerVersion = "3.44"
$gminerVersionUnderscore = "3_44"
$url = "https://github.com/develsoftware/GMinerRelease/releases/download/$gminerVersion/gminer_$($gminerVersionUnderscore)_windows64.zip"
$zipFile = "bin\gminer.zip"

Write-Host "[*] Downloading GMiner v$gminerVersion..."
try {
    Invoke-WebRequest -Uri $url -OutFile $zipFile
} catch {
    Write-Host "[!] Failed to download GMiner. Please check your internet connection or the URL." -ForegroundColor Red
    return
}

# 5. Extract GMiner
Write-Host "[*] Extracting GMiner..."
try {
    Expand-Archive -Path $zipFile -DestinationPath bin\gminer -Force
    Remove-Item $zipFile
} catch {
    Write-Host "[!] Failed to extract GMiner." -ForegroundColor Red
    return
}

Write-Host "[+] GPU Miner Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Windows Defender might flag 'miner.exe' as a threat."
Write-Host "You must add an exclusion for the 'bin' folder in Windows Security settings."
Write-Host ""
Write-Host "To start unMineable GPU mining, run: python gpu_unmineable.py"
Write-Host "To start NiceHash GPU mining, run: python gpu_nicehash.py"
