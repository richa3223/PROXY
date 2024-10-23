"""
Asserts for Generic HTTP Errors
"""


def assert_500_internal_server_error(payload: dict) -> None:
    """Asserts the payload is a 500 Internal Server Error response

    Args:
        payload (dict): The response payload
    """
    assert payload["body"] == {
        "issue": [
            {
                "code": "invalid",
                "details": {
                    "coding": [
                        {
                            "code": "SERVER_ERROR",
                            "display": "Failed to generate response",
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                            "version": "1",
                        }
                    ]
                },
                "diagnostics": "Internal Server Error - Failed to generate response",
                "severity": "error",
            }
        ],
        "resourceType": "OperationOutcome",
    }, f"Expected SERVER_ERROR, got {payload['body']}"
