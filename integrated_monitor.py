"""
AAC6164 Assignment - Integrated Monitoring System
Students: NG CHING ER & NURUL DANIA BINTI FAIROS

This script runs both directory monitoring and system performance monitoring
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add module paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'student_A_module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'student_B_module'))

# Import both modules
import directory_monitor as dir_mon
import system_monitor as sys_mon

def run_directory_monitoring():
    """Run Student A's directory monitoring in a thread"""
    print("[Student A] Starting directory monitoring...")
    try:
        dir_mon.main()
    except Exception as e:
        print(f"[Student A] Error: {e}")

def run_system_monitoring():
    """Run Student B's system monitoring in a thread"""
    print("[Student B] Starting system monitoring...")
    try:
        sys_mon.main()
    except Exception as e:
        print(f"[Student B] Error: {e}")

def main():
    print("="*70)
    print("AAC6164 - Integrated Monitoring System")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Modules:")
    print("  [A] Directory Monitoring (Student A)")
    print("  [B] System Performance Monitoring (Student B)")
    print()
    print("Press Ctrl+C to stop both modules")
    print("="*70)
    print()
    
    # Create threads for both modules
    thread_a = threading.Thread(target=run_directory_monitoring, daemon=True)
    thread_b = threading.Thread(target=run_system_monitoring, daemon=True)
    
    # Start both threads
    thread_a.start()
    thread_b.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("Stopping integrated monitoring system...")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

if __name__ == "__main__":
    main()
