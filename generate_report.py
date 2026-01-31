import csv
from datetime import datetime
from pathlib import Path

def generate_report():
    report_file = Path("reports/integrated_report.txt").resolve()
    report_file.parent.mkdir(exist_ok=True)

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("AAC6164 Integrated Monitoring Report\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # --- Student A: Directory Monitoring ---
            f.write("="*70 + "\n")
            f.write("DIRECTORY MONITORING SUMMARY (Student A)\n")
            f.write("="*70 + "\n\n")

            dir_log = Path("/home/ngchinger/logs/directory_changes.log")
            if dir_log.exists():
                content = dir_log.read_text(encoding='utf-8')
                created = content.count("[FILE CREATED]")
                modified = content.count("[FILE MODIFIED]")
                deleted = content.count("[FILE DELETED]")

                f.write(f"Total file creations detected: {created}\n")
                f.write(f"Total file modifications detected: {modified}\n")
                f.write(f"Total file deletions detected: {deleted}\n\n")

                f.write("Recent events (Last 50 lines):\n")
                f.write("-" * 70 + "\n")
                lines = content.strip().split('\n')
                f.write('\n'.join(lines[-50:]))
            else:
                f.write("Log file not found at: logs/directory_changes.log\n")

            f.write("\n\n")

            # --- Student B: System Performance ---
            f.write("="*70 + "\n")
            f.write("SYSTEM PERFORMANCE SUMMARY (Student B)\n")
            f.write("="*70 + "\n\n")

            csv_file = Path("student_B_module/logs/system_metrics.csv")
            if csv_file.exists():
                with open(csv_file, 'r', encoding='utf-8') as csvf:
                    reader = csv.DictReader(csvf)
                    rows = list(reader)

                    if rows:
                        cpu_vals = [float(r['cpu_percent']) for r in rows]
                        mem_vals = [float(r['mem_percent']) for r in rows]
                        disk_vals = [float(r['disk_percent']) for r in rows]

                        count = len(rows)
                        f.write(f"Total measurements: {count}\n")
                        f.write(f"Average CPU usage: {sum(cpu_vals)/count:.2f}%\n")
                        f.write(f"Average Memory usage: {sum(mem_vals)/count:.2f}%\n")
                        f.write(f"Average Disk usage: {sum(disk_vals)/count:.2f}%\n\n")
                        f.write(f"Peak CPU usage: {max(cpu_vals):.2f}%\n")
                        f.write(f"Peak Memory usage: {max(mem_vals):.2f}%\n\n")

                        f.write("Recent measurements (Last 10):\n")
                        f.write("-" * 70 + "\n")
                        for row in rows[-10:]:
                            f.write(f"{row['timestamp']}: CPU={row['cpu_percent']}% "
                                   f"MEM={row['mem_percent']}% DISK={row['disk_percent']}%\n")
            else:
                f.write("CSV file not found at: student_B_module/logs/system_metrics.csv\n")

            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")

        print(f"Report successfully generated at: {report_file}")
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    generate_report()
