"""Test the redact_eventbridge_events_and_log_to_cloudwatch Lambda function correctly redacts sensitive data and logs to CloudWatch."""

from datetime import datetime
from json import dumps, loads
from logging import getLogger
from time import sleep
from uuid import uuid4

import pytest
from boto3 import client
from botocore.exceptions import ClientError

from ..helpers import ENVIRONMENT, WORKSPACE
from ..helpers.aws.cloudwatch import (
    create_log_group,
    create_log_stream,
    delete_log_group,
)
from ..helpers.aws.eventbridge import EVENT_BUS_NAME

FUNCTION_NAME = f"{WORKSPACE}-redact_eventbridge_events_and_log_to_cloudwatch"
TAGS = {
    "Environment": ENVIRONMENT,
    "Workspace": WORKSPACE,
    "Test": "Infrastructure",
    "TestClass": "TestRedactEventBridgeEventsAndLogToCloudWatch",
}


lambda_client = client("lambda")
log_client = client("logs")
eventbridge_client = client("events")
iam_client = client("iam")

logger = getLogger(__name__)

LOG_GROUP_PREFIX = "eventbridge-log-redaction-infrastructure-test"
RULE_NAME = "redact-eventbridge-events-and-log-to-cloudwatch-rule"
EVENT_SOURCE = "test-infrastructure"


