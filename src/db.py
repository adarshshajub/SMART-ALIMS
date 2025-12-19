import sqlite3
import os
import hashlib

# absolute path → root folder of your project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
