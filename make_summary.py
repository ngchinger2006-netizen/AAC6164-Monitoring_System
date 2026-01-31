import csv
from statistics import mean
from pathlib import Path

LOG_FILE = Path("logs/system_metrics.csv")
REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "summary_report.txt"


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


def main():
    if not LOG_FILE.exists():
        print("[ERROR] logs/system_metrics.csv not found. Run system_monitor.py first.")
        return

    with LOG_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("[ERROR] No data rows yet. Run system_monitor.py longer.")
        return

    cpu_vals = [to_float(r.get("cpu_percent")) for r in rows]
    mem_vals = [to_float(r.get("mem_percent")) for r in rows]
    disk_vals = [to_float(r.get("disk_percent")) for r in rows]

    cpu_vals = [x for x in cpu_vals if x is not None]
    mem_vals = [x for x in mem_vals if x is not None]
    disk_vals = [x for x in disk_vals if x is not None]

    latest = rows[-1]

    avg_cpu = round(mean(cpu_vals), 2) if cpu_vals else "N/A"
    max_cpu = round(max(cpu_vals), 2) if cpu_vals else "N/A"
    spikes_80 = sum(1 for x in cpu_vals if x >= 80) if cpu_vals else 0

    avg_mem = round(mean(mem_vals), 2) if mem_vals else "N/A"
    max_mem = round(max(mem_vals), 2) if mem_vals else "N/A"

    latest_disk = latest.get("disk_percent") or "N/A"
    max_disk = round(max(disk_vals), 2) if disk_vals else "N/A"

    latest_uptime = latest.get("uptime_seconds") or "N/A"

    report = []
    report.append("SYSTEM PERFORMANCE SUMMARY REPORT")
    report.append("=" * 50)
    report.append(f"Log source: {LOG_FILE}")
    report.append(f"Total samples: {len(rows)}\n")

    report.append("CPU SUMMARY")
    report.append("-" * 30)
    report.append(f"Average CPU (%): {avg_cpu}")
    report.append(f"Max CPU (%): {max_cpu}")
    report.append(f"CPU spikes >= 80%: {spikes_80}\n")

    report.append("MEMORY SUMMARY")
    report.append("-" * 30)
    report.append(f"Average Memory (%): {avg_mem}")
    report.append(f"Max Memory (%): {max_mem}\n")

    report.append("DISK SUMMARY")
    report.append("-" * 30)
    report.append(f"Latest Disk (%): {latest_disk}")
    report.append(f"Max Disk (%): {max_disk}\n")

    report.append("UPTIME")
    report.append("-" * 30)
    report.append(f"Latest uptime (s): {latest_uptime}\n")

    report.append("TOP 3 PROCESSES BY CPU (latest)")
    report.append("-" * 30)
    report.append(f"1) {latest.get('top_cpu_1', '')}")
    report.append(f"2) {latest.get('top_cpu_2', '')}")
    report.append(f"3) {latest.get('top_cpu_3', '')}\n")

    report.append("TOP 3 PROCESSES BY MEMORY (latest)")
    report.append("-" * 30)
    report.append(f"1) {latest.get('top_mem_1', '')}")
    report.append(f"2) {latest.get('top_mem_2', '')}")
    report.append(f"3) {latest.get('top_mem_3', '')}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    text = "\n".join(report) + "\n"
    REPORT_FILE.write_text(text, encoding="utf-8")

    print(text)
    print(f"[OK] Saved report to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
