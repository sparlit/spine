import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime

# Try to import rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default config with API enabled for Web Dashboard
    return {
        "wallet": os.environ.get("WALLET", ""),
        "worker": os.environ.get("WORKER", "SpineMiner"), "coin": os.environ.get("COIN", "BTC"),
        "mock": False,
        "api": {"port": 8888, "access-token": None, "worker-id": None},
        "cuda": True,
        "huge-pages": True
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_xmrig_path():
    if sys.platform == "win32":
        return os.path.join("bin", "xmrig.exe")
    return os.path.join("bin", "xmrig")

class MinerApp:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.hashrate = "0 H/s"
        self.logs = []
        self.start_time = None
        self.process = None

    def start_mining(self):
        if self.config.get("mock"):
            self.logs.append("[Info] Running in MOCK mode for testing.")
            self.running = True
            self.start_time = datetime.now()
            threading.Thread(target=self._mock_mining, daemon=True).start()
            return

        xmrig_path = get_xmrig_path()
        if not os.path.exists(xmrig_path):
            self.logs.append(f"[Error] XMRig not found at {xmrig_path}.")
            return

        # Build command with CUDA and API support
        cmd = [
            xmrig_path,
            "-o", "rx.unmineable.com:3333",
            "-u", f"{self.config.get('coin', 'BTC')}:{self.config['wallet']}.{self.config['worker']}#v3v3-9p5n",
            "-p", "x",
            "--donate-level", "1",
            "--http-port", str(self.config['api']['port']),
            "--http-host", "0.0.0.0"
        ]

        if self.config.get("cuda"):
            cmd.append("--cuda")
            self.logs.append("[Info] GPU Mining (CUDA) enabled.")

        try:
            # We use a separate thread to handle the process output
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.running = True
            self.start_time = datetime.now()

            def read_output():
                for line in iter(self.process.stdout.readline, ''):
                    line = line.strip()
                    if line:
                        if "speed" in line and "H/s" in line:
                            try:
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part == "10s/60s/15m":
                                        self.hashrate = parts[i+1] + " H/s"
                            except:
                                pass

                        self.logs.append(line)
                        if len(self.logs) > 100:
                            self.logs.pop(0)
                self.running = False

            threading.Thread(target=read_output, daemon=True).start()
        except Exception as e:
            self.logs.append(f"[Error] Failed to start: {str(e)}")

    def _mock_mining(self):
        import random
        while self.running:
            hr = random.uniform(100, 1000)
            self.hashrate = f"{hr:.2f} H/s"
            self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] speed 10s/60s/15m {hr:.1f} H/s")
            time.sleep(5)

    def stop_mining(self):
        self.running = False
        if self.process:
            self.process.terminate()

    def generate_layout(self):
        layout = Layout()
        layout.split(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

        header_text = Text(" SPINE BITCOIN MINER ENHANCED ", style="bold white on blue", justify="center")
        layout["header"].update(Panel(header_text))

        layout["body"].split_row(Layout(name="stats", ratio=1), Layout(name="logs", ratio=2))

        uptime = str(datetime.now() - self.start_time).split('.')[0] if self.start_time else "0:00:00"
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("[bold]Status:[/]", "[green]ACTIVE[/]" if self.running else "[red]INACTIVE[/]")
        stats_table.add_row("[bold]GPU Mining:[/]", "[cyan]ENABLED[/]" if self.config.get("cuda") else "[grey]DISABLED[/]")
        stats_table.add_row("[bold]Hashrate:[/]", f"[bold cyan]{self.hashrate}[/]")
        stats_table.add_row("[bold]Dashboard:[/]", "[yellow]http://localhost:5002[/]")
        stats_table.add_row("[bold]Uptime:[/]", uptime)

        layout["stats"].update(Panel(stats_table, title="Statistics"))
        layout["logs"].update(Panel("\n".join(self.logs[-15:]), title="Console"))
        layout["footer"].update(Panel(Text("Ctrl+C to exit | Web Dashboard active", justify="center")))

        return layout

def main():
    config = load_config()

    if not config["wallet"]:
        print("========================================")
        print("      SELECT PAYOUT COIN              ")
        print("========================================")
        print("1. Bitcoin (BTC)")
        print("2. Dogecoin (DOGE)")
        print("3. Shiba Inu (SHIB)")
        choice = input("Choice [1]: ").strip() or "1"
        config["coin"] = {"1":"BTC", "2":"DOGE", "3":"SHIB"}.get(choice, "BTC")
        print(f"Payout Coin set to: {config['coin']}")
        print("Welcome! Please enter your Binance BTC Address:")
        wallet = input("Address: ").strip()
        if not wallet: return
        config["wallet"] = wallet
        save_config(config)

    app = MinerApp(config)
    app.start_mining()

    if not HAS_RICH:
        while True: time.sleep(1)

    with Live(app.generate_layout(), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                live.update(app.generate_layout())
                time.sleep(1)
        except KeyboardInterrupt:
            app.stop_mining()

if __name__ == "__main__":
    main()
