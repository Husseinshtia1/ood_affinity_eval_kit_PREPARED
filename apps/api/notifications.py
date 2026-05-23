from __future__ import annotations

import smtplib
from email.message import EmailMessage

from .settings import get_settings

settings = get_settings()


def build_invitation_message(email: str, token: str) -> EmailMessage:
    invitation_link = f"{settings.frontend_url}/accept-invitation?token={token}"
    message = EmailMessage()
    message['Subject'] = 'You have been invited to PREPARED.ai'
    message['From'] = settings.smtp_from_email
    message['To'] = email

    text_body = f"""You have been invited to PREPARED.ai.

Accept your invitation here:
{invitation_link}

If you did not expect this invitation, you can ignore this email.
"""

    html_body = f"""
<html>
  <body>
    <p>You have been invited to <strong>PREPARED.ai</strong>.</p>
    <p><a href="{invitation_link}">Accept your invitation</a></p>
    <p>If you did not expect this invitation, you can ignore this email.</p>
  </body>
</html>
"""

    message.set_content(text_body)
    message.add_alternative(html_body, subtype='html')
    return message


def send_invitation_email(email: str, token: str) -> bool:
    invitation_link = f"{settings.frontend_url}/accept-invitation?token={token}"

    if not settings.smtp_host:
        print(f"[NOTIFICATION] SMTP disabled. Invitation link for {email}: {invitation_link}")
        return False

    message = build_invitation_message(email, token)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.ehlo()
        if settings.smtp_port != 25:
            smtp.starttls()
            smtp.ehlo()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)

    return True
