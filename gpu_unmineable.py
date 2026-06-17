import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime
import gpu_utils

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

CONFIG_FILE = "config_gpu_unmineable.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "wallet": "",
        "worker": "SpineGPU",
        "coin": "BTC",
        "algo": None
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_gminer_path():
    if sys.platform == "win32":
        return os.path.join("bin", "gminer", "miner.exe")
    return os.path.join("bin", "gminer", "miner")

class GPUMinerApp:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.hashrate = "0 MH/s"
        self.logs = []
        self.start_time = None
        self.process = None
        self.algo = config.get("algo") or "kawpow"

    def start_mining(self):
        gminer_path = get_gminer_path()
        if not os.path.exists(gminer_path):
            self.logs.append(f"[Error] GMiner not found at {gminer_path}.")
            return

        # unMineable stratum mapping
        stratum_map = {
            "kawpow": "kp.unmineable.com:3333",
            "autolykos2": "autolykos.unmineable.com:3333",
            "nexpow": "nex.unmineable.com:3333"
        }
        server = stratum_map.get(self.algo, "kp.unmineable.com:3333")

        # Command for GMiner
        cmd = [
            gminer_path,
            "--algo", self.algo,
            "--server", server,
            "--user", f"{self.config['coin']}:{self.config['wallet']}.{self.config['worker']}#v3v3-9p5n",
            "--api", "12345"
        ]

        try:
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
                        # Parse GMiner speed
                        if "Speed:" in line:
                            parts = line.split("Speed:")
                            if len(parts) > 1:
                                self.hashrate = parts[1].split()[0] + " " + parts[1].split()[1]

                        self.logs.append(line)
                        if len(self.logs) > 100:
                            self.logs.pop(0)
                self.running = False

            threading.Thread(target=read_output, daemon=True).start()
        except Exception as e:
            self.logs.append(f"[Error] Failed to start: {str(e)}")

    def stop_mining(self):
        self.running = False
        if self.process:
            self.process.terminate()

    def generate_layout(self):
        layout = Layout()
        layout.split(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

        header_text = Text(" SPINE GPU MINER - UNMINEABLE ", style="bold white on orange3", justify="center")
        layout["header"].update(Panel(header_text))

        layout["body"].split_row(Layout(name="stats", ratio=1), Layout(name="logs", ratio=2))

        uptime = str(datetime.now() - self.start_time).split('.')[0] if self.start_time else "0:00:00"
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("[bold]Status:[/]", "[green]ACTIVE[/]" if self.running else "[red]INACTIVE[/]")
        stats_table.add_row("[bold]Algo:[/]", f"[cyan]{self.algo}[/]")
        stats_table.add_row("[bold]Hashrate:[/]", f"[bold cyan]{self.hashrate}[/]")
        stats_table.add_row("[bold]Coin:[/]", f"[yellow]{self.config['coin']}[/]")
        stats_table.add_row("[bold]Dashboard:[/]", "[yellow]http://localhost:5001[/]")
        stats_table.add_row("[bold]Uptime:[/]", uptime)

        layout["stats"].update(Panel(stats_table, title="Statistics"))
        layout["logs"].update(Panel("\n".join(self.logs[-15:]), title="Console"))
        layout["footer"].update(Panel(Text("Ctrl+C to exit | Web Dashboard active", justify="center")))

        return layout

def main():
    config = load_config()

    if not config["wallet"]:
        print("Welcome to Spine GPU Miner (unMineable Edition)")
        wallet = input("Enter your Payout Address (BTC/DOGE/SHIB): ").strip()
        if not wallet: return
        config["wallet"] = wallet

        print("\nSelect Payout Coin:")
        print("1. BTC  2. DOGE  3. SHIB")
        c = input("Choice [1]: ").strip() or "1"
        config["coin"] = {"1":"BTC", "2":"DOGE", "3":"SHIB"}.get(c, "BTC")

        print("\nBenchmarking GPUs to find the best algorithm...")
        config["algo"] = gpu_utils.get_best_algo()
        print(f"Best algorithm found: {config['algo']}")

        save_config(config)

    app = GPUMinerApp(config)
    app.start_mining()

    if not HAS_RICH:
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            app.stop_mining()
            return

    with Live(app.generate_layout(), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                live.update(app.generate_layout())
                time.sleep(1)
        except KeyboardInterrupt:
            app.stop_mining()

if __name__ == "__main__":
    main()
