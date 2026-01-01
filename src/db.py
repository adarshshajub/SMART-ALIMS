import sqlite3
import os
import hashlib

# absolute path → root folder of your project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "incidents.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            severity TEXT,
            message TEXT,
            log_timestamp TEXT,
            snow_incident TEXT
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS processed_logs (
            log_hash TEXT PRIMARY KEY
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER  PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            severity TEXT,
            email_to TEXT NOT NULL,
            subject TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            body TEXT,
            include_search INTEGER DEFAULT 1,
            last_triggered TEXT,
            schedule_type TEXT DEFAULT 'interval',
            schedule_value INTEGER DEFAULT 5
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER,
            triggered_at TEXT,
            incident_count INTEGER
        );
    """)

    conn.commit()
    conn.close()

def fetch_incidents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM incidents")
    data = c.fetchall()
    conn.close()
    return data

def save_incident(job_id, severity, message, timestamp, snow_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO incidents (job_id, severity, message, log_timestamp, snow_incident)
        VALUES (?, ?, ?, ?, ?)
    """, (job_id, severity, message, timestamp, snow_id))
    conn.commit()
    conn.close()

def hash_line(line):
    return hashlib.sha256(line.encode()).hexdigest()

def is_processed(line):
    h = hash_line(line)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed_logs WHERE log_hash=?", (h,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_processed(line):
    h = hash_line(line)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO processed_logs (log_hash) VALUES (?)", (h,))
    conn.commit()
    conn.close()
