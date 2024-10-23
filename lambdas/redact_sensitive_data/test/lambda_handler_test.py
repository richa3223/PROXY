"""
Collection of tests for the redact sensitive data  lambda function.
"""

import json
from base64 import b64decode, b64encode, decode

import pytest

from lambdas.redact_sensitive_data.main import RedactData, lambda_handler


@pytest.fixture
def correct_sample_event():
    """Fixture providing a sample event for testing."""
    return {
        "records": [
            {
                "recordId": "11111111111111111111111111111111111111111111111111111111111",
                "approximateArrivalTimestamp": 1710845104989,
                "data": b64encode(
                    json.dumps(
                        {
                            "version": "0",
                            "id": "114f5e13-2ad8-c938-8e39-4c2b7d98b64b",
                            "detail-type": "Validation Succesful",
                            "source": "Validation Service",
                            "account": "111111111111",
                            "time": "2024-03-18T13:36:32Z",
                            "region": "eu-west-2",
                            "resources": [],
                            "detail": {
                                "metadata": {
                                    "client-key": "CLIENT_KEY_PLACEHOLDER",
                                    "correlation-id": "CORRELATION_ID_PLACEHOLDER",
                                    "created": "CREATED_PLACEHOLDER",
                                    "request-id": "REQUEST_ID_PLACEHOLDER",
                                },
                                "sensitive": {
                                    "patient-identifier": "PATIENT_IDENTIFIER_PLACEHOLDER",
                                    "proxy-identifier": "PROXY_IDENTIFIER_PLACEHOLDER",
                                },
                                "standard": {
                                    "proxy-identifier-type": "PROXY_IDENTIFIER_TYPE_PLACEHOLDER",
                                    "relationship-type": "RELATIONSHIP_TYPE_PLACEHOLDER",
                                    "validation-result-info": {
                                        "VALIDATED_RELATIONSHIP": "Validated relationship"
                                    },
                                },
                            },
                        }
                    ).encode("utf-8")
                ).decode("utf-8"),
            }
        ]
    }


@pytest.fixture
def incorrect_sample_event():
    """Fixture providing a sample event with the sensitive block missing for testing."""
    return {
        "records": [
            {
                "recordId": "11111111111111111111111111111111111111111111111111111111111",
                "approximateArrivalTimestamp": 1710845104989,
                "data": b64encode(
                    json.dumps(
                        {
                            "version": "0",
                            "id": "114f5e13-2ad8-c938-8e39-4c2b7d98b64b",
                            "detail-type": "Validation Succesful",
                            "source": "Validation Service",
                            "account": "111111111111",
                            "time": "2024-03-18T13:36:32Z",
                            "region": "eu-west-2",
                            "resources": [],
                            "detail": {
                                "metadata": {
                                    "client-key": "CLIENT_KEY_PLACEHOLDER",
                                    "correlation-id": "CORRELATION_ID_PLACEHOLDER",
                                    "created": "CREATED_PLACEHOLDER",
                                    "request-id": "REQUEST_ID_PLACEHOLDER",
                                },
                                "standard": {
                                    "proxy-identifier-type": "PROXY_IDENTIFIER_TYPE_PLACEHOLDER",
                                    "relationship-type": "RELATIONSHIP_TYPE_PLACEHOLDER",
                                    "validation-result-info": {
                                        "VALIDATED_RELATIONSHIP": "Validated relationship"
                                    },
                                },
                            },
                        }
                    ).encode("utf-8")
                ).decode("utf-8"),
            }
        ]
    }


def test_redact_data_missing_sensitive_block(incorrect_sample_event, mocker):
    """Test to ensure log is written when sensitive block is not found and returned record has a status of ProcesingFailed."""

    # Arrange
    mock_write_log = mocker.patch("lambdas.redact_sensitive_data.main.write_log")
    redact_data = RedactData(additional_log_config="mock_log_base")

    # Act
    redacted_data = redact_data.main(incorrect_sample_event, {})

    # Assert
    mock_write_log.assert_any_call(
        "ERROR",
        {
            "info": "Processing failed because the sensitive block was not found in the passed events, see CloudWatch logs for details.",
            "error": "",
        },
    )
    assert redacted_data["records"][0]["result"] == "ProcessingFailed"


def test_data_correctly_redacted(correct_sample_event, mocker):
    """Test to ensure data is successfully redacted"""

    # Arrange
    mock_write_log = mocker.patch("lambdas.redact_sensitive_data.main.write_log")
    redact_data = RedactData(additional_log_config="mock_log_base")

    # Act
    redacted_data = redact_data.main(correct_sample_event, {})
    redacted_event = json.loads(
        b64decode(redacted_data["records"][0]["data"]).decode("utf-8")
    )

    # Assert
    mock_write_log.assert_any_call(
        "DEBUG",
        {"info": "Data successfully redacted for event."},
    )
    assert redacted_data["records"][0]["result"] == "Ok"
    assert redacted_event["detail"]["sensitive"] == "[REDACTED]"
