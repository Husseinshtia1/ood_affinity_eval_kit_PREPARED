from apps.api.notifications import build_invitation_message


def test_build_invitation_message_contains_accept_link():
    message = build_invitation_message('user@example.com', 'token-123')

    assert message['To'] == 'user@example.com'
    assert message['Subject'] == 'You have been invited to PREPARED.ai'
    assert 'accept-invitation?token=token-123' in message.as_string()
    assert 'text/html' in message.as_string()
