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

CONFIG_FILE = "config_gpu_nicehash.json"

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
        "algo": None,
        "region": "auto"
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_gminer_path():
    if sys.platform == "win32":
        return os.path.join("bin", "gminer", "miner.exe")
    return os.path.join("bin", "gminer", "miner")

class NiceHashMinerApp:
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

        # NiceHash stratum mapping
        # GMiner algos: kawpow, autolykos2
        nh_algo_map = {
            "kawpow": "kawpow",
            "autolykos2": "autolykos"
        }
        nh_algo = nh_algo_map.get(self.algo, "kawpow")
        server = f"{nh_algo}.auto.nicehash.com:443"

        # Command for GMiner
        cmd = [
            gminer_path,
            "--algo", self.algo,
            "--server", server,
            "--ssl", "1",
            "--user", f"{self.config['wallet']}.{self.config['worker']}",
            "--api", "12346"
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

        header_text = Text(" SPINE GPU MINER - NICEHASH ", style="bold white on blue", justify="center")
        layout["header"].update(Panel(header_text))

        layout["body"].split_row(Layout(name="stats", ratio=1), Layout(name="logs", ratio=2))

        uptime = str(datetime.now() - self.start_time).split('.')[0] if self.start_time else "0:00:00"
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("[bold]Status:[/]", "[green]ACTIVE[/]" if self.running else "[red]INACTIVE[/]")
        stats_table.add_row("[bold]Algo:[/]", f"[cyan]{self.algo}[/]")
        stats_table.add_row("[bold]Hashrate:[/]", f"[bold cyan]{self.hashrate}[/]")
        stats_table.add_row("[bold]NiceHash Wallet:[/]", f"[yellow]{self.config['wallet'][:10]}...[/]")
        stats_table.add_row("[bold]Uptime:[/]", uptime)

        layout["stats"].update(Panel(stats_table, title="Statistics"))
        layout["logs"].update(Panel("\n".join(self.logs[-15:]), title="Console"))
        layout["footer"].update(Panel(Text("Ctrl+C to exit", justify="center")))

        return layout

def main():
    config = load_config()

    if not config["wallet"]:
        print("Welcome to Spine GPU Miner (NiceHash Edition)")
        print("Please enter your NiceHash Mining Address (starting with nhwm... or your BTC address):")
        wallet = input("Address: ").strip()
        if not wallet: return
        config["wallet"] = wallet

        print("\nBenchmarking GPUs to find the best algorithm...")
        config["algo"] = gpu_utils.get_best_algo()
        print(f"Best algorithm found: {config['algo']}")

        save_config(config)

    app = NiceHashMinerApp(config)
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
