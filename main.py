import time
from src.parser import analyze_new_lines
from src.db import init_db
import os

# Set your log file path (absolute path recommended)
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "sample.json")


def monitor_logs(interval=5):
    """
    Continuously monitor the log file.
    Every 'interval' seconds, read only new log lines.
    """

    print("[SYSTEM] Starting Continuous Log Monitoring...")
    print(f"[SYSTEM] Watching file: {LOG_FILE}")
    print("[SYSTEM] Press CTRL+C to stop.\n")

    while True:
        try:
            analyze_new_lines(LOG_FILE)
            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[SYSTEM] Monitoring stopped by user.")
            break

        except Exception as e:
            print(f"[ERROR] Unexpected error in monitor: {e}")
            time.sleep(interval)  # Avoid crash loop


if __name__ == "__main__":
    # Ensure DB exists before monitoring
    init_db()

    # Start continuous monitoring loop
    monitor_logs(interval=5)   # Check every 5 seconds
