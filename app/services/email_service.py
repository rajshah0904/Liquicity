from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import secrets
import datetime


class EmailServiceError(Exception):
    """Custom exception for email service failures"""
    pass


def generate_verification_token():
    """
    Generate a URL-safe token and expiration timestamp (24h) for email verification.
    Returns (token, expires_at).
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    return token, expires_at


def generate_reset_token():
    """
    Generate a URL-safe token and expiration timestamp (1h) for password reset.
    Returns (token, expires_at).
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    return token, expires_at


def _send_email(subject: str, recipient: str, html_body: str):
    """
    Internal helper to send an email via SMTP using environment variables:
    SMTP_HOST, SMTP_PORT, EMAIL_USER, EMAIL_PASS.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not smtp_host or not user or not password:
        raise EmailServiceError("SMTP configuration is incomplete.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    part = MIMEText(html_body, "html")
    msg.attach(part)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def send_verification_email(email: str, token: str):
    """
    Send an email verification link to the user.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_link = f"{frontend_url}/verify-email?token={token}"
    subject = "Verify your Liquicity account"
    html = (
        f"<p>Welcome to Liquicity! Please verify your email by clicking "
        f"<a href=\"{verify_link}\">here</a>. This link expires in 24 hours.</p>"
    )
    _send_email(subject, email, html)


def send_password_reset_email(email: str, token: str):
    """
    Send a password reset link to the user.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={token}"
    subject = "Liquicity Password Reset Request"
    html = (
        f"<p>You requested to reset your password. Click "
        f"<a href=\"{reset_link}\">here</a> to proceed. This link expires in 1 hour.</p>"
    )
    _send_email(subject, email, html) 