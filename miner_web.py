from flask import Flask, render_template_string, jsonify
import requests
import json
import os

app = Flask(__name__)

# XMRig API is usually on port 8888 as configured in miner_tui.py
XMRIG_API_URL = "http://127.0.0.1:8888/1/summary"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spine Miner Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f0f0f; color: #f0f0f0; font-family: 'Inter', sans-serif; }
        .card { background-color: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; margin-top: 20px; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); border-color: #00d4ff; }
        .status-active { color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
        .stat-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
        .stat-label { font-size: 0.8rem; color: #aaaaaa; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .navbar { background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a; }
        .gpu-badge { background-color: #76b900; color: black; font-weight: bold; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1">SPINE BTC MINER</span>
            <span class="badge bg-primary">v1.1 PRO</span>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            <div class="col-12 text-center">
                <h2 class="fw-light">Real-time Performance</h2>
            </div>
        </div>

        <div class="row g-4" id="stats-container">
            <div class="col-12 text-center py-5">
                <div class="spinner-grow text-info" role="status"></div>
                <p class="mt-3 text-muted">Awaiting connection to XMRig...</p>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-lg-8 offset-lg-2">
                <div class="card p-4">
                    <h5 class="mb-4">System Information</h5>
                    <div class="row" id="sys-info">
                        <div class="col-6"><p class="text-muted">CPU</p><p id="cpu-name">Loading...</p></div>
                        <div class="col-6"><p class="text-muted">Algorithm</p><p id="algo-name">Loading...</p></div>
                        <div class="col-6"><p class="text-muted">Version</p><p id="ver-name">Loading...</p></div>
                        <div class="col-6"><p class="text-muted">GPU Support</p><p id="gpu-status">Loading...</p></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.error) throw new Error(data.error);

                    const hr = data.hashrate ? data.hashrate.total[0] : 0;
                    const uptimeSec = data.uptime || 0;
                    const hours = Math.floor(uptimeSec / 3600);
                    const minutes = Math.floor((uptimeSec % 3600) / 60);
                    const uptimeStr = `${hours}h ${minutes}m`;

                    document.getElementById('stats-container').innerHTML = `
                        <div class="col-md-4">
                            <div class="card text-center p-4">
                                <div class="stat-label">Total Hashrate</div>
                                <div class="stat-value">${hr.toFixed(1)} <span style="font-size: 1rem">H/s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card text-center p-4">
                                <div class="stat-label">Miner Status</div>
                                <div class="stat-value status-active">ONLINE</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card text-center p-4">
                                <div class="stat-label">Session Uptime</div>
                                <div class="stat-value">${uptimeStr}</div>
                            </div>
                        </div>
                    `;

                    document.getElementById('cpu-name').innerText = data.cpu.brand;
                    document.getElementById('algo-name').innerText = data.algo;
                    document.getElementById('ver-name').innerText = data.version;
                    document.getElementById('gpu-status').innerHTML = data.has_gpu ? '<span class="gpu-badge">NVIDIA CUDA ACTIVE</span>' : 'CPU Only';
                })
                .catch(err => {
                    document.getElementById('stats-container').innerHTML = `
                        <div class="col-12">
                            <div class="alert alert-warning border-0 bg-dark text-warning">
                                <strong>Connection Offline:</strong> Ensure the miner is running with API enabled.
                            </div>
                        </div>`;
                });
        }

        setInterval(updateStats, 3000);
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
    try:
        r = requests.get(XMRIG_API_URL, timeout=1.5)
        data = r.json()
        # Add a flag for GPU detection for the UI
        data['has_gpu'] = 'cuda' in data.get('features', []) or (data.get('gpu') and data['gpu'].get('enabled'))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Miner API unreachable"}), 500

if __name__ == '__main__':
    # Listen on all interfaces so phone can access it
    app.run(host='0.0.0.0', port=5000)
