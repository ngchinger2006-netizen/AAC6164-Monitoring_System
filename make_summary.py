import csv
from statistics import mean
from pathlib import Path

LOG_FILE = Path("logs/system_metrics.csv")
REPORT_FILE = Path("reports/summary_report.txt")

# Put possible column names here (the script will pick the first one it finds)
CPU_CANDIDATES = ["cpu_percent", "cpu", "cpu_usage", "cpu(%)", "cpuPercentage"]
MEM_CANDIDATES = ["mem_percent", "memory_percent", "mem", "mem_usage", "memory(%)"]
DISK_CANDIDATES = ["disk_percent", "disk", "disk_usage", "disk(%)"]


def to_float(x):
    try:
        if x is None:
            return None
        s = str(x).strip().replace("%", "")
        if s == "":
            return None
        return float(s)
    except Exception:
        return None


def pick_column(fieldnames, candidates):
    for c in candidates:
        if c in fieldnames:
            return c
    return None


def main():
    if not LOG_FILE.exists():
        print("[ERROR] logs/system_metrics.csv not found. Run system_monitor.py first.")
        return

    with LOG_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []

    if not rows:
        print("[ERROR] CSV exists but has no rows yet.")
        return

    # Pick columns based on actual header
    cpu_col = pick_column(fields, CPU_CANDIDATES)
    mem_col = pick_column(fields, MEM_CANDIDATES)
    disk_col = pick_column(fields, DISK_CANDIDATES)

    print("[DEBUG] CSV header:", fields)
    print("[DEBUG] Using columns:", {"cpu": cpu_col, "mem": mem_col, "disk": disk_col})

    if cpu_col is None:
        print("[ERROR] No CPU column matched. Your CSV header does not match expected names.")
        return

    cpu_vals = [to_float(r.get(cpu_col)) for r in rows]
    cpu_vals = [x for x in cpu_vals if x is not None]

    mem_vals = []
    if mem_col:
        mem_vals = [to_float(r.get(mem_col)) for r in rows]
        mem_vals = [x for x in mem_vals if x is not None]

    disk_vals = []
    if disk_col:
        disk_vals = [to_float(r.get(disk_col)) for r in rows]
        disk_vals = [x for x in disk_vals if x is not None]

    latest = rows[-1]

    report_lines = []
    report_lines.append("SYSTEM PERFORMANCE SUMMARY REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Log source: {LOG_FILE}")
    report_lines.append(f"Total samples: {len(rows)}")
    report_lines.append("")

    report_lines.append("CPU SUMMARY")
    report_lines.append("-" * 30)
    report_lines.append(f"CPU column: {cpu_col}")
    report_lines.append(f"Average CPU (%): {round(mean(cpu_vals), 2) if cpu_vals else 'N/A'}")
    report_lines.append(f"Max CPU (%): {round(max(cpu_vals), 2) if cpu_vals else 'N/A'}")
    report_lines.append(f"CPU spikes >= 80%: {sum(1 for x in cpu_vals if x >= 80) if cpu_vals else 0}")
    report_lines.append("")

    report_lines.append("MEMORY SUMMARY")
    report_lines.append("-" * 30)
    if mem_col and mem_vals:
        report_lines.append(f"Memory column: {mem_col}")
        report_lines.append(f"Average Memory (%): {round(mean(mem_vals), 2)}")
        report_lines.append(f"Max Memory (%): {round(max(mem_vals), 2)}")
    else:
        report_lines.append("Memory: N/A (no memory column detected)")
    report_lines.append("")

    report_lines.append("DISK SUMMARY")
    report_lines.append("-" * 30)
    if disk_col and disk_vals:
        report_lines.append(f"Disk column: {disk_col}")
        report_lines.append(f"Latest Disk: {latest.get(disk_col, 'N/A')}")
        report_lines.append(f"Max Disk (%): {round(max(disk_vals), 2)}")
    else:
        report_lines.append("Disk: N/A (no disk column detected)")
    report_lines.append("")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("\n".join(report_lines))
    print(f"\n[OK] Saved report to: {REPORT_FILE}")


if __name__ == "__main__":
    main()