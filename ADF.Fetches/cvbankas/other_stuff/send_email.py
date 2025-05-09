import os
import smtplib
from email.mime.text import MIMEText
from other_stuff.log_config import logger


# using "app password" from google(gmail), can be obtained from https://myaccount.google.com/apppasswords


def send_email(subject, body):
    logger.info("Preparing to send an email")

    from_email = os.getenv("EMAIL_FROM_WHO")
    password = os.getenv("EMAIL_FROM_WHO_PASSWORD")
    to_emails = os.getenv("EMAILS_TO_WHOM").split(",")
    smtp_server = os.getenv("SMTP_SERVER")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    with smtplib.SMTP_SSL(smtp_server, 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_emails, msg.as_string())

        logger.info("Email was sent")
