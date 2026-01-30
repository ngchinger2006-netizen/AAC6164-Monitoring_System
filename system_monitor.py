from __future__ import annotations

import csv
import time
from pathlib import Path
from datetime import datetime

import psutil

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "system_metrics.csv"

FIELDNAMES = [
    "timestamp",

    # CPU
    "cpu_percent",
    "load_1",
    "load_5",
    "load_15",
    "running_processes",

    # Memory
    "mem_total_bytes",
    "mem_used_bytes",
    "mem_available_bytes",
    "mem_percent",

    # Disk (root)
    "disk_total_bytes",
    "disk_used_bytes",
    "disk_free_bytes",
    "disk_percent",

    # Uptime
    "uptime_seconds",
    "idle_seconds",

    # Process counts
    "total_processes",
    "sleeping_processes",

    # Top 3 by CPU (name:pid:cpu%)
    "top_cpu_1",
    "top_cpu_2",
    "top_cpu_3",

    # Top 3 by MEM (name:pid:mem%)
    "top_mem_1",
    "top_mem_2",
    "top_mem_3",
]


def ensure_csv_header() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def safe_get_loadavg():
    # Linux/Unix has load average; some systems may not.
    try:
        return psutil.getloadavg()  # (1,5,15)
    except Exception:
        return (None, None, None)


def process_counts():
    total = 0
    running = 0
    sleeping = 0

    for p in psutil.process_iter(attrs=["status"]):
        total += 1
        st = p.info.get("status")
        if st == psutil.STATUS_RUNNING:
            running += 1
        elif st in (psutil.STATUS_SLEEPING, psutil.STATUS_DISK_SLEEP):
            sleeping += 1

    return total, running, sleeping


def top_processes():
    """
    Return:
      top_cpu: 3 strings "name:pid:cpu"
      top_mem: 3 strings "name:pid:mem"
    """
    # Prime CPU sampling (psutil needs a previous call)
    for p in psutil.process_iter(attrs=["pid"]):
        try:
            p.cpu_percent(None)
        except Exception:
            pass

    time.sleep(0.2)  # small measurement window

    procs = []
    for p in psutil.process_iter(attrs=["pid", "name"]):
        try:
            pid = p.info["pid"]
            name = (p.info.get("name") or "unknown").replace(",", " ")
            cpu = p.cpu_percent(None)
            mem = p.memory_percent()
            procs.append((name, pid, cpu, mem))
        except Exception:
            continue

    top_cpu = sorted(procs, key=lambda x: x[2], reverse=True)[:3]
    top_mem = sorted(procs, key=lambda x: x[3], reverse=True)[:3]

    top_cpu_str = [f"{n}:{pid}:{cpu:.2f}" for (n, pid, cpu, mem) in top_cpu]
    top_mem_str = [f"{n}:{pid}:{mem:.2f}" for (n, pid, cpu, mem) in top_mem]

    while len(top_cpu_str) < 3:
        top_cpu_str.append("")
    while len(top_mem_str) < 3:
        top_mem_str.append("")

    return top_cpu_str, top_mem_str


def collect_one_row() -> dict:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    l1, l5, l15 = safe_get_loadavg()

    # Memory
    vm = psutil.virtual_memory()

    # Disk (root partition)
    du = psutil.disk_usage("/")

    # Uptime
    boot = psutil.boot_time()
    uptime_seconds = int(time.time() - boot)

    # Idle time (available on Linux)
    try:
        idle_seconds = int(psutil.cpu_times().idle)
    except Exception:
        idle_seconds = ""

    # Process counts
    total_p, running_p, sleeping_p = process_counts()

    # Top processes
    top_cpu, top_mem = top_processes()

    return {
        "timestamp": ts,

        "cpu_percent": f"{cpu_percent:.2f}",
        "load_1": "" if l1 is None else f"{l1:.2f}",
        "load_5": "" if l5 is None else f"{l5:.2f}",
        "load_15": "" if l15 is None else f"{l15:.2f}",
        "running_processes": str(running_p),

        "mem_total_bytes": str(vm.total),
        "mem_used_bytes": str(vm.used),
        "mem_available_bytes": str(vm.available),
        "mem_percent": f"{vm.percent:.2f}",

        "disk_total_bytes": str(du.total),
        "disk_used_bytes": str(du.used),
        "disk_free_bytes": str(du.free),
        "disk_percent": f"{du.percent:.2f}",

        "uptime_seconds": str(uptime_seconds),
        "idle_seconds": str(idle_seconds),

        "total_processes": str(total_p),
        "sleeping_processes": str(sleeping_p),

        "top_cpu_1": top_cpu[0],
        "top_cpu_2": top_cpu[1],
        "top_cpu_3": top_cpu[2],

        "top_mem_1": top_mem[0],
        "top_mem_2": top_mem[1],
        "top_mem_3": top_mem[2],
    }


def append_row(row: dict) -> None:
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def main():
    ensure_csv_header()
    print(f"[OK] Logging to: {LOG_FILE}")

    interval_seconds = 10  # required periodic sampling

    while True:
        row = collect_one_row()
        append_row(row)

        print(
            f"[{row['timestamp']}] "
            f"CPU={row['cpu_percent']}% "
            f"MEM={row['mem_percent']}% "
            f"DISK={row['disk_percent']}%"
        )

        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()