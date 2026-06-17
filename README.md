# Spine BTC Miner
A professional Text User Interface (TUI) Bitcoin miner for Windows 11 and Android (Termux).

## Quick Start
1. Read **[GUIDE.md](GUIDE.md)** for setup instructions.
2. Run the setup script for your platform.
3. Run `python miner_tui.py` for CPU mining or `python gpu_unmineable.py` for GPU mining.

## Features
- Real-time hashrate monitoring.
- Automated payout to Binance BTC wallet.
- Optimized for CPU mining (RandomX) and GPU mining (KawPow, Autolykos2, NexPow).
- Specialized GPU miners for **unMineable** and **NiceHash**.
- Automatic GPU benchmarking to select the best algorithm.
- Easy setup for both Mobile and Laptop.

## GPU Web Dashboard
You can monitor your GPU mining progress from any device on your local network.
1. Start the GPU web server: `python miner_web_gpu.py`
2. Open your browser and go to: `http://[LAPTOP-IP-ADDRESS]:5001`

## Native Kanban Dashboard (TUI)
For a professional, high-density overview of your entire mining operation:
1. Run: `python miner_kanban.py`
2. This dashboard aggregates data from both CPU and GPU miners into a native Kanban-style TUI.
