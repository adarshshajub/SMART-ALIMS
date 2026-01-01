
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_emails, subject, body):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)

    msg = MIMEMultipart()
    msg["From"] = smtp_from
    msg["To"] = to_emails
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def build_alert_email(alert, incidents):
    body = alert["body"] or ""

    if alert["include_search"]:
        body += "\n\n--- Alert Details ---\n"
        body += f"Keyword: {alert['keyword']}\n"
        body += f"Severity: {alert['severity'] or 'ALL'}\n"
        body += f"Matched Incidents: {len(incidents)}\n\n"

        for inc in incidents[:5]:  # limit to avoid huge emails
            body += (
                f"- [{inc['severity']}] "
                f"{inc['job_id']} | {inc['message']} | "
                f"{inc['log_timestamp']}\n"
            )

    return body