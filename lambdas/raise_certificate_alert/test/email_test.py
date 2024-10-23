"""Test email functions"""

from os import environ
from unittest.mock import MagicMock, patch

from ..email import (
    email_alert,
    hydrate_email_alert_and_send,
    hydrate_email_alert_message,
)

FILE_PATH = "lambdas.raise_certificate_alert.email"
SUBJECT = "Test subject"
MESSAGE = "Test message"
TEMPLATE = "Test template"


@patch(f"{FILE_PATH}.email_alert")
@patch(f"{FILE_PATH}.hydrate_email_alert_message")
def test_hydrate_email_alert_and_send(
    mock_hydrate_email_alert_message: MagicMock, mock_email_alert: MagicMock
) -> None:
    """Test hydrate email alert and send"""
    # Arrange
    secret_manager = MagicMock()
    content_to_replace = {"key": "value"}
    mock_hydrate_email_alert_message.return_value = SUBJECT, TEMPLATE
    # Act
    hydrate_email_alert_and_send(SUBJECT, TEMPLATE, content_to_replace, secret_manager)
    # Assert
    mock_hydrate_email_alert_message.assert_called_once_with(
        SUBJECT, TEMPLATE, content_to_replace
    )
    mock_email_alert.assert_called_once_with(SUBJECT, TEMPLATE, secret_manager)


@patch(f"{FILE_PATH}.send_email")
def test_email_alert(mock_send_email: MagicMock) -> None:
    """Test email alert"""
    # Arrange
    secret_manager = MagicMock()
    secret_manager.get_secret.side_effect = ["api_url", "subscription_key"]
    environ["TEAM_EMAIL"] = email = "test@test.com"
    # Act
    email_alert(SUBJECT, MESSAGE, secret_manager)
    # Assert
    mock_send_email.assert_called_once_with(
        to_email_address=email,
        subject=SUBJECT,
        body=MESSAGE,
        api_url="api_url",
        subscription_key="subscription_key",
    )
    # Cleanup
    del environ["TEAM_EMAIL"]


def test_hydrate_email_alert_message() -> None:
    """Test hydrate email alert message"""
    # Arrange
    content_to_replace = {"key": "value"}
    # Act
    subject, content = hydrate_email_alert_message(
        SUBJECT, TEMPLATE, content_to_replace
    )
    # Assert
    assert subject == SUBJECT
    assert content == TEMPLATE
