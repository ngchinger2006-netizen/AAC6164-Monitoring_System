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
    "mem_used_mb",
    "mem_total_mb",
    "mem_percent",
    "disk_used_gb",
    "disk_total_gb",
    "disk_percent",
    "uptime_seconds",
    "top_cpu_process",
    "top_mem_process",
]


def ensure_header():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode().strip()


def get_cpu_usage():
    output = run_cmd("top -bn1 | grep 'Cpu(s)'")
    idle = float(output.split(",")[3].split()[0])
    return round(100 - idle, 2)


def get_load_avg():
    output = run_cmd("uptime")
    loads = output.split("load average:")[1].split(",")
    return loads[0].strip(), loads[1].strip(), loads[2].strip()


def get_memory():
    output = run_cmd("free -m | grep Mem")
    parts = output.split()
    total = int(parts[1])
    used = int(parts[2])
    percent = round((used / total) * 100, 2)
    return used, total, percent


def get_disk():
    output = run_cmd("df -h / | tail -1")
    parts = output.split()
    total = parts[1]
    used = parts[2]
    percent = parts[4]
    return used, total, percent


def get_uptime():
    output = run_cmd("cat /proc/uptime")
    seconds = int(float(output.split()[0]))
    return seconds


def top_process_cpu():
    output = run_cmd("ps -eo pid,comm,%cpu --sort=-%cpu | head -2 | tail -1")
    return output


def top_process_mem():
    output = run_cmd("ps -eo pid,comm,%mem --sort=-%mem | head -2 | tail -1")
    return output


def collect_sample():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cpu = get_cpu_usage()
    l1, l5, l15 = get_load_avg()
    mem_used, mem_total, mem_percent = get_memory()
    disk_used, disk_total, disk_percent = get_disk()
    uptime_sec = get_uptime()

    top_cpu = top_process_cpu()
    top_mem = top_process_mem()

    return {
        "timestamp": ts,
        "cpu_percent": cpu,
        "load_1": l1,
        "load_5": l5,
        "load_15": l15,
        "mem_used_mb": mem_used,
        "mem_total_mb": mem_total,
        "mem_percent": mem_percent,
        "disk_used_gb": disk_used,
        "disk_total_gb": disk_total,
        "disk_percent": disk_percent,
        "uptime_seconds": uptime_sec,
        "top_cpu_process": top_cpu,
        "top_mem_process": top_mem,
    }


def main():
    ensure_header()
    print("[OK] Logging system metrics every 10 seconds...")

    while True:
        row = collect_sample()

        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)

        print(f"[{row['timestamp']}] CPU={row['cpu_percent']}% MEM={row['mem_percent']}% DISK={row['disk_percent']}")

        time.sleep(10)


if __name__ == "__main__":
    main()
