"""
Test redact eventbridge events and log to cloudwatch Lambda
"""

import pytest
from boto3 import client

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-redact_eventbridge_events_and_log_to_cloudwatch"


EVENT = {
    "version": "0",
    "id": "8b8975a9-aa5a-f66d-b82d-aeba42d1cf5c",
    "detail-type": "Validation Successful",
    "source": "Validation Service",
    "account": "1236545",
    "time": "2024-06-06T11:41:52Z",
    "region": "eu-west-2",
    "resources": [],
    "detail": {
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
}


EVENT_WITHOUT_SENSITIVE_DATA = EVENT.copy()
del EVENT_WITHOUT_SENSITIVE_DATA["detail"]["sensitive"]

EVENT_WITH_SENSITIVE_EMPTY_KEYS = EVENT.copy()
EVENT_WITH_SENSITIVE_EMPTY_KEYS["detail"]["sensitive"] = {
    "patient-identifier": "",
    "proxy-identifier": "",
}


log_client = client("logs")
lambda_client = client("lambda")


@pytest.mark.parametrize(
    "event",
    [
        EVENT.copy(),
        {
            "Source": "test_redact_eventbridge_events_and_log_to_cloudwatch__unexpected_event_format"
        },
        {},
        EVENT_WITHOUT_SENSITIVE_DATA.copy(),
        EVENT_WITH_SENSITIVE_EMPTY_KEYS.copy(),
    ],
)
def test_redact_eventbridge_events_and_log_to_cloudwatch(
    event: dict, helpers: Helpers
) -> None:
    """
    Lambda receives an event with sensitive data
    The Lambda returns a successful response

    NOTE: This test doesn't actually test the redaction of the sensitive data due to the delay in the CloudWatch logs
    As a result, the redacted data is not verified in this test but is verified in an infrastructure test
    """
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, event)
    # Assert
    assert payload["body"] == "Success"
