import csv
from pathlib import Path
from statistics import mean

LOG_FILE = Path("logs/system_metrics.csv")
REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "system_summary.txt"

def pick_field(rows,candidates):
    """Pick the first field name that exists in the CSV header."""
    for c in candidates:
        if rows and c in rows[0]:
            return c
        return None
    
def get_vals(rows, field):
    """Extract numeric values safely from a column"""
    if not field:
        return[]
    
    vals = []
    for r in rows:
        v = r.get(field, "")

        if isinstance(v, str):
            v = v.strip().replace("%", "")

        try:
            vals.append(float(v))
        except Exception:
            continue

    return vals

def main():
    if not LOG_FILE.exists():
        print("ERROR: logs/system_metrics.csv not found.")
        print("Run monitoring script first.")
    
    with LOG_FILE.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("ERROR: CSV has no data.")
        return
    
    cpu_field = pick_field(rows, ["cpu_usage_percent", "cpu_percent"])
    mem_field = pick_field(rows, ["mem_percent", "mem_percentage", "memory_percent"])
    disk_field = pick_field(rows,["disk_percent"])
    
    cpu_vals = get_vals(rows, cpu_field)
    mem_vals = get_vals(rows, mem_field)
    disk_vals = get_vals(rows, disk_field)

    spikes = []
    if cpu_field:
        for r in rows:
            try:
                val = float(r[cpu_field])
                if val >= 80:
                    spikes.append((r["timestamp"], val))
            except:
                pass

    first_ts = rows[0].get("timestamp", rows[0].get("time", "N/A"))
    last_ts = rows[-1].get("timestamp", rows[-1].get("time", "N/A"))
    last = rows[-1]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open("w", encoding="utf-8") as out:
        out.write("SYSTEM PERFORMANCE SUMMARY REPORT\n")
        out.write("============================================\n\n")
        out.write(f"Log source: {LOG_FILE}\n")
        out.write(f"Time range: {first_ts} -> {last_ts}\n")
        out.write (f"Total samples: {len(rows)}\n\n")

        out.write("CPU SUMMARY\n")
        out.write("-----------\n")
        out.write(f"Average CPU (%): {max(cpu_vals):.2f}\n" if cpu_vals else "Average CPU (%): N/A\n")
        out.write(f"Max CPU (%): {max(cpu_vals):.2f}\n" if cpu_vals else "Max CPU(%): N/A\n")
        out.write(f"CPU spikes >= 80%: {len(spikes)}\n\n")

        out.write("MEMORY SUMMARY\n")
        out.write("-----------\n")
        out.write(f"Average Memory (%): {mean(mem_vals):.2f}\n" if mem_vals else "Average Memory (%): N/A\n")
        out.write(f"Max Memory (%): {max(mem_vals):.2f}\n" if mem_vals else "Max Memory(%): N/A\n")
        
        out.write("DISK SUMMARY\n")
        out.write("-----------\n")
        out.write(f"Latest Disk (%): {last.get('disk_field', 'N/A')}\n")
        out.write(f"Max Disk (%): {max(disk_vals):.2f}\n\n" if disk_vals else "Max Memory (%): N/A\n\n")
        
        out.write("UPTIME\n")
        out.write("------\n")
        out.write(f"Latest uptime (s): {last.get('uptime_seconds', 'N/A')}\n")
        out.write(f"Latest idle (s): {last.get('idle_seconds', 'N/A')}\n")

        out.write("PROCESS COUNTS (latest sample)\n")
        out.write("-----------------------------\n")
        out.write(f"Total processes: {last.get('proc_total', 'N/A')}\n")
        out.write(f"Running: {last.get('proc_running', 'N/A')}\n")
        out.write(f"Sleeping (estimated): {last.get('proc_sleeping_est', 'N/A')}\n\n")

        out.write("TOP 3 PROCESSES BY CPU (latest))\n")
        out.write("-----------------------------\n")
        out.write(f"1) {last.get('top_cpu_1', '')}\n")
        out.write(f"2) {last.get('top_cpu_2', '')}\n")
        out.write(f"3) {last.get('top_cpu_3', '')}\n\n")

        out.write("TOP 3 PROCESSES BY MEMORY (latest))\n")
        out.write("-----------------------------\n")
        out.write(f"1) {last.get('top_mem_1', '')}\n")
        out.write(f"2) {last.get('top_mem_2', '')}\n")
        out.write(f"3) {last.get('top_mem_3', '')}\n\n")

        if spikes:
            out.write("NOTABLE EVENTS\n")
            out.write("--------------\n")
            out.write("CPU spikes >= 80%:\n")
            for ts, val in spikes[:10]:
                out.write(f"-{ts} : {val:.2f}%\n")

    print(f"Summary written to: {REPORT_FILE}")

if __name__ == "__main__":
    main()