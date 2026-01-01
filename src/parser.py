import json
from .servicenow_api import create_incident
from .db import save_incident, is_processed, mark_processed


def analyze_new_lines(file_path):
    """
    Reads the log file line-by-line and processes only NEW log lines.
    Prevents duplicates and automatically creates incidents in ServiceNow.
    """

    print(f"[INFO] Scanning log file: {file_path}")

    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip blank lines
                if not line:
                    continue

                # Check if line was already processed
                if is_processed(line):
                    continue  # Avoid duplicate incidents

                # Parse JSON safely
                try:
                    log = json.loads(line)
                except Exception as e:
                    print(f"[WARN] Invalid JSON log skipped: {line}")
                    mark_processed(line)
                    continue

                # Extract fields
                level = log.get("level", "").upper()
                msg = log.get("message", "").lower()
                job = log.get("job_id", "UNKNOWN")
                ts = log.get("timestamp", "")

                # Debug
                print(f"[DEBUG] New log detected: {log}")

                severity = None

                if level == "ERROR" :
                    severity = "HIGH"

                elif "failed" in msg or "exception" in msg or "timeout" in msg:
                    severity = "MEDIUM"

                elif level == "WARN":
                    severity = "LOW"

                else:
                    # Nothing to analyze → mark processed and skip
                    mark_processed(line)
                    continue

                # Debug
                print(f"[INFO] Issue detected -> {severity} severity")

                # -----------------------------
                # CREATE SERVICENOW INCIDENT
                # -----------------------------
                short_desc = f"Severity {severity} issue detected in job {job}"
                description = f"Log message: '{msg}' at {ts}"

                snow_id = create_incident(short_desc, description, severity)

                if snow_id:
                    print(f"[INFO] ServiceNow Incident Created: {snow_id}")
                else:
                    print("[ERROR] Failed to create ServiceNow incident")

                # -----------------------------
                # SAVE INCIDENT LOCALLY IN DB
                # -----------------------------
                save_incident(job, severity, msg, ts, snow_id)

                # Mark log as processed
                mark_processed(line)

    except FileNotFoundError:
        print(f"[ERROR] Log file not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in analyzer: {e}")
