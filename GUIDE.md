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
