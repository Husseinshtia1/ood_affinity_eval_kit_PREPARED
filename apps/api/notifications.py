from .settings import get_settings

settings = get_settings()


def send_invitation_email(email: str, token: str) -> bool:
    invitation_link = f"{settings.frontend_url}/accept-invitation?token={token}"

    if not settings.smtp_host:
        print(f"[NOTIFICATION] SMTP disabled. Invitation link for {email}: {invitation_link}")
        return False

    # SMTP provider integration comes here
    print(f"[NOTIFICATION] Sending invitation email to {email}")
    return True
