"""
Test sensitive data is redacted
"""

import json
from base64 import b64decode, b64encode

from ..helpers import WORKSPACE, Helpers

REDACTED = "REDACTED"
FUNCTION_NAME = f"{WORKSPACE}-redact_sensitive_data"


def test_redact_data_missing_sensitive_block(helpers: Helpers) -> None:
    """
    Test to ensure data is not redacted when
    the sensitive object is not present in the event
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME,
        {
            "records": [
                {
                    "recordId": "11111111111111111111111111111111111111111111111111111111111",
                    "approximateArrivalTimestamp": 1710845104989,
                    "data": b64encode(
                        json.dumps(
                            {
                                "version": "0",
                                "id": "144a6f5b-cbb6-85c1-a96a-a895034e97ae",
                                "detail-type": "Validation Successful",
                                "source": "Validation Service",
                                "account": "123456789",
                                "time": "2024-01-26T15:23:24Z",
                                "region": "eu-west-2",
                                "resources": [],
                                "detail": {
                                    "metadata": {
                                        "client-key": "d1191d07-8758-4c0f-b07c-cca2cb1b219c",
                                        "correlation-id": "3845e8d0-9f40-41a6-a491-c71e4b4214fd",
                                        "created": "2024-01-26T15:23:22.404477",
                                        "request-id": "cf3e76de-e34f-4cea-bc81-89b6ee6ba623",
                                    },
                                    "standard": {
                                        "proxy-identifier-type": "NHS Number",
                                        "relationship-type": "",
                                        "validation-result-info": {
                                            "VALIDATED_PROXY": "Validated Proxy"
                                        },
                                    },
                                },
                            }
                        ).encode("utf-8")
                    ).decode("utf-8"),
                }
            ]
        },
    )

    redacted_event = json.loads(
        b64decode(payload["records"][0]["data"]).decode("utf-8")
    )
    assert payload["records"][0]["result"] == "ProcessingFailed"
    assert REDACTED not in str(redacted_event)


def test_data_correctly_redacted(helpers: Helpers) -> None:
    """
    Test to ensure data is successfully redacted
    when the sensitive object is present in the event
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME,
        {
            "records": [
                {
                    "recordId": "11111111111111111111111111111111111111111111111111111111111",
                    "approximateArrivalTimestamp": 1710845104989,
                    "data": b64encode(
                        json.dumps(
                            {
                                "version": "0",
                                "id": "144a6f5b-cbb6-85c1-a96a-a895034e97ae",
                                "detail-type": "Validation Successful",
                                "source": "Validation Service",
                                "account": "123456789",
                                "time": "2024-01-26T15:23:24Z",
                                "region": "eu-west-2",
                                "resources": [],
                                "detail": {
                                    "metadata": {
                                        "client-key": "d1191d07-8758-4c0f-b07c-cca2cb1b219c",
                                        "correlation-id": "3845e8d0-9f40-41a6-a491-c71e4b4214fd",
                                        "created": "2024-01-26T15:23:22.404477",
                                        "request-id": "cf3e76de-e34f-4cea-bc81-89b6ee6ba623",
                                    },
                                    "sensitive": {
                                        "patient-identifier": "",
                                        "proxy-identifier": "9000000009",
                                    },
                                    "standard": {
                                        "proxy-identifier-type": "NHS Number",
                                        "relationship-type": "",
                                        "validation-result-info": {
                                            "VALIDATED_PROXY": "Validated Proxy"
                                        },
                                    },
                                },
                            }
                        ).encode("utf-8")
                    ).decode("utf-8"),
                }
            ]
        },
    )

    redacted_event = json.loads(
        b64decode(payload["records"][0]["data"]).decode("utf-8")
    )
    assert payload["records"][0]["result"] == "Ok"
    assert redacted_event["detail"]["sensitive"] == "[" + REDACTED + "]"
    assert str(redacted_event).count(REDACTED) == 1
