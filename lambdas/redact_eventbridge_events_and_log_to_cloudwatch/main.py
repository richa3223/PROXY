"""Redact sensitive information from EventBridge events and log to CloudWatch."""

from json import dumps
from os import getenv
from time import time

from boto3 import client
from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log


class RedactEventBridgeEventsAndLogToCloudWatch(LambdaApplication):
    """Lambda process to redact sensitive values before they are stored in CloudWatch."""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Redact all sensitive fields in a given event."""
        log_group = getenv("CLOUDWATCH_LOG_GROUP_NAME")
        log_stream = getenv("CLOUDWATCH_LOG_STREAM_NAME")
        write_log("DEBUG", {"info": f"Writing logs to log group: {log_group}"})
        write_log("DEBUG", {"info": f"Writing logs to log stream: {log_stream}"})
        self._verify_parameters(log_group, log_stream)
        event = dict(self.event)
        redacted_record = self._redact_sensitive_data(event)
        self._log_to_cloudwatch(redacted_record, log_group, log_stream)
        self.response = {"body": "Success"}

    def _verify_parameters(self, log_group: str, log_stream: str) -> None:
        """Verify the required parameters are set."""
        if not log_group:
            raise ValueError("CLOUDWATCH_LOG_GROUP_NAME is not set")
        if not log_stream:
            raise ValueError("CLOUDWATCH_LOG_STREAM_NAME is not set")

    def _redact_sensitive_data(self, event_bridge_event: dict) -> dict:
        """Redact sensitive data from a given event."""
        if (
            "detail" in event_bridge_event
            and "sensitive" in event_bridge_event["detail"]
        ):
            for key in event_bridge_event["detail"]["sensitive"]:
                event_bridge_event["detail"]["sensitive"][key] = "[REDACTED]"
            write_log("DEBUG", {"info": "Data successfully redacted for event."})
        else:
            write_log(
                "WARNING", {"info": "Sensitive data not found in the passed events"}
            )

        return event_bridge_event

    def _log_to_cloudwatch(
        self, redacted_record: dict, log_group: str, log_stream: str
    ) -> None:
        """Log redacted record to CloudWatch.

        Args:
            redacted_record (dict): Redacted record.
            log_group (str): CloudWatch log group.
            log_stream (str): CloudWatch log stream.
        """
        client("logs").put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[
                {
                    "timestamp": round(time() * 1000),
                    "message": dumps(redacted_record),
                }
            ],
        )


redact_eventbridge_events_and_log_to_cloudwatch = (
    RedactEventBridgeEventsAndLogToCloudWatch(additional_log_config=LOG_BASE)
)


def lambda_handler(event: dict, context: dict) -> dict:
    """Redact sensitive information from EventBridge events and log to CloudWatch.

    Args:
        event (dict): EventBridge event.
        context (dict): Lambda context.

    Returns:
        dict: Redacted event.
    """
    return redact_eventbridge_events_and_log_to_cloudwatch.main(event, context)