class TestRedactEventBridgeEventsAndLogToCloudWatch:

    def teardown_class(self) -> None:
        """Remove any remaining log groups"""
        log_groups = log_client.describe_log_groups(
            logGroupNamePrefix=LOG_GROUP_PREFIX
        )["logGroups"]
        logger.debug(f"Log groups: {log_groups}")
        for log_group in log_groups:
            delete_log_group(log_group["logGroupName"])

    @pytest.fixture()
    def setup_and_teardown_infrastructure(self):
        """Set up and tear down the infrastructure for the test."""
        # EventBridge restrict logging rule
        current_pattern = self.__get_and_update_eventbridge_rule()
        # Get the current log group and stream from the Lambda configuration
        current_log_group, current_log_stream = self.__get_lambda_config()
        # Create the new log group and stream
        infrastructure_name = f"{LOG_GROUP_PREFIX}-{str(uuid4())}"
        create_log_group(infrastructure_name, TAGS)
        create_log_stream(infrastructure_name, infrastructure_name)
        # Update the Lambda configuration
        self.__update_lambda_config(infrastructure_name, infrastructure_name)
        logger.info(f"Waiting for Lambda configuration to update: {FUNCTION_NAME}")
        sleep(60)
        logger.info(f"Lambda configuration updated: {FUNCTION_NAME}")
        # Run the test
        yield
        # Reset the Lambda configuration
        self.__update_lambda_config(current_log_group, current_log_stream)
        # Reset the EventBridge rule
        self.__reset_eventbridge_rule(current_pattern)
        # Tear down the infrastructure
        delete_log_group(infrastructure_name)

    def __get_lambda_config(self) -> tuple[str, str]:
        """Get the current log group and stream from the Lambda configuration."""
        lambda_config = lambda_client.get_function(FunctionName=FUNCTION_NAME)
        environment = lambda_config["Configuration"]["Environment"]["Variables"]
        current_log_group = environment["CLOUDWATCH_LOG_GROUP_NAME"]
        current_log_stream = environment["CLOUDWATCH_LOG_STREAM_NAME"]
        return current_log_group, current_log_stream

    def __update_lambda_config(self, log_group, log_stream) -> None:
        """Update the Lambda configuration with the given log group and stream."""
        try:
            lambda_client.update_function_configuration(
                FunctionName=FUNCTION_NAME,
                Environment={
                    "Variables": {
                        "CLOUDWATCH_LOG_GROUP_NAME": log_group,
                        "CLOUDWATCH_LOG_STREAM_NAME": log_stream,
                    }
                },
            )
        except ClientError as error:
            if "ResourceConflictException" in str(error):
                sleep(15)
                self.__update_lambda_config(log_group, log_stream)

    def __get_and_update_eventbridge_rule(self) -> str:
        """Get the current EventBridge rule and update it to restrict logging."""
        current_pattern = eventbridge_client.describe_rule(
            Name=RULE_NAME, EventBusName=EVENT_BUS_NAME
        )["EventPattern"]
        eventbridge_client.put_rule(
            Name=RULE_NAME,
            EventBusName=EVENT_BUS_NAME,
            EventPattern=dumps({"source": [EVENT_SOURCE]}),
            State="ENABLED",
        )
        logger.info(f"EventBridge rule updated with test filter: {RULE_NAME}")
        return current_pattern

    def __reset_eventbridge_rule(self, current_pattern: str) -> None:
        """Reset the EventBridge rule to the original pattern."""
        eventbridge_client.put_rule(
            Name=RULE_NAME,
            EventBusName=EVENT_BUS_NAME,
            EventPattern=current_pattern,
            State="ENABLED",
        )
        logger.info(f"EventBridge rule reset: {RULE_NAME}")

    def __await_log_events(self) -> dict:
        """Await the log event to be available in CloudWatch."""
        log_group_name, log_stream_name = self.__get_lambda_config()
        log_events = []
        seconds = 10
        logger.info(f"Checking for log events in {log_group_name}")
        for counter in range(18):
            log_events = log_client.get_log_events(
                logGroupName=log_group_name, logStreamName=log_stream_name
            )
            if log_events["events"]:
                break
            logger.info(f"Counter: {counter}, Sleeping for {seconds} seconds...")
            sleep(seconds)
            logger.info(f"Waited for {(counter+1)*seconds} seconds...")
        else:
            logger.error(
                "Timed out waiting for log events to be available, resetting Lambda configuration."
            )
            self.__update_lambda_config(log_group_name, log_stream_name)
            raise TimeoutError("Timed out waiting for log events to be available.")
        return log_events

    @pytest.mark.parametrize(
        "detail,expected",
        [
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "patient-identifier": "9730675929",
                        "proxy-identifier": "9730676399",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "proxy-identifier": "[REDACTED]",
                    "patient-identifier": "[REDACTED]",
                },
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "patient-identifier": "",
                        "proxy-identifier": "",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "proxy-identifier": "[REDACTED]",
                    "patient-identifier": "[REDACTED]",
                },
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "proxy-identifier": "",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "proxy-identifier": "[REDACTED]",
                },
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "patient-identifier": "",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "patient-identifier": "[REDACTED]",
                },
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {},
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {},
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "patient-identifier": "9730675929",
                        "proxy-identifier": "",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "proxy-identifier": "[REDACTED]",
                    "patient-identifier": "[REDACTED]",
                },
            ),
            (
                {
                    "metadata": {
                        "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                        "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                        "created": "2024-06-06T11:41:52.931714",
                        "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
                    },
                    "sensitive": {
                        "patient-identifier": "",
                        "proxy-identifier": "9730675929",
                    },
                    "standard": {
                        "proxy-identifier-type": "NHS Number",
                        "relationship-type": "",
                        "validation-result-info": {
                            "VALIDATED_RELATIONSHIP": "Validated Relationship"
                        },
                    },
                },
                {
                    "proxy-identifier": "[REDACTED]",
                    "patient-identifier": "[REDACTED]",
                },
            ),
        ],
    )
    def test_redact_eventbridge_events_and_log_to_cloudwatch(
        self,
        detail: dict,
        expected: str,
        setup_and_teardown_infrastructure,
    ) -> None:
        """EventBridge receives an event with sensitive data.
        The Lambda redacts the sensitive data
        Then logs redacted event to CloudWatch."""
        # Act
        logger.info(f"Sending event to EventBridge: {EVENT_BUS_NAME}")
        eventbridge_client.put_events(
            Entries=[
                {
                    "Time": datetime(2015, 1, 1),
                    "Source": EVENT_SOURCE,
                    "Resources": ["string"],
                    "DetailType": "string",
                    "Detail": dumps(detail),
                    "EventBusName": EVENT_BUS_NAME,
                },
            ]
        )
        # Await the log event to be available in CloudWatch
        log_events = self.__await_log_events()
        # Assert

        message = loads(log_events["events"][0]["message"])
        logger.info(f"Message: {message}")
        assert message["detail"]["sensitive"] == expected

    def test_redact_eventbridge_events_and_log_to_cloudwatch__no_sensitive(
        self,
        setup_and_teardown_infrastructure,
    ) -> None:
        """EventBridge receives an event without sensitive data.
        The Lambda logs the event to CloudWatch."""
        # Act
        logger.info(f"Sending event to EventBridge: {EVENT_BUS_NAME}")
        details = {
            "metadata": {
                "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                "correlation-id": "fee18326-88ec-42b1-8664-cfeb0ec63248",
                "created": "2024-06-06T11:41:52.931714",
                "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
            },
            "standard": {
                "proxy-identifier-type": "NHS Number",
                "relationship-type": "",
                "validation-result-info": {
                    "VALIDATED_RELATIONSHIP": "Validated Relationship"
                },
            },
        }
        eventbridge_client.put_events(
            Entries=[
                {
                    "Time": datetime(2015, 1, 1),
                    "Source": EVENT_SOURCE,
                    "Resources": ["string"],
                    "DetailType": "string",
                    "Detail": dumps(details),
                    "EventBusName": EVENT_BUS_NAME,
                },
            ]
        )
        # Await the log event to be available in CloudWatch
        log_events = self.__await_log_events()
        # Assert
        message = loads(log_events["events"][0]["message"])
        logger.info(f"Message: {message}")
        assert message["detail"] == details
