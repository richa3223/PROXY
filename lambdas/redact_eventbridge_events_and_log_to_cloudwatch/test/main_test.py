"""Collection of tests for the main module."""

from unittest.mock import MagicMock, patch

import pytest

from lambdas.redact_eventbridge_events_and_log_to_cloudwatch.main import (
    RedactEventBridgeEventsAndLogToCloudWatch,
    lambda_handler,
)

FILE_PATH = "lambdas.redact_eventbridge_events_and_log_to_cloudwatch.main"


@patch(f"{FILE_PATH}.RedactEventBridgeEventsAndLogToCloudWatch.main")
def test_lambda_handler(mock_main):
    # Arrange
    event = {"key": "value"}
    context = MagicMock()
    # Act
    lambda_handler(event, context)
    # Assert
    mock_main.assert_called_once_with(event, context)


class TestRedactEventBridgeEventsAndLogToCloudWatch:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.redact_eventbridge_events_and_log_to_cloudwatch = (
            RedactEventBridgeEventsAndLogToCloudWatch()
        )

    @patch(f"{FILE_PATH}.RedactEventBridgeEventsAndLogToCloudWatch._log_to_cloudwatch")
    @patch(
        f"{FILE_PATH}.RedactEventBridgeEventsAndLogToCloudWatch._redact_sensitive_data"
    )
    @patch(f"{FILE_PATH}.RedactEventBridgeEventsAndLogToCloudWatch._verify_parameters")
    def test_main(
        self,
        mock_verify_parameters: MagicMock,
        mock_redact_sensitive_data: MagicMock,
        mock_log_to_cloudwatch: MagicMock,
    ) -> None:
        # Arrange
        event = {"key": "value"}
        context = MagicMock()
        # Act
        self.redact_eventbridge_events_and_log_to_cloudwatch.main(event, context)
        # Assert
        mock_verify_parameters.assert_called_once()
        mock_redact_sensitive_data.assert_called_once_with(event)
        mock_log_to_cloudwatch.assert_called_once()

    @patch(f"{FILE_PATH}.write_log")
    def test_redact_sensitive_data(self, mock_write_log: MagicMock) -> None:
        # Arrange
        event_bridge_event = {"detail": {"sensitive": {"key": "value"}}}
        # Act
        result = (
            self.redact_eventbridge_events_and_log_to_cloudwatch._redact_sensitive_data(
                event_bridge_event
            )
        )
        # Assert
        assert result == {"detail": {"sensitive": {"key": "[REDACTED]"}}}
        mock_write_log.assert_called_once_with(
            "DEBUG", {"info": "Data successfully redacted for event."}
        )

    @patch(f"{FILE_PATH}.write_log")
    def test_redact_sensitive_data_no_sensitive_data(
        self, mock_write_log: MagicMock
    ) -> None:
        # Arrange
        event_bridge_event = {"detail": {}}
        # Act
        result = (
            self.redact_eventbridge_events_and_log_to_cloudwatch._redact_sensitive_data(
                event_bridge_event
            )
        )
        # Assert
        assert result == {"detail": {}}
        mock_write_log.assert_called_once_with(
            "WARNING", {"info": "Sensitive data not found in the passed events"}
        )

    @patch(f"{FILE_PATH}.time")
    @patch(f"{FILE_PATH}.client")
    def test_log_to_cloudwatch(
        self, mock_client: MagicMock, mock_time: MagicMock
    ) -> None:
        # Arrange
        redacted_record = {"key": "value"}
        self.redact_eventbridge_events_and_log_to_cloudwatch.log_group = group = "group"
        self.redact_eventbridge_events_and_log_to_cloudwatch.log_stream = stream = (
            "stream"
        )
        mock_time.return_value = time = 0
        # Act
        self.redact_eventbridge_events_and_log_to_cloudwatch._log_to_cloudwatch(
            redacted_record, group, stream
        )
        # Assert
        mock_client.assert_called_once_with("logs")
        mock_client.return_value.put_log_events.assert_called_once_with(
            logGroupName=group,
            logStreamName=stream,
            logEvents=[
                {
                    "timestamp": time,
                    "message": '{"key": "value"}',
                }
            ],
        )

    def test_redact_eventbridge_events_and_log_to_cloudwatch_verify_parameters(
        self,
    ) -> None:
        # Arrange
        self.redact_eventbridge_events_and_log_to_cloudwatch.log_group = group = "group"
        self.redact_eventbridge_events_and_log_to_cloudwatch.log_stream = stream = (
            "stream"
        )
        # Act & Assert
        self.redact_eventbridge_events_and_log_to_cloudwatch._verify_parameters(
            group, stream
        )
