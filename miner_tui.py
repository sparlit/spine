import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime

# Try to import rich, but have a fallback for basic printing
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
    return {"wallet": "", "worker": "SpineMiner", "mock": False}

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
            self.logs.append("[Info] Please run the setup script for your platform.")
            return

        # Optimization flags for RandomX
        cmd = [
            xmrig_path,
            "-o", "rx.unmineable.com:3333",
            "-u", f"BTC:{self.config['wallet']}.{self.config['worker']}#v3v3-9p5n",
            "-p", "x",
            "--donate-level", "1",
            "--cpu-max-threads-hint", "75" # Keep some room for system responsiveness
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
                        # Extract hashrate from XMRig output
                        # Example: [2023-10-27 10:00:00] speed 10s/60s/15m 500.0 490.0 480.0 H/s max 510.0 H/s
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
        """Simulate mining for testing without real hardware usage."""
        import random
        while self.running:
            hr = random.uniform(100, 1000)
            self.hashrate = f"{hr:.2f} H/s"
            self.logs.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] speed 10s/60s/15m {hr:.1f} {hr:.1f} {hr:.1f} H/s")
            if len(self.logs) > 100:
                self.logs.pop(0)
            time.sleep(5)

    def stop_mining(self):
        self.running = False
        if self.process:
            self.process.terminate()

    def generate_layout(self):
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        header_text = Text(" SPINE BITCOIN MINER v1.0 ", style="bold white on blue", justify="center")
        layout["header"].update(Panel(header_text))

        layout["body"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="logs", ratio=2)
        )

        uptime = str(datetime.now() - self.start_time).split('.')[0] if self.start_time else "0:00:00"
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_row("[bold]Status:[/]", "[green]ACTIVE[/]" if self.running else "[red]INACTIVE[/]")
        stats_table.add_row("[bold]Wallet:[/]", f"[yellow]{self.config['wallet'][:8]}...{self.config['wallet'][-8:]}[/]")
        stats_table.add_row("[bold]Worker:[/]", self.config['worker'])
        stats_table.add_row("[bold]Algorithm:[/]", "RandomX (Unmineable)")
        stats_table.add_row("[bold]Hashrate:[/]", f"[bold cyan]{self.hashrate}[/]")
        stats_table.add_row("[bold]Uptime:[/]", uptime)

        layout["stats"].update(Panel(stats_table, title="[bold]Pool Statistics[/]"))

        visible_logs = "\n".join(self.logs[-15:])
        layout["logs"].update(Panel(visible_logs, title="[bold]Console Output[/]"))

        footer_text = Text("Commands: [Ctrl+C] Exit | Mining BTC via Monero algorithm", style="italic", justify="center")
        layout["footer"].update(Panel(footer_text))

        return layout

def main():
    config = load_config()

    if not config["wallet"]:
        print("========================================")
        print("       SPINE BITCOIN MINER SETUP        ")
        print("========================================")
        print("Please enter your Binance BTC Address.")
        print("Format: BTC address (e.g., 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa)")
        wallet = input("\nAddress: ").strip()
        if not wallet:
            print("Error: Address is required.")
            return
        config["wallet"] = wallet
        save_config(config)

    app = MinerApp(config)

    if not HAS_RICH:
        print("\n[!] Warning: 'rich' library not installed. TUI will be limited.")
        print("[!] Install it with: pip install rich")
        print("-" * 40)
        app.start_mining()
        try:
            while True:
                if app.logs:
                    print(app.logs[-1])
                time.sleep(2)
        except KeyboardInterrupt:
            app.stop_mining()
            return

    app.start_mining()

    with Live(app.generate_layout(), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                live.update(app.generate_layout())
                time.sleep(1)
        except KeyboardInterrupt:
            app.stop_mining()

if __name__ == "__main__":
    main()
