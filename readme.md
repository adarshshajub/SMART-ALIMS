<h1>Smart Automated Log & Incident Management System</h1>

<p>
<b>Smart Automated Log & Incident Management System</b> is
designed to continuously monitor application logs, detect errors in real time,
create incidents automatically, and trigger configurable email alerts using
scheduled execution.
</p>

<p>
The system follows a <b>decoupled architecture</b>, separating log ingestion and
background processing from the web-based dashboard and alert management layer.
</p>

<hr>

<h2>Key Features</h2>

<ul>
    <li>Continuous log monitoring and analysis</li>
    <li>Rule-based severity classification (HIGH / MEDIUM / LOW)</li>
    <li>Automatic incident creation (ServiceNow integration)</li>
    <li>Centralized incident dashboard</li>
    <li>Advanced search and filtering</li>
    <li>Configurable email alerts with subject & body</li>
    <li>Scheduled alert execution using APScheduler</li>
    <li>Duplicate alert prevention using state tracking</li>
    <li>Alert execution history tracking</li>
</ul>

<hr>

<h2>System Architecture</h2>

<p>The system is composed of two independent components:</p>

<h3>1. Web Application (Flask)</h3>
<ul>
    <li>User authentication and authorization</li>
    <li>Incident dashboard and search</li>
    <li>Alert creation, editing, enable/disable</li>
    <li>Scheduler-based alert triggering</li>
    <li>Email notification handling</li>
</ul>

<h3>2. Background Worker</h3>
<ul>
    <li>Continuous log file monitoring</li>
    <li>Parsing and severity evaluation</li>
    <li>Duplicate log prevention</li>
    <li>Incident persistence to database</li>
    <li>External incident creation (ServiceNow)</li>
</ul>

<hr>

<h2>Database Design</h2>

<h3>Core Tables</h3>

<ul>
    <li><b>incidents</b> – Stores detected incidents</li>
    <li><b>alerts</b> – Stores alert configurations</li>
    <li><b>alert_history</b> – Stores alert execution history</li>
    <li><b>accounts</b> – User authentication</li>
    <li><b>processed_logs</b> – Prevents duplicate log processing</li>
</ul>

<hr>

<h2>Alert Execution Logic</h2>

<p>
Alerts are <b>state-aware</b>. Each alert stores a <code>last_triggered</code> timestamp.
During every scheduled run:
</p>

<ul>
    <li>Only incidents newer than the last trigger are evaluated</li>
    <li>Email is sent only if new incidents are found</li>
    <li>Duplicate alerts are automatically prevented</li>
</ul>

<p>
This behavior matches enterprise monitoring tools such as Splunk and ELK.
</p>

<hr>

<h2>Email Notification</h2>

<p>
Emails are sent using SMTP with configurable:
</p>

<ul>
    <li>Recipient list</li>
    <li>Subject</li>
    <li>Custom body</li>
    <li>Optional auto-inclusion of search criteria and incident summary</li>
</ul>

<hr>

<h2>Scheduler</h2>

<p>
The system uses <b>APScheduler</b> to run alerts at configurable intervals:
</p>

<ul>
    <li>Every N minutes</li>
    <li>Hourly</li>
    <li>Daily</li>
</ul>

<p>
All active alerts are reloaded automatically on application startup.
</p>

<hr>

<h2>How to Run the Project</h2>

<h3>1. Clone the Repository</h3>

<pre>
git clone https://github.com/adarshshajub/SMART-ALIMS.git
cd SMART-ALIMS
</pre>

<h3>2. Create Virtual Environment</h3>

<pre>
python -m venv venv
venv\Scripts\activate
</pre>

<h3>3. Install Dependencies</h3>
<pre>
pip install -r requirements.txt
</pre>

<h3>4. Configure Environment Variables</h3>

Create a .env file in the project root:
<pre>
FLASK_SECRET_KEY=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SNOW_INSTANCE=
SNOW_USER=
SNOW_PASS=
</pre>

Note: To generate a Secret Key execute below code in terminal add the result value in the .env file 
<pre>
python -c 'import secrets; print(secrets.token_hex(16))'
</pre>

<h3>5. Start Background Worker</h3>

<pre>
python -m src.worker.main
</pre>

<h3>6. Start Web Application</h3>

<pre>
python -m src.web.app
</pre>

<hr>

<h2>Security Considerations</h2>

<ul>
    <li>Passwords are securely hashed</li>
    <li>Email credentials stored via environment variables</li>
    <li>Scheduler protected from duplicate execution</li>
    <li>Alert spam prevented using state tracking</li>
</ul>

<hr>

<h2>Conclusion</h2>

<p>
Smart Automated Log & Incident Management System demonstrates a real-world, production-style approach to automated
monitoring and incident orchestration. The project emphasizes scalability,
fault isolation, and extensibility while maintaining a clean and modular
architecture.
</p>


