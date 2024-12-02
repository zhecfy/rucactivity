import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import os
from dotenv import load_dotenv

def send_email(subject: str, html_content: str) -> None:
    load_dotenv()

    FROM = os.getenv("FROM")
    TO = os.getenv("TO")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    PASSWORD = os.getenv("PASSWORD")

    message = MIMEMultipart()
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = f"RUCActivity<{FROM}>"
    message['To'] = TO

    message.attach(MIMEText(html_content, 'html'))

    try:
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp.login(FROM, PASSWORD)
        smtp.sendmail(FROM, TO, message.as_string())
        print("email sent")

    except Exception as e:
        print(f"email error: {e}")

    finally:
        smtp.quit()