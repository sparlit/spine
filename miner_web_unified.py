import sys
import requests
import json
import os
import subprocess
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# API Configurations
XMRIG_API_URL = "http://127.0.0.1:8888/1/summary"
GMINER_API_PORTS = [12345, 12346]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spine Unified Miner Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e11; color: #f0f0f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e2329; border: none; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); }
        .status-active { color: #02c076; }
        .status-offline { color: #f6465d; }
        .stat-value { font-size: 1.8rem; font-weight: bold; color: #ffffff; }
        .stat-label { font-size: 0.8rem; color: #848e9c; text-transform: uppercase; margin-bottom: 5px; }
        .navbar { background-color: #1e2329; border-bottom: 1px solid #2b3139; }
        .gpu-card { border-left: 4px solid #f0b90b; }
        .cpu-card { border-left: 4px solid #00d4ff; }
        .proc-card { border-left: 4px solid #9242f5; }
        .progress { height: 8px; background-color: #2b3139; }
        .progress-bar { background-color: #f0b90b; }
        .badge-cpu { background-color: #00d4ff; color: #000; }
        .badge-gpu { background-color: #f0b90b; color: #000; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1" style="color: #f0b90b;">SPINE UNIFIED DASHBOARD</span>
            <div>
                <span class="badge bg-primary">v2.0 PRO</span>
                <span id="global-status" class="badge bg-secondary">System Scanning...</span>
            </div>
        </div>
    </nav>

    <div class="container">
        <!-- CPU SECTION -->
        <div class="row">
            <div class="col-12"><h4 class="text-muted mb-0"><span class="badge badge-cpu">CPU</span> Engine & Brain</h4></div>
        </div>
        <div class="row g-3" id="cpu-container">
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">CPU Hashrate</div>
                    <div id="cpu-hr" class="stat-value">0.0 H/s</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">CPU Status</div>
                    <div id="cpu-status" class="stat-value status-offline">OFFLINE</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">CPU Uptime</div>
                    <div id="cpu-uptime" class="stat-value">0h 0m</div>
                </div>
            </div>
        </div>

        <!-- GPU SECTION -->
        <div class="row mt-4">
            <div class="col-12"><h4 class="text-muted mb-0"><span class="badge badge-gpu">GPU</span> Engine & Brain</h4></div>
        </div>
        <div class="row g-3" id="gpu-overview">
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">Total GPU Hashrate</div>
                    <div id="gpu-total-hr" class="stat-value">0.00 MH/s</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">GPU Status</div>
                    <div id="gpu-status-text" class="stat-value status-offline">OFFLINE</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="stat-label">GPU Uptime</div>
                    <div id="gpu-uptime-text" class="stat-value">0h 0m</div>
                </div>
            </div>
        </div>
        <div class="row g-3" id="gpu-details">
            <!-- GPU Individual Cards -->
        </div>

        <!-- PROCESS MONITOR SECTION -->
        <div class="row mt-4">
            <div class="col-12"><h4 class="text-muted mb-0">System Process Monitor</h4></div>
        </div>
        <div class="row g-3 mb-5" id="process-container">
            <!-- Process items will be injected here -->
        </div>
    </div>

    <script>
        function formatHashrate(hr, isGpu) {
            if (!isGpu) return hr.toFixed(1) + " H/s";
            if (hr >= 1000000) return (hr / 1000000).toFixed(2) + " MH/s";
            if (hr >= 1000) return (hr / 1000).toFixed(2) + " KH/s";
            return hr.toFixed(2) + " H/s";
        }

        function formatUptime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            return h + "h " + m + "m";
        }

        function updateCpuStats() {
            fetch('/api/cpu')
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('cpu-status').innerText = "OFFLINE";
                        document.getElementById('cpu-status').className = "stat-value status-offline";
                        return;
                    }
                    const hr = data.hashrate ? data.hashrate.total[0] : 0;
                    document.getElementById('cpu-hr').innerText = formatHashrate(hr, false);
                    document.getElementById('cpu-status').innerText = "MINING";
                    document.getElementById('cpu-status').className = "stat-value status-active";
                    document.getElementById('cpu-uptime').innerText = formatUptime(data.uptime || 0);
                })
                .catch(() => {
                    document.getElementById('cpu-status').innerText = "OFFLINE";
                    document.getElementById('cpu-status').className = "stat-value status-offline";
                });
        }

        function updateGpuStats() {
            fetch('/api/gpu')
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('gpu-status-text').innerText = "OFFLINE";
                        document.getElementById('gpu-status-text').className = "stat-value status-offline";
                        document.getElementById('gpu-details').innerHTML = "";
                        return;
                    }
                    document.getElementById('gpu-status-text').innerText = "MINING";
                    document.getElementById('gpu-status-text').className = "stat-value status-active";
                    document.getElementById('gpu-uptime-text').innerText = formatUptime(data.uptime || 0);

                    const devices = data.devices || [];
                    const totalHr = devices.reduce((sum, d) => sum + (d.speed || 0), 0);
                    document.getElementById('gpu-total-hr').innerText = formatHashrate(totalHr, true);

                    let html = "";
                    devices.forEach((gpu, i) => {
                        html += `
                            <div class="col-12">
                                <div class="card p-3 gpu-card">
                                    <div class="row align-items-center text-center text-md-start">
                                        <div class="col-md-3"><strong>${gpu.name}</strong><br><small class="text-muted">GPU #${i}</small></div>
                                        <div class="col-md-2"><div class="stat-label">Speed</div>${formatHashrate(gpu.speed, true)}</div>
                                        <div class="col-md-2"><div class="stat-label">Temp</div><span class="${gpu.temp > 75 ? 'text-danger' : 'text-success'}">${gpu.temp}°C</span></div>
                                        <div class="col-md-2"><div class="stat-label">Power</div>${gpu.power}W</div>
                                        <div class="col-md-3">
                                            <div class="stat-label">Fan ${gpu.fan}%</div>
                                            <div class="progress"><div class="progress-bar" style="width: ${gpu.fan}%"></div></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('gpu-details').innerHTML = html;
                })
                .catch(() => {
                    document.getElementById('gpu-status-text').innerText = "OFFLINE";
                    document.getElementById('gpu-status-text').className = "stat-value status-offline";
                });
        }

        function updateProcesses() {
            fetch('/api/processes')
                .then(res => res.json())
                .then(data => {
                    let html = "";
                    let allOk = true;
                    data.forEach(p => {
                        const statusClass = p.running ? "status-active" : "status-offline";
                        const statusText = p.running ? "RUNNING" : "STOPPED";
                        if (!p.running && p.critical) allOk = false;

                        html += `
                            <div class="col-md-4 col-lg-3">
                                <div class="card p-3 proc-card">
                                    <div class="stat-label">${p.type.toUpperCase()}</div>
                                    <div style="font-size: 1rem; font-weight: bold;">${p.name}</div>
                                    <div class="${statusClass}" style="font-size: 0.8rem; font-weight: bold;">${statusText}</div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('process-container').innerHTML = html;

                    const globalStatus = document.getElementById('global-status');
                    if (allOk) {
                        globalStatus.innerText = "System Healthy";
                        globalStatus.className = "badge bg-success";
                    } else {
                        globalStatus.innerText = "Check Engine/Brain";
                        globalStatus.className = "badge bg-danger";
                    }
                });
        }

        setInterval(updateCpuStats, 3000);
        setInterval(updateGpuStats, 3000);
        setInterval(updateProcesses, 5000);
        updateCpuStats();
        updateGpuStats();
        updateProcesses();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/cpu')
def get_cpu_stats():
    try:
        r = requests.get(XMRIG_API_URL, timeout=1.5)
        return jsonify(r.json())
    except:
        return jsonify({"error": "Offline"}), 500

@app.route('/api/gpu')
def get_gpu_stats():
    for port in GMINER_API_PORTS:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/stat", timeout=0.5)
            if r.status_code == 200:
                return jsonify(r.json())
        except:
            continue
    return jsonify({"error": "Offline"}), 500

def check_process(name, is_python=False):
    try:
        if sys.platform == "win32":
            cmd = f'tasklist /FI "IMAGENAME eq {name}"'
            if is_python:
                # Use powershell for python scripts to match command line
                cmd = f'powershell -Command "Get-Process | Where-Object {{ $_.CommandLine -like \'*{{name}}*\' }}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return name.lower() in result.stdout.lower()
        else:
            cmd = f"pgrep -af {name}" if is_python else f"pgrep -x {name}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            return result.returncode == 0
    except:
        return False

@app.route("/api/processes")
def get_processes():
    processes = [
        {"name": "xmrig", "type": "engine", "critical": False},
        {"name": "miner", "type": "engine", "critical": False},
        {"name": "miner_tui.py", "type": "brain", "critical": False, "python": True},
        {"name": "gpu_unmineable.py", "type": "brain", "critical": False, "python": True},
        {"name": "gpu_nicehash.py", "type": "brain", "critical": False, "python": True},
        {"name": "miner_kanban.py", "type": "brain", "critical": False, "python": True},
        {"name": "miner_web_unified.py", "type": "brain", "critical": True, "python": True}
    ]
    for p in processes:
        p["running"] = check_process(p["name"], p.get("python", False))
    return jsonify(processes)

@app.route("/api/mt5")
def get_mt5_stats():
    data = {
        "status": "OFFLINE",
        "hashrate_cpu": 0.0,
        "hashrate_gpu": 0.0,
        "processes_running": 0,
        "health": "OK"
    }
    try:
        try:
            r_cpu = requests.get(XMRIG_API_URL, timeout=0.5)
            if r_cpu.status_code == 200:
                cpu_json = r_cpu.json()
                data["hashrate_cpu"] = cpu_json.get("hashrate", {}).get("total", [0])[0]
                data["status"] = "MINING"
        except: pass
        for port in GMINER_API_PORTS:
            try:
                r_gpu = requests.get(f"http://127.0.0.1:{port}/stat", timeout=0.3)
                if r_gpu.status_code == 200:
                    gpu_json = r_gpu.json()
                    data["hashrate_gpu"] = sum(d.get("speed", 0) for d in gpu_json.get("devices", []))
                    data["status"] = "MINING"
                    break
            except: continue
        proc_list = ["xmrig", "miner", "miner_tui.py", "gpu_unmineable.py", "gpu_nicehash.py", "miner_web_unified.py"]
        running_count = sum(1 for p in proc_list if check_process(p, p.endswith(".py")))
        data["processes_running"] = running_count
        if running_count < 2: data["health"] = "WARNING"
    except Exception as e:
        data["health"] = f"ERROR: {str(e)}"
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
