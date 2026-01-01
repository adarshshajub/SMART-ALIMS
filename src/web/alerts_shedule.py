from flask_apscheduler import APScheduler
import os
import sqlite3
from src.email_utils import send_email, build_alert_email
from datetime import datetime, timezone

scheduler = APScheduler()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "incidents.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn


def schedule_alert_job(alert):
    job_id = f"alert_{alert['id']}"

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    if not alert["enabled"]:
        return

    if alert["schedule_type"] == "interval":
        scheduler.add_job(
            id=job_id,
            func=process_single_alert,
            trigger="interval",
            minutes=alert["schedule_value"],
            args=[alert["id"]]
        )

    elif alert["schedule_type"] == "hourly":
        scheduler.add_job(
            id=job_id,
            func=process_single_alert,
            trigger="interval",
            hours=alert["schedule_value"],
            args=[alert["id"]]
        )

    elif alert["schedule_type"] == "daily":
        scheduler.add_job(
            id=job_id,
            func=process_single_alert,
            trigger="interval",
            days=alert["schedule_value"],
            args=[alert["id"]]
        )


def process_single_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = cursor.fetchone()

    if not alert or not alert["enabled"]:
        conn.close()
        return

    last_triggered = alert["last_triggered"] or "1970-01-01"

    query = """
        SELECT * FROM incidents
        WHERE log_timestamp > ?
        AND (
            job_id LIKE ?
            OR message LIKE ?
        )
    """
    params = [
        last_triggered,
        f"%{alert['keyword']}%",
        f"%{alert['keyword']}%",
    ]

    if alert["severity"]:
        query += " AND severity = ?"
        params.append(alert["severity"])

    cursor.execute(query, params)
    incidents = cursor.fetchall()

    if incidents:
        email_body = build_alert_email(alert, incidents)

        send_email(
            to_emails=alert["email_to"],
            subject=alert["subject"],
            body=email_body
        )

        cursor.execute("""
            UPDATE alerts
            SET last_triggered = ?
            WHERE id = ?
        """, (datetime.now(timezone.utc).isoformat(), alert_id))

        cursor.execute("""
            INSERT INTO alert_history (alert_id, triggered_at, incident_count)
            VALUES (?, ?, ?)
        """, (
            alert_id,
            datetime.now(timezone.utc).isoformat(),
            len(incidents)
        ))
        conn.commit()

    conn.close()


def load_alert_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts WHERE enabled = 1")
    alerts = cursor.fetchall()

    conn.close()

    for alert in alerts:
        print(f"Alert Trigger:  {alert}")
        schedule_alert_job(alert)