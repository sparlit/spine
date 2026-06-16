# Spine BTC Miner - User Guide

This guide will help you set up and run your Bitcoin miner on Windows 11 and Android (Termux).

## 1. Get your Binance BTC Address
To receive your earnings, you need your Bitcoin deposit address from Binance:
1. Log in to your **Binance** account.
2. Go to **Wallet** -> **Fiat and Spot**.
3. Click **Deposit**.
4. Select **BTC** (Bitcoin) as the coin.
5. Select **Bitcoin** as the network.
6. Copy the **Address** shown. It usually starts with `1`, `3`, or `bc1`.

---

## 2. Windows 11 Setup
### Prerequisites
- Install [Python 3.10+](https://www.python.org/downloads/windows/). Make sure to check **"Add Python to PATH"** during installation.

### Installation
1. Open **PowerShell** as Administrator.
2. Navigate to the folder containing these files.
3. Run the setup script:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; .\setup_windows.ps1
   ```
4. **IMPORTANT**: Windows Defender will likely block `bin/xmrig.exe`.
   - Go to **Windows Security** -> **Virus & threat protection**.
   - Under **Virus & threat protection settings**, click **Manage settings**.
   - Scroll down to **Exclusions** and click **Add or remove exclusions**.
   - Click **Add an exclusion** -> **Folder** and select the `bin` folder of this project.

### Running
Run the miner:
```bash
python miner_tui.py
```
Enter your Binance BTC address when prompted.

---

## 3. Android (Termux) Setup
### Prerequisites
- Install **Termux** from [F-Droid](https://f-droid.org/en/packages/com.termux/) (The Play Store version is outdated).

### Installation
1. Open Termux.
2. Grant storage permission: `termux-setup-storage`
3. Run the setup script:
   ```bash
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```

### Running
Run the miner:
```bash
python miner_tui.py
```
Enter your Binance BTC address when prompted.

---

## 4. How it works
- This miner uses the **RandomX** algorithm (optimized for CPUs).
- It connects to the **unMineable** pool.
- Even though it mines Monero (XMR), the pool converts it automatically and pays you in **Bitcoin (BTC)** directly to your Binance wallet.
- **Note**: Mining on mobile/laptops is not highly profitable but is a great way to earn small amounts of BTC "for free" while learning.

## 5. Troubleshooting
- **No Hashrate**: Ensure your internet is connected and no firewall is blocking port 3333.
- **Heat**: Mining makes your device hot. If it's too hot, close the app.
- **Low Earnings**: CPU mining is slow. Keeping the device plugged into power is recommended.


## 6. GPU Mining (Laptop with NVIDIA)
The enhanced version now supports NVIDIA GPU mining via CUDA.
1. Run `setup_windows.ps1` again to download the CUDA plugin.
2. Ensure you have the latest [NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx) installed.
3. The miner will automatically detect and use your RTX GPU.

## 7. Web Dashboard
You can monitor your mining progress from any device on your local network (like your phone).
1. Start the web server: `python miner_web.py`
2. On your phone, open your browser and go to: `http://[LAPTOP-IP-ADDRESS]:5000`
   - To find your laptop IP, run `ipconfig` in CMD on Windows.

## 8. Docker Support
If you prefer running in a container:
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure **NVIDIA Container Toolkit** is enabled.
2. Edit `docker-compose.yml` to put your Binance address.
3. Run: `docker-compose up -d`
4. Access the dashboard at `http://localhost:5000`.

## 9. Performance Tuning
- **Huge Pages**: The miner works best if "Huge Pages" are enabled. On Windows, run the miner as Administrator once to let it configure this automatically.
- **CUDA**: Using the GPU (RTX) alongside the CPU will significantly increase your hashrate.
- **Payouts**: You can change the coin by adding `"coin": "DOGE"` or `"coin": "ETH"` to your `config.json`.

## 10. Pro performance tips for Laptop
To get the absolute best speed out of your RTX Laptop:
- **Plug it in**: Always keep your laptop connected to the charger. Windows slows down the CPU and GPU when on battery.
- **Cooling**: Elevate the back of the laptop or use a cooling pad. Heat causes "thermal throttling" which slows down the miner.
- **Huge Pages**: If you see "Huge Pages: permission denied" in the logs, right-click your terminal (PowerShell) and select "Run as Administrator".
- **GPU Driver**: Make sure you have the [Game Ready or Studio Driver](https://www.nvidia.com/download/index.aspx) from NVIDIA, not the generic Windows ones.
