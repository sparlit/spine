import subprocess
import os
import json
import time
import sys
import re

CONFIG_GPU_FILE = "config_gpu.json"

def get_gpu_info():
    """Returns a list of GPUs with their VRAM in MB."""
    try:
        # Try running nvidia-smi
        # On windows, it might not be in PATH but usually is if drivers are installed
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        gpus = []
        for line in output.strip().split('\n'):
            if ',' in line:
                name, vram = line.split(',')
                gpus.append({"name": name.strip(), "vram": int(vram.strip())})
        return gpus
    except:
        # Mock for non-NVIDIA or errors in development
        return [{"name": "NVIDIA GeForce RTX 3060", "vram": 12288}]

def load_gpu_config():
    if os.path.exists(CONFIG_GPU_FILE):
        try:
            with open(CONFIG_GPU_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"benchmarks": {}, "best_algo": None}

def save_gpu_config(config):
    with open(CONFIG_GPU_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def run_benchmark(algo, duration=15):
    """Runs a benchmark for the given algorithm and returns hashrate."""
    gminer_path = os.path.join("bin", "gminer", "miner.exe")
    if not os.path.exists(gminer_path):
        # Mock values for testing logic
        return 10.0 + (5.0 if algo == "kawpow" else 20.0)

    cmd = [
        gminer_path,
        "--algo", algo,
        "--server", "localhost",
        "--port", "1234",
        "--user", "benchmark",
        "--benchmark", "1"
    ]

    try:
        # Use a timeout to ensure benchmark doesn't hang
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        start_time = time.time()
        rates = []
        while time.time() - start_time < duration:
            line = process.stdout.readline()
            if not line: break
            # GMiner output parsing
            match = re.search(r"Speed: ([\d.]+) (H/s|KH/s|MH/s|GH/s)", line)
            if match:
                val = float(match.group(1))
                unit = match.group(2)
                # Convert all to MH/s for relative comparison
                if unit == "KH/s": val /= 1000
                elif unit == "H/s": val /= 1000000
                elif unit == "GH/s": val *= 1000
                rates.append(val)
        process.terminate()
        return sum(rates)/len(rates) if rates else 0
    except:
        return 0

def get_best_algo():
    config = load_gpu_config()
    if config.get("best_algo"):
        return config["best_algo"]

    gpus = get_gpu_info()
    max_vram = max(gpu["vram"] for gpu in gpus) if gpus else 0

    algos = []
    # Algo compatibility based on VRAM
    if max_vram >= 4000:
        algos = ["kawpow", "autolykos2", "nexpow"]
    elif max_vram >= 2000:
        algos = ["autolykos2"]
    else:
        algos = ["autolykos2"]

    # Simple profitability weight (mocked multipliers)
    # These represent relative "value" per unit of hashrate for these algos
    weights = {"kawpow": 1.0, "autolykos2": 0.05, "nexpow": 0.5}

    best_score = -1
    best_algo = algos[0]

    for algo in algos:
        # Quick benchmark for each supported algo
        rate = run_benchmark(algo, duration=15)
        config["benchmarks"][algo] = rate
        score = rate * weights.get(algo, 1.0)
        if score > best_score:
            best_score = score
            best_algo = algo

    config["best_algo"] = best_algo
    save_gpu_config(config)
    return best_algo
