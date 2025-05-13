import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from other_stuff.log_config import logger


# using "app password" from google(gmail), can be obtained from https://myaccount.google.com/apppasswords


def send_email(subject, body, attachment_path=None):
    logger.info("Preparing to send an email")

    from_email = os.getenv("EMAIL_FROM_WHO")
    password = os.getenv("EMAIL_FROM_WHO_PASSWORD")
    to_emails = os.getenv("EMAILS_TO_WHOM").split(",")
    smtp_server = os.getenv("SMTP_SERVER")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    # Attach the body of the email
    msg.attach(MIMEText(body, "plain"))

    # Attach the job_ads.db file if the path is provided
    if attachment_path:
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                msg.attach(part)
                logger.info("Attachment added successfully")
        except Exception as e:
            logger.error(f"Failed to attach the file: {e}")

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_emails, msg.as_string())
            logger.info("Email was sent")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


def send_i_am_alive_email(subject, body):
    logger.info("Preparing to send 'I am alive' email")

    from_email = os.getenv("EMAIL_FROM_WHO")
    password = os.getenv("EMAIL_FROM_WHO_PASSWORD")
    to_emails = os.getenv("I_AM_ALIVE_EMAIL_RECIPIENT").split(",")
    smtp_server = os.getenv("SMTP_SERVER")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    with smtplib.SMTP_SSL(smtp_server, 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_emails, msg.as_string())

        logger.info("'I am alive' email was sent")
