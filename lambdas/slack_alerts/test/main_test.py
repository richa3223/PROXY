"""Test the main module."""

from os import environ
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from lambdas.slack_alerts.main import lambda_handler, send_slack_message, slack_alerts


@patch("lambdas.slack_alerts.main.send_slack_message")
def test_slack_alerts(mock_send_slack_message: MagicMock) -> None:
    """Test the slack_alerts function."""
    # Arrange
    mock_send_slack_message.return_value = None
    event = {"message": "test"}
    # Act
    slack_alerts(event)
    # Assert
    mock_send_slack_message.assert_called_once_with(event)


@patch("lambdas.slack_alerts.main.post")
def test_send_slack_message(mock_post: MagicMock) -> None:
    """Test the send_slack_message function."""
    # Arrange
    mock_post.return_value = MagicMock(status_code=200, reason="OK", text="OK")
    message = {"message": "test"}
    environ["SLACK_WEBHOOK_URL"] = webhook = "https://hooks.slack.com/services/test"
    # Act
    send_slack_message(message)
    # Assert
    mock_post.assert_called_once_with(webhook, json=message)
    # Cleanup
    del environ["SLACK_WEBHOOK_URL"]


@pytest.mark.parametrize(
    "status_code, reason",
    [
        (400, "BAD_REQUEST"),
        (500, "TEST"),
    ],
)
@patch("lambdas.slack_alerts.main.post")
def test_send_slack_message__api_error(
    mock_post: MagicMock, status_code: int, reason: str
) -> None:
    """Test the send_slack_message function."""
    # Arrange
    mock_post.return_value = MagicMock(status_code=status_code, reason=reason)
    message = {"message": "test"}
    environ["SLACK_WEBHOOK_URL"] = webhook = "https://hooks.slack.com/services/test"
    # Act
    with pytest.raises(
        ValueError,
        match=f"Slack alert failed with response.status_code={status_code} response.reason='{reason}'",
    ):
        send_slack_message(message)
    # Assert
    mock_post.assert_called_once_with(webhook, json=message)
    # Cleanup
    del environ["SLACK_WEBHOOK_URL"]


@patch("lambdas.slack_alerts.main.send_slack_message")
def test_lambda_handler(
    mock_send_slack_message: MagicMock, lambda_context: LambdaContext
) -> None:
    """Test the lambda_handler function."""
    # Arrange
    mock_send_slack_message.return_value = None
    event = {"message": "test"}
    # Act
    lambda_handler(event, lambda_context)
    # Assert
    mock_send_slack_message.assert_called_once_with(event)
