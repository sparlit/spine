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
$xmrigVersion = "6.26.0"
$url = "https://github.com/xmrig/xmrig/releases/download/v$xmrigVersion/xmrig-$xmrigVersion-windows-x64.zip"
$zipFile = "bin\xmrig.zip"

Write-Host "[*] Downloading XMRig v$xmrigVersion..."
try {
    Invoke-WebRequest -Uri $url -OutFile $zipFile -ErrorAction Stop
} catch {
    Write-Host "[!] Failed to download XMRig. Please check your internet connection or URL: $url" -ForegroundColor Red
    return
}

# 5. Extract XMRig
Write-Host "[*] Extracting XMRig..."
try {
    Expand-Archive -Path $zipFile -DestinationPath bin\tmp -Force -ErrorAction Stop
    Move-Item bin\tmp\xmrig-$xmrigVersion\xmrig.exe bin\xmrig.exe -Force -ErrorAction Stop
    Remove-Item $zipFile -Force
    Remove-Item bin\tmp -Recurse -Force
} catch {
    Write-Host "[!] Extraction failed. You might need to manually extract $zipFile to the bin folder." -ForegroundColor Red
}

# 6. Download CUDA Plugin (For NVIDIA GPUs)
Write-Host "[*] Downloading XMRig CUDA Plugin..."
$cudaVersion = "6.22.1"
$cudaUrl = "https://github.com/xmrig/xmrig-cuda/releases/download/v$cudaVersion/xmrig-cuda-$cudaVersion-cuda12_9-win64.zip"
$cudaZip = "bin\cuda.zip"

try {
    Write-Host "[*] Downloading CUDA Plugin from $cudaUrl..."
    Invoke-WebRequest -Uri $cudaUrl -OutFile $cudaZip -ErrorAction Stop
    Write-Host "[*] Extracting CUDA Plugin..."
    Expand-Archive -Path $cudaZip -DestinationPath bin\tmp_cuda -Force -ErrorAction Stop
    Move-Item bin\tmp_cuda\xmrig-cuda.dll bin\xmrig-cuda.dll -Force -ErrorAction Stop
    Remove-Item $cudaZip -Force
    Remove-Item bin\tmp_cuda -Recurse -Force
    Write-Host "[+] CUDA Plugin installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[!] Could not download or install CUDA plugin automatically." -ForegroundColor Yellow
    Write-Host "Error Details: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host "GPU mining might require manual setup. Download from: https://github.com/xmrig/xmrig-cuda/releases" -ForegroundColor Gray
}

Write-Host "[+] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Windows Defender might flag 'xmrig.exe' or 'xmrig-cuda.dll' as a threat."
Write-Host "You must add an exclusion for the 'bin' folder in Windows Security settings."
Write-Host ""
Write-Host "To start mining with TUI, run: python miner_tui.py"
Write-Host "To start the Web Dashboard, run: python miner_web.py"
