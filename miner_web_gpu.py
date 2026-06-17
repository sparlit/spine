from flask import Flask, render_template_string, jsonify
import requests
import json
import os

app = Flask(__name__)

# GMiner API ports configured in gpu scripts
# unMineable: 12345, NiceHash: 12346
GMINER_API_PORTS = [12345, 12346]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spine GPU Miner Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e11; color: #f0f0f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e2329; border: none; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .status-active { color: #02c076; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #ffffff; }
        .stat-label { font-size: 0.85rem; color: #848e9c; text-transform: uppercase; margin-bottom: 5px; }
        .navbar { background-color: #1e2329; border-bottom: 1px solid #2b3139; }
        .gpu-card { border-left: 4px solid #f0b90b; }
        .progress { height: 8px; background-color: #2b3139; }
        .progress-bar { background-color: #f0b90b; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1" style="color: #f0b90b;">SPINE GPU DASHBOARD</span>
            <span class="badge bg-warning text-dark">GPU PRO</span>
        </div>
    </nav>

    <div class="container">
        <div id="connection-status" class="alert alert-danger d-none">
            No active GPU miner detected. Start <b>gpu_unmineable.py</b> or <b>gpu_nicehash.py</b> first.
        </div>

        <div class="row g-4" id="overview-container">
            <!-- Summary Stats -->
        </div>

        <div class="row mt-2" id="gpu-container">
            <!-- GPU Detail Cards -->
        </div>
    </div>

    <script>
        function formatHashrate(hr) {
            if (hr >= 1000000) return (hr / 1000000).toFixed(2) + " MH/s";
            if (hr >= 1000) return (hr / 1000).toFixed(2) + " KH/s";
            return hr.toFixed(2) + " H/s";
        }

        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('connection-status').classList.remove('d-none');
                        return;
                    }
                    document.getElementById('connection-status').classList.add('d-none');

                    const devices = data.devices || [];
                    const totalHr = devices.reduce((sum, d) => sum + (d.speed || 0), 0);

                    const uptimeSec = data.uptime || 0;
                    const hours = Math.floor(uptimeSec / 3600);
                    const minutes = Math.floor((uptimeSec % 3600) / 60);

                    document.getElementById('overview-container').innerHTML = `
                        <div class="col-md-4">
                            <div class="card p-4">
                                <div class="stat-label">Total GPU Hashrate</div>
                                <div class="stat-value">${formatHashrate(totalHr)}</div>
                                <div class="text-warning mt-1" style="font-size: 0.8rem">Algorithm: ${data.algorithm || 'Unknown'}</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-4">
                                <div class="stat-label">System Status</div>
                                <div class="stat-value status-active">MINING</div>
                                <div class="text-muted mt-1" style="font-size: 0.8rem">Version: ${data.version || 'GMiner'}</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-4">
                                <div class="stat-label">Session Uptime</div>
                                <div class="stat-value">${hours}h ${minutes}m</div>
                                <div class="text-muted mt-1" style="font-size: 0.8rem">Running since start</div>
                            </div>
                        </div>
                    `;

                    let gpuHtml = '';
                    devices.forEach((gpu, index) => {
                        gpuHtml += `
                            <div class="col-12">
                                <div class="card p-4 gpu-card">
                                    <div class="row align-items-center">
                                        <div class="col-md-4">
                                            <h5 class="mb-1">${gpu.name}</h5>
                                            <span class="badge bg-dark">GPU #${index}</span>
                                        </div>
                                        <div class="col-md-2 text-center">
                                            <div class="stat-label">Speed</div>
                                            <div class="fw-bold">${formatHashrate(gpu.speed)}</div>
                                        </div>
                                        <div class="col-md-2 text-center">
                                            <div class="stat-label">Temp</div>
                                            <div class="fw-bold ${gpu.temp > 75 ? 'text-danger' : 'text-success'}">${gpu.temp}°C</div>
                                        </div>
                                        <div class="col-md-2 text-center">
                                            <div class="stat-label">Power</div>
                                            <div class="fw-bold">${gpu.power}W</div>
                                        </div>
                                        <div class="col-md-2 text-center">
                                            <div class="stat-label">Fan</div>
                                            <div class="fw-bold">${gpu.fan}%</div>
                                        </div>
                                    </div>
                                    <div class="progress mt-3">
                                        <div class="progress-bar" role="progressbar" style="width: ${gpu.fan}%"></div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('gpu-container').innerHTML = gpuHtml;
                })
                .catch(err => {
                    document.getElementById('connection-status').classList.remove('d-none');
                });
        }

        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    # Try both possible ports (unMineable and NiceHash)
    for port in GMINER_API_PORTS:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/stat", timeout=0.5)
            if r.status_code == 200:
                return jsonify(r.json())
        except:
            continue

    # Mock data for demonstration if no miner is running (optional, but good for testing)
    # return jsonify({
    #     "devices": [{"name": "NVIDIA GeForce RTX 3060", "speed": 25400000, "temp": 62, "fan": 45, "power": 115}],
    #     "algorithm": "kawpow",
    #     "version": "3.44",
    #     "uptime": 1200
    # })

    return jsonify({"error": "No GPU miner detected"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
