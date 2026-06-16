#!/bin/bash
# Spine BTC Miner Termux Setup Script

echo "========================================"
echo "   SPINE BTC MINER - TERMUX SETUP       "
echo "========================================"

# 1. Update and install dependencies
echo "[*] Updating packages and installing build tools..."
pkg update -y
pkg install -y git cmake make python clang libuv openssl

# 2. Install Python dependencies
echo "[*] Installing Python dependencies..."
pip install rich

# 3. Create bin directory
mkdir -p bin

# 4. Clone and Build XMRig from source (Best for ARM)
echo "[*] Downloading and compiling XMRig (this may take a few minutes)..."
git clone https://github.com/xmrig/xmrig.git
cd xmrig
mkdir build
cd build
cmake .. -DWITH_HWLOC=OFF # HWLOC is often problematic in Termux
make -j$(nproc)

# 5. Move binary to bin
mv xmrig ../../bin/
cd ../../
rm -rf xmrig

echo "[+] Setup Complete!"
echo ""
echo "To start mining, run: python miner_tui.py"
