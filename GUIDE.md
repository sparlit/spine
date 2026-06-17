# Spine BTC Miner - User Guide

This guide will help you set up and run your Bitcoin miner on Windows 11 and Android (Termux).

## 1. Get your Payout Address
- **unMineable**: Use your Binance BTC/DOGE/SHIB deposit address.
- **NiceHash**: Use your NiceHash Mining Address (usually starts with `nhwm...`) or your BTC address.

---

## 2. Windows 11 Setup
### Prerequisites
- Install [Python 3.10+](https://www.python.org/downloads/windows/). Make sure to check **"Add Python to PATH"** during installation.

### Installation (CPU)
1. Open **PowerShell** as Administrator.
2. Navigate to the folder.
3. Run: `Set-ExecutionPolicy Bypass -Scope Process -Force; .\setup_windows.ps1`

### Installation (GPU - New!)
1. Open **PowerShell** as Administrator.
2. Run: `Set-ExecutionPolicy Bypass -Scope Process -Force; .\setup_gpu.ps1`
3. This downloads **GMiner** and sets up GPU-specific dependencies.

### Running
- **CPU Mining**: `python miner_tui.py`
- **GPU (unMineable)**: `python gpu_unmineable.py`
- **GPU (NiceHash)**: `python gpu_nicehash.py`

**IMPORTANT**: Windows Defender will likely block `bin/xmrig.exe` or `bin/gminer/miner.exe`. Add an exclusion for the `bin` folder.

---

## 3. Android (Termux) Setup
*(Note: GPU mining is not supported on Termux)*
1. Open Termux.
2. Run: `chmod +x setup_termux.sh && ./setup_termux.sh`
3. Run: `python miner_tui.py`

---

## 4. How it works
- **CPU Miner**: Uses XMRig (RandomX). Best for older laptops or mobile.
- **GPU Miner**: Uses GMiner. Supports KawPow, Autolykos2, and NexPow.
- **Auto-Selection**: On first run, the GPU miner benchmarks your card to pick the most profitable algorithm.

## 5. GPU Mining Details
- **unMineable**: Mines various coins (RVN, ERGO, NEXA) and pays you in your choice of BTC, DOGE, or SHIB.
- **NiceHash**: Mines for the NiceHash marketplace and pays in BTC.

## 6. Pro performance tips for Laptop
- **Plug it in**: Always keep your laptop connected to the charger.
- **Cooling**: Elevate the back of the laptop or use a cooling pad.
- **GPU Driver**: Use latest [NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx).

## 7. GPU Web Dashboard
The specialized GPU dashboard provides real-time hardware metrics.
1. Run `python miner_web_gpu.py` in a separate terminal.
2. Access it at `http://localhost:5001`.
3. It displays GPU Temperature, Power consumption, and Fan speed alongside hashrates.

## 8. Native Kanban Dashboard
The Kanban dashboard (`miner_kanban.py`) is the ultimate monitoring tool for power users.
- **Column 1: Inventory** - Hardware status for both CPU and GPU.
- **Column 2: Strategy** - Current pool, algorithm, and worker info.
- **Column 3: Execution** - Live hashrates and session uptime.
- **Column 4: Telemetry** - Advanced hardware metrics (Temperature, Power, Fan).
- **Usage**: Simply run `python miner_kanban.py` while your miners are running.
