"""Tests for the slack module."""

from json import dumps
from os import environ
from unittest.mock import MagicMock, patch

from ..slack import (
    EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME,
    get_slack_message_template,
    hydrate_slack_alert_and_send,
    hydrate_slack_alert_message,
    send_slack_alert,
)

FILE_PATH = "lambdas.raise_certificate_alert.slack"


@patch(f"{FILE_PATH}.send_slack_alert")
@patch(f"{FILE_PATH}.hydrate_slack_alert_message")
def test_hydrate_slack_alert_and_send(
    mock_hydrate_slack_alert_message: MagicMock, mock_send_slack_alert: MagicMock
) -> None:
    """Test hydrate slack alert and send"""
    # Arrange
    content_to_replace = {"key": "value"}
    # Act
    hydrate_slack_alert_and_send("file_name", content_to_replace)
    # Assert
    mock_hydrate_slack_alert_message.assert_called_once_with(
        "file_name", content_to_replace
    )
    mock_send_slack_alert.assert_called_once_with(
        mock_hydrate_slack_alert_message.return_value
    )


@patch(f"{FILE_PATH}.client")
def test_send_slack_alert(mock_client: MagicMock) -> None:
    """Test send slack alert"""
    # Arrange
    message = {"key": "value"}
    environ["SLACK_ALERTS_LAMBDA_FUNCTION_NAME"] = lambda_function = (
        "slack_alerts_lambda_function_name"
    )
    # Act
    send_slack_alert(message)
    # Assert
    mock_client.assert_called_once_with("lambda")
    mock_client.return_value.invoke.assert_called_once_with(
        FunctionName=lambda_function,
        InvocationType="RequestResponse",
        Payload=dumps(message),
    )
    # Cleanup
    del environ["SLACK_ALERTS_LAMBDA_FUNCTION_NAME"]


@patch(f"{FILE_PATH}.get_slack_message_template")
def test_hydrate_slack_alert_message(
    mock_get_slack_message_template: MagicMock,
) -> None:
    """Test hydrate slack alert message"""
    # Arrange
    content_to_replace = {"key": "value"}
    mock_get_slack_message_template.return_value = '{"message": "html_string <key>"}'
    # Act
    result = hydrate_slack_alert_message("file_name", content_to_replace)
    # Assert
    assert result == {"message": "html_string value"}


def test_get_slack_message_template() -> None:
    """Test get slack message template"""
    # Arrange
    mock_open = MagicMock()
    with patch(f"{FILE_PATH}.open", mock_open):
        # Act
        result = get_slack_message_template(EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME)
        # Assert
        mock_open.assert_called_once_with(
            f"lambdas/raise_certificate_alert/slack_alert_templates/{EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME}",
            "r",
        )
        assert result == mock_open.return_value.__enter__.return_value.read.return_value
