import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()  # ← add this

def send_flood_alert(alerts: list, summary: dict):
    """
    Call this when danger alerts are active.
    alerts = list of alert dicts from get_danger_alerts()
    """
    sender   = os.environ.get("EMAIL_SENDER", "")
    password = os.environ.get("EMAIL_PASSWORD", "")
    recipients = os.environ.get("ALERT_RECIPIENTS", "")

    if not sender or not password or not recipients:
        print("Email config missing in .env — skipping alert")
        return False

    to_list = [r.strip() for r in recipients.split(",")]

    # build the email body
    alert_rows = ""
    for a in alerts:
        alert_rows += f"""
        <tr>
            <td>{a['river']}</td>
            <td>{a['gauge_station']}</td>
            <td>{a['gauge_level_m']} m</td>
            <td>{a['danger_level']} m</td>
            <td>{a.get('trend', 'N/A')}</td>
        </tr>"""

    html = f"""
    <html><body>
    <h2 style="color:#c0392b;">🚨 WMD Flood Danger Alert — {datetime.now().strftime('%d %b %Y %H:%M')}</h2>
    <p><b>{len(alerts)} river gauge(s)</b> have exceeded danger levels in West Bengal.</p>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
        <tr style="background:#f0b0a0;">
            <th>River</th><th>Station</th><th>Current Level</th>
            <th>Danger Level</th><th>Trend</th>
        </tr>
        {alert_rows}
    </table>
    <br>
    <p>Max rainfall today: <b>{summary.get('max_rainfall_mm', 'N/A')} mm</b> 
       at {summary.get('max_station', 'N/A')}</p>
    <p style="color:#888;font-size:12px;">— WMD Irrigation Monitor, West Bengal I&WD</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 Flood Alert — {len(alerts)} danger breach(es) detected"
    msg["From"]    = sender
    msg["To"]      = ", ".join(to_list)
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_list, msg.as_string())
        print(f"Alert email sent to {to_list}")
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False