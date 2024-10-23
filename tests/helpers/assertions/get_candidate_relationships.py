def assert_401_insufficient_authorisation(payload: dict) -> None:
    """Asserts the payload is a 401 Insufficient Authorisation response

    Args:
        payload (dict): The response payload
    """
    assert payload["body"] == {
        "issue": [
            {
                "code": "forbidden",
                "details": {
                    "coding": [
                        {
                            "code": "FORBIDDEN",
                            "display": "Access Denied",
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                            "version": "1",
                        }
                    ]
                },
                "diagnostics": "Insufficient authorisation to access resource - requires P9.",
                "severity": "error",
            }
        ],
        "resourceType": "OperationOutcome",
    }, f"Expected FORBIDDEN, got {payload['body']}"


def assert_403_forbidden(payload: dict) -> None:
    """Asserts the payload is a 403 Forbidden response

    Args:
        payload (dict): The response payload
    """
    assert payload["body"] == {
        "issue": [
            {
                "code": "forbidden",
                "details": {
                    "coding": [
                        {
                            "code": "FORBIDDEN",
                            "display": "Access Denied",
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                            "version": "1",
                        }
                    ]
                },
                "diagnostics": "Access denied to resource.",
                "severity": "error",
            }
        ],
        "resourceType": "OperationOutcome",
    }, f"Expected FORBIDDEN, got {payload['body']}"
