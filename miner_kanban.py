import os
import sys
import time
import requests
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

# API Endpoints
CPU_API = "http://127.0.0.1:8888/1/summary"
GPU_UNMINEABLE_API = "http://127.0.0.1:12345/stat"
GPU_NICEHASH_API = "http://127.0.0.1:12346/stat"

class KanbanDashboard:
    def __init__(self):
        self.console = Console()
        self.data = {
            "cpu": None,
            "gpu": None,
            "last_update": "Never"
        }

    def fetch_data(self):
        # Fetch CPU data
        try:
            r = requests.get(CPU_API, timeout=0.3)
            self.data["cpu"] = r.json()
        except:
            self.data["cpu"] = None

        # Fetch GPU data
        self.data["gpu"] = None
        for url in [GPU_UNMINEABLE_API, GPU_NICEHASH_API]:
            try:
                r = requests.get(url, timeout=0.3)
                if r.status_code == 200:
                    self.data["gpu"] = r.json()
                    break
            except:
                continue

        self.data["last_update"] = datetime.now().strftime("%H:%M:%S")

    def make_inventory_panel(self):
        table = Table(show_header=False, box=None, padding=(0,1))

        if self.data["cpu"]:
            cpu_info = self.data["cpu"].get("cpu", {})
            table.add_row("[bold cyan]CPU:[/] " + str(cpu_info.get("brand", "Detected")))
            table.add_row("[bold cyan]Cores:[/] " + str(cpu_info.get("cores", "N/A")))
        else:
            table.add_row("[dim]CPU Miner Offline[/]")

        table.add_section()

        if self.data["gpu"]:
            devices = self.data["gpu"].get("devices", [])
            for i, dev in enumerate(devices):
                table.add_row(f"[bold green]GPU {i}:[/] {dev.get('name')}")
                # GMiner uses mem_total or similar
                vram = dev.get('mem_total', 0) // 1024 if 'mem_total' in dev else 'N/A'
                table.add_row(f"  [dim]VRAM: {vram}GB[/]")
        else:
            table.add_row("[dim]GPU Miner Offline[/]")

        return Panel(table, title="[bold white]1. INVENTORY[/]", border_style="blue")

    def make_strategy_panel(self):
        table = Table(show_header=False, box=None, padding=(0,1))

        if self.data["gpu"]:
            gpu = self.data["gpu"]
            algo = gpu.get("algorithm", "N/A")
            table.add_row("[bold magenta]Algo:[/] " + algo)
            table.add_row("[bold magenta]Pool:[/] " + ("NiceHash" if "nicehash" in str(gpu).lower() else "unMineable"))

        if self.data["cpu"]:
            cpu = self.data["cpu"]
            table.add_row("[bold magenta]CPU Algo:[/] " + cpu.get("algo", "RandomX"))

        table.add_section()
        table.add_row("[bold yellow]Mode:[/] Automated Performance")

        return Panel(table, title="[bold white]2. STRATEGY[/]", border_style="magenta")

    def make_execution_panel(self):
        table = Table(show_header=False, box=None, padding=(0,1))

        # Hashrates
        if self.data["gpu"]:
            total_gpu_hr = sum(dev.get("speed", 0) for dev in self.data["gpu"].get("devices", []))
            hr_str = f"{total_gpu_hr/1e6:.2f} MH/s"
            table.add_row("[bold green]GPU Speed:[/] " + hr_str)

        if self.data["cpu"]:
            cpu_hr = self.data["cpu"].get("hashrate", {}).get("total", [0])[0]
            table.add_row("[bold green]CPU Speed:[/] " + f"{cpu_hr:.1f} H/s")

        table.add_section()

        uptime = 0
        if self.data["gpu"]: uptime = max(uptime, self.data["gpu"].get("uptime", 0))
        if self.data["cpu"]: uptime = max(uptime, self.data["cpu"].get("uptime", 0))

        hours = uptime // 3600
        mins = (uptime % 3600) // 60
        table.add_row("[bold yellow]Session:[/] " + f"{hours}h {mins}m")

        return Panel(table, title="[bold white]3. EXECUTION[/]", border_style="green")

    def make_telemetry_panel(self):
        table = Table(show_header=False, box=None, padding=(0,1))

        if self.data["gpu"]:
            for i, dev in enumerate(self.data["gpu"].get("devices", [])):
                temp = dev.get("temp", 0)
                fan = dev.get("fan", 0)
                pwr = dev.get("power", 0)

                temp_style = "red" if temp > 75 else "green"
                table.add_row(f"[bold]GPU {i}:[/] [{temp_style}]{temp}°C[/] | {pwr}W")
                table.add_row(f"  [dim]Fan: {fan}%[/]")
        else:
            table.add_row("[dim]Waiting for data...[/]")

        table.add_section()
        status = "[bold green]HEALTHY[/]"
        if self.data["gpu"]:
            for dev in self.data["gpu"].get("devices", []):
                if dev.get("temp", 0) > 85: status = "[bold red]CRITICAL[/]"

        table.add_row("Health: " + status)

        return Panel(table, title="[bold white]4. TELEMETRY[/]", border_style="yellow")

    def generate_layout(self):
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        header_text = Text(f" SPINE KANBAN DASHBOARD | Updated: {self.data['last_update']} ", style="bold black on yellow", justify="center")
        layout["header"].update(Panel(header_text))

        kanban_layout = Layout()
        kanban_layout.split_row(
            Layout(self.make_inventory_panel(), name="inventory"),
            Layout(self.make_strategy_panel(), name="strategy"),
            Layout(self.make_execution_panel(), name="execution"),
            Layout(self.make_telemetry_panel(), name="telemetry")
        )
        layout["body"].update(kanban_layout)

        footer_text = Text("Unified CPU/GPU Monitor | Performance Optimized | Ctrl+C to exit", justify="center", style="dim italic")
        layout["footer"].update(Panel(footer_text))

        return layout

def main():
    dashboard = KanbanDashboard()
    with Live(dashboard.generate_layout(), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                dashboard.fetch_data()
                live.update(dashboard.generate_layout())
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
