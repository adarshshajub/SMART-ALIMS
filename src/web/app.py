from flask import Flask, render_template, request, redirect, url_for, session 
import sqlite3
import os
import re
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user, login_required
from dotenv import load_dotenv
from .alerts_shedule import schedule_alert_job, load_alert_jobs, scheduler

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app) 
login_manager.login_view = 'login'

load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY') # Use a default for local testing

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "incidents.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

# --- Flask-Login User Setup ---

# 1. Define a User Class that inherits from UserMixin
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        # Flask-Login expects the ID to be a string
        return str(self.id)

# 2. Define the user_loader callback
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    # Query the database for the user by ID
    c.execute('SELECT id, username FROM accounts WHERE id = ?', (user_id,))
    account = c.fetchone()
    conn.close()
    
    if account:
        return User(id=account[0], username=account[1])
    return None

# --- Application Routes ---

@app.route("/")
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Incident KPIs ---
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'HIGH'")
    high_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'MEDIUM'")
    medium_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'LOW'")
    low_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents")
    total_incidents = cursor.fetchone()[0]

    # --- Alerts KPIs ---
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE enabled = 1")
    active_alerts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE enabled = 0")
    disabled_alerts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alert_history")
    triggered_alerts = cursor.fetchone()[0]

    # --- Recent Incidents ---
    cursor.execute("""
        SELECT * FROM incidents
        ORDER BY log_timestamp DESC
        LIMIT 10
    """)
    recent_incidents = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        total_incidents=total_incidents,
        active_alerts=active_alerts,
        disabled_alerts=disabled_alerts,
        triggered_alerts=triggered_alerts,
        recent_incidents=recent_incidents,
        username=current_user.username
    )

#  Login Page 
@app.route('/login', methods=['GET','POST'])
def login():
    msg = None
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, username FROM accounts WHERE username = ? AND password = ?',(username, password))
        account = c.fetchone()
        conn.close()

        if account:
            user_id = account[0]
            user_obj = User(id=user_id, username=account[1])
            login_user(user_obj)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            msg = 'Incorrect username/password!'
            
    return render_template('login.html', msg=msg)

# Logout page 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# New user register page 
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        account = c.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            c.execute('INSERT INTO accounts VALUES (NULL, ?, ?, ?)', (username, password, email))
            conn.commit()
            msg = 'You have successfully registered! You can now log in.'
        
        conn.close()
        
    return render_template('register.html', msg=msg)

# Search page 
@app.route("/search/", methods=["GET", "POST"])
@login_required
def search():
    conn = get_db_connection()
    cursor = conn.cursor()

    keyword = ""
    severity = ""

    base_query = "SELECT * FROM incidents"
    conditions = []
    params = []

    # 🔹 ALWAYS load default data (GET or POST)
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        severity = request.form.get("severity", "").strip()

        if keyword:
            conditions.append("""
                (job_id LIKE ?
                OR message LIKE ?
                OR snow_incident LIKE ?)
            """)
            params.extend([f"%{keyword}%"] * 3)

        if severity:
            conditions.append("severity = ?")
            params.append(severity)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY log_timestamp DESC"

    cursor.execute(base_query, params)
    results = cursor.fetchall()
    conn.close()

    return render_template(
        "search.html",
        results=results,
        keyword=keyword,
        severity=severity
    )

# Alerts page 
@app.route("/alerts/")
@login_required
def alerts():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
    alerts = cursor.fetchall()

    conn.close()
    return render_template("alerts.html", alerts=alerts)

# New Alert create page 
@app.route("/alerts/create", methods=["GET", "POST"])
@login_required
def create_alert():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO alerts
            (keyword, severity, email_to, subject, body,
            include_search, schedule_type, schedule_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["keyword"],
            request.form.get("severity"),
            request.form["email_to"],
            request.form["subject"],
            request.form.get("body"),
            1 if request.form.get("include_search") else 0,
            request.form.get("schedule_type"),
            int(request.form.get("schedule_value", 5))
        ))

        conn.commit()

        cursor.execute("SELECT * FROM alerts WHERE id = last_insert_rowid()")
        alert = cursor.fetchone()
        schedule_alert_job(alert)
        conn.close()
        return redirect(url_for("alerts"))

    return render_template(
        "alert_form.html",
        keyword=request.args.get("keyword", ""),
        severity=request.args.get("severity", ""),
        alert=None
    )

# Alert Disable or Enable 
@app.route("/alerts/toggle/<int:alert_id>")
@login_required
def toggle_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE alerts
        SET enabled = CASE WHEN enabled = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (alert_id,))

    conn.commit()

    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = cursor.fetchone()
    schedule_alert_job(alert)
    conn.close()

    return redirect(url_for("alerts"))

# Edit alert page 
@app.route("/alerts/edit/<int:alert_id>", methods=["GET", "POST"])
@login_required
def edit_alert(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            UPDATE alerts SET
                keyword = ?,
                severity = ?,
                email_to = ?,
                subject = ?,
                body = ?,
                include_search = ?,
                schedule_type = ?,
                schedule_value = ?
            WHERE id = ?
        """, (
            request.form["keyword"],
            request.form.get("severity"),
            request.form["email_to"],
            request.form["subject"],
            request.form.get("body"),
            1 if request.form.get("include_search") else 0,
            request.form.get("schedule_type"),
            int(request.form.get("schedule_value", 5)),
            alert_id
        ))

        conn.commit()
        cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        alert = cursor.fetchone()
        schedule_alert_job(alert)
        conn.close()
        return redirect(url_for("alerts"))

    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = cursor.fetchone()
    conn.close()

    return render_template("alert_form.html", alert=alert)


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    load_alert_jobs()

    app.run(
        debug=False
    )