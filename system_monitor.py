import csv
import time
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/system_metrics.csv")

FIELDS = [
    "timestamp",
    # CPU
    "cpu_usage_percent",
    "loadavg_1",
    "loadavg_5",
    "loadavg_15",
    "running_processes",
    # Memory
    "mem_total_kb",
    "mem_used_kb",
    "mem_available_kb",
    "mem_percent",
    # Disk
    "disk_total_kb",
    "disk_used_kb",
    "disk_free_kb",
    "disk_percent",
    # Uptime
    "uptime_seconds",
    "idle_seconds",
    # Processes
    "proc_total",
    "proc_running",
    "proc_sleeping_est",
    # Top processes
    "top_cpu_1",
    "top_cpu_2",
    "top_cpu_3",
    "top_mem_1",
    "top_mem_2",
    "top_mem_3",
]

def run_cmd(cmd: str) -> str:
    """Run a shell command and return output (empty string of error)."""
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""
    
def ensure_header():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="raise").writerow(row)
            writer.writeheader()

def get_cpu_usage_percent():
    """
    CPU usage from top:
    CPU usage = 100 - idle%
    """
    out = run_cmd("top -bn1 | grep 'Cpu(s)'")
    try:
        parts = [p.strip()for p in out.split(",")]
        idle_part = next(p for p in parts if "id" in p or p.endswith("id"))
        idle_str = idle_part.replace("id", "").replace("%Cpu(s):", "").strip()
        idle = float(idle_str.split()[0])
        return round(100.0 - idle, 2)
    except Exception:
        return ""
    
def get_loadavg():
        """Load average from /proc/loadavg (1,5,15)."""
        try:
            with open ("/proc/loadavg", "r", encoding="utf-8") as f:
                s = f.read().strip().split()
            return s[0], s[1], s[2]
        except Exception:
            return "","",""
        
def get_running_processes():
    """Count processes in running state using ps."""
    out = run_cmd("ps -eo stat | tail -n +2")
    if not out:
        return ""
    return sum(1 for line in out.splitlines() if line.strip().startswith("R"))

def get_memory():
    """Memory info from /proc/meminfo (KB)."""
    try:
        mem_total = None
        mem_available = None

        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    mem_total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_available = int(line.split()[1])
        if mem_total - mem_available is None:
                return "", "", "", ""
        
        mem_used = mem_total - mem_available
        mem_percent = round((mem_used / mem_total) * 100.0, 2)

        return mem_total, mem_used, mem_available, mem_percent
    
    except Exception as e:
        print("get_memory_error:", e)
        return "", "", "", ""
    
def get_disk():
    """Disk usage for / using df -kP (portable format)."""
    out = run_cmd("df-kP / tail -n 1")
    try: 
        cols = out.split()
        total = int(cols[1])
        used = int (cols[2])
        free = int(cols[3])
        percent = cols[4].replace("%", "")
        return total, used, free, percent
    except Exception:
        return "", "", "", ""
    
def get_uptime_idle():
    """Uptime and idle seconds from /proc/uptime."""
    try:
        with open ("/proc/uptime", "r", encoding="utf-8") as f:
            up, idle = f.read().strip().split()
        return int(float(up)), int(float(idle))
    except Exception:
        return "", ""
    
def get_total_processes():
    """Total processes = number of numeric directories in /proc."""
    try:
        return len ([p for p in Path("/proc").iterdir() if p.is_dir() and p.name.isdigit()])
    except Exception:
        return ""
    
def get_proc_running():
    """procs_running from /proc/stat."""
    try:
        for line in Path ("/proc/stat").read_text(encoding="utf-8").splitlines():
            if line.startswith("procs_running"):
                return int(line.split([1]))
    except Exception:
        pass
    return ""

def top3_cpu_mem():
    top_cpu_lines = run_cmd("ps -eo pid,comm,%cpu -- sort=-%cpu | head -n 4 | tail -n 3").splitlines()
    top_mem_lines = run_cmd ("ps -eo pid,comm,%mem --sort=-%mem | head -n 4 | tail -n 3").splitlines()

    def fmt(lines):
        res = []
        for ln in lines:
            parts= ln.split(None, 2) 
            if len(parts) == 3:
                res.append(f"{parts[0]}:{parts[1]}:{parts[2]}")
        while len(res) < 3:
            res.append("") 
        return res[:3]
    
    return fmt(top_cpu_lines), fmt(top_mem_lines)

def log_once():
    ts = datetime.now().replace(microsecond=0).isoformat()

    cpu_usage = get_cpu_usage_percent()
    la1, la5, la15 = get_loadavg()
    running_ps = get_running_processes()

    mem_total, mem_used, mem_avail, mem_percent = get_memory()
    disk_total, disk_used, disk_free, disk_percent = get_disk()

    uptime_s, idle_s = get_uptime_idle()

    proc_total = get_total_processes()
    proc_running = get_proc_running()

    proc_sleeping_est = ""
    try:
        if proc_total != "" and proc_running != "":
            proc_sleeping_est = max(0, int(proc_total) - int(proc_running))
    except Exception:
        proc_sleeping_est = ""

    top_cpu, top_mem = top3_cpu_mem()

    row = {
        "timestamp": ts,
        "cpu_usage_percent": cpu_usage,
        "loadavg_1": la1,
        "loadavg_5": la5,
        "loadavg_15": la15,
        "running_processes": running_ps,
        "mem_total_kb": mem_total,
        "mem_used_kb": mem_used,
        "mem_available_kb": mem_avail,
        "mem_percent": mem_percent,
        "disk total kb": disk_total,
        "disk_used_kb":disk_used,
        "disk_free_kb": disk_free,
        "disk_percent": disk_percent,
        "uptime_seconds": uptime_s,
        "idle_seconds": idle_s,
        "proc_total": proc_total,
        "proc_running": proc_running,
        "proc_sleeping_est": proc_sleeping_est,
        "top_cpu_1": top_cpu[0],
        "top_cpu_2": top_cpu[1],
        "top_cpu_3": top_cpu[2],
        "top_mem_1": top_mem[0],
        "top_mem_2": top_mem[1],
        "top_mem_3": top_mem[2],
    }

    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore").writerow(row)

    print(f"[{ts}] Logged -> {LOG_FILE}")

def main(interval_seconds=10, samples=30):
    ensure_header()
    for _ in range (samples):
        log_once()
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()


