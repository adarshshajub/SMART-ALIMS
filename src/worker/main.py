import time
from .parser import analyze_new_lines
from src.db import init_db
import os
from dotenv import load_dotenv 

load_dotenv()

# Set your log file path (absolute path recommended)
LOG_FILENAME = os.getenv('LOG_FILENAME')
LOG_DIR = os.getenv('LOG_DIR')
LOG_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(LOG_ROOT_DIR, LOG_DIR, LOG_FILENAME)


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
