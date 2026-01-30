import csv
import time
import subprocess
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "system_metrics.csv"

FIELDNAMES = [
    "timestamp",
    "cpu_percent",
    "load_1",
    "load_5",
    "load_15",
    "running_processes",
    "mem_used_mb",
    "mem_total_mb",
    "mem_percent",
    "disk_used",
    "disk_total",
    "disk_percent",
    "uptime_seconds",
    "top_cpu_1",
    "top_cpu_2",
    "top_cpu_3",
    "top_mem_1",
    "top_mem_2",
    "top_mem_3",
]


def run_cmd(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def ensure_header():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES)


def get_cpu_percent() -> float:
    out = run_cmd("top -bn1 | grep 'Cpu(s)'")
    # Example: Cpu(s):  3.0 us,  1.0 sy,  0.0 ni, 95.5 id, ...
    parts = out.split(",")
    idle_part = None
    for p in parts:
        if " id" in p:
            idle_part = p
            break
    if idle_part is None:
        return 0.0
    idle = float(idle_part.strip().split()[0])
    return round(100.0 - idle, 2)


def get_loadavg():
    out = run_cmd("cat /proc/loadavg")
    p = out.split()
    return p[0], p[1], p[2]


def get_running_processes() -> int:
    out = run_cmd("ps -eo stat | tail -n +2")
    return sum(1 for s in out.splitlines() if s.startswith("R"))


def get_memory():
    out = run_cmd("free -m | grep Mem:")
    p = out.split()
    total = int(p[1])
    used = int(p[2])
    percent = round((used / total) * 100.0, 2) if total else 0.0
    return used, total, percent


def get_disk():
    out = run_cmd("df -h / | tail -1")
    p = out.split()
    total = p[1]
    used = p[2]
    percent = p[4].replace("%", "")  # store numeric percent only
    return used, total, percent


def get_uptime_seconds() -> int:
    out = run_cmd("cat /proc/uptime")
    return int(float(out.split()[0]))


def top3_cpu():
    out = run_cmd("ps -eo comm,pid,%cpu --sort=-%cpu | head -4 | tail -3")
    lines = [ln.strip().replace(",", " ") for ln in out.splitlines()]
    while len(lines) < 3:
        lines.append("")
    return lines[:3]


def top3_mem():
    out = run_cmd("ps -eo comm,pid,%mem --sort=-%mem | head -4 | tail -3")
    lines = [ln.strip().replace(",", " ") for ln in out.splitlines()]
    while len(lines) < 3:
        lines.append("")
    return lines[:3]


def collect_row():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cpu = get_cpu_percent()
    l1, l5, l15 = get_loadavg()
    running = get_running_processes()

    mem_used, mem_total, mem_percent = get_memory()
    disk_used, disk_total, disk_percent = get_disk()
    uptime = get_uptime_seconds()

    c1, c2, c3 = top3_cpu()
    m1, m2, m3 = top3_mem()

    return {
        "timestamp": ts,
        "cpu_percent": cpu,
        "load_1": l1,
        "load_5": l5,
        "load_15": l15,
        "running_processes": running,
        "mem_used_mb": mem_used,
        "mem_total_mb": mem_total,
        "mem_percent": mem_percent,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "disk_percent": disk_percent,
        "uptime_seconds": uptime,
        "top_cpu_1": c1,
        "top_cpu_2": c2,
        "top_cpu_3": c3,
        "top_mem_1": m1,
        "top_mem_2": m2,
        "top_mem_3": m3,
    }


def append_row(row: dict):
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def main():
    ensure_header()
    print(f"[OK] Logging to {LOG_FILE}")
    print("[OK] Sampling every 10 seconds (Ctrl+C to stop)\n")

    while True:
        row = collect_row()
        append_row(row)
        print(
            f"[{row['timestamp']}] CPU={row['cpu_percent']}% "
            f"MEM={row['mem_percent']}% DISK={row['disk_percent']}%"
        )
        time.sleep(10)


if __name__ == "__main__":
    main()
