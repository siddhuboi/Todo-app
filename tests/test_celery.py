from unittest.mock import patch,MagicMock
from celery_tasks import send_task_email
import pytest
import smtplib
from send_email import send_mail
@patch("celery_tasks.send_mail")
def test_send_task_email(mock_send_mail):
    send_task_email(receiver_mail="test@example.com",
                    subject="Test subject",
                    body="The body")

    mock_send_mail.assert_called_once_with(
        receiver_mail="test@example.com",
        subject="Test subject",
        body='The body'
    )

@patch("celery_tasks.send_mail")
def test_send_task_email_failure(mock_send_mail):

    mock_send_mail.side_effect = Exception("Email sending failed")

    with pytest.raises(Exception, match="Email sending failed"):
        send_task_email(
            receiver_mail="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )

    mock_send_mail.assert_called_once_with(
        receiver_mail="test@example.com",
        subject="Test Subject",
        body="Test Body"
    )

@patch("send_email.smtplib.SMTP_SSL")
@patch("send_email.os.getenv")
def test_send_mail(mock_getenv,mock_smtp):
    mock_getenv.side_effect=[
        "sender@gmail.com",
        "app-password"
    ]
    mock_server=MagicMock()
    mock_smtp.return_value.__enter__.return_value=mock_server
    send_mail(
        receiver_mail="test@example.com",
        subject="Test Subject",
        body="Test Body"
    )
    mock_smtp.assert_called_once_with("smtp.gmail.com",465)
    mock_server.login.assert_called_once_with(
        "sender@gmail.com",
        "app-password"
    )
    mock_server.send_message.assert_called_once()

@patch("send_email.os.getenv")
def test_send_mail_missing_credentials(mock_getenv):

    mock_getenv.side_effect = [
        None,
        None
    ]

    with pytest.raises(
        ValueError,
        match="Email credentials are not configured"
    ):
        send_mail(
            receiver_mail="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )

@patch("send_email.smtplib.SMTP_SSL")
@patch("send_email.os.getenv")
def test_send_mail_smtp_connection_failure(mock_getenv, mock_smtp):

    mock_getenv.side_effect = [
        "sender@gmail.com",
        "app-password"
    ]

    mock_smtp.side_effect = smtplib.SMTPServerDisconnected(
        "Connection unexpectedly closed"
    )

    with pytest.raises(
        smtplib.SMTPServerDisconnected,
        match="Connection unexpectedly closed"
    ):
        send_mail(
            receiver_mail="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )