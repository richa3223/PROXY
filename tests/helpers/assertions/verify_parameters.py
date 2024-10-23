def assert_success(actual_response: dict, expected_response: dict) -> None:
    """Asserts the actual response is equal to the expected response

    Args:
        actual_response (dict): The actual response
        expected_response (dict): The expected response
    """
    del expected_response["accesstoken.auth_user_id"]
    del expected_response["accesstoken.auth_level"]
    assert (
        actual_response == expected_response
    ), f"Expected {expected_response}, got {actual_response}"


def assert_500_internal_server_error(payload: dict) -> None:
    """Asserts the payload is a 500 Internal Server Error response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 500,
        "response_code": "SERVER_ERROR",
        "audit_msg": "Internal Server Error - Failed to generate response",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Failed to generate response",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected SERVER_ERROR, got {payload['error']}"


def assert_400_x_request_id_not_found_error(payload: dict) -> None:
    """Asserts the payload is a 400 X-Request-ID not found response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 400,
        "response_code": "BAD_REQUEST",
        "audit_msg": "Invalid request with error - X-Request-ID header not found.",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Required header parameter(s) are missing.",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected X-Request-ID NOT FOUND, got {payload['error']}"


def assert_400_missing_identifier_value(payload: dict) -> None:
    """Asserts the payload is a 400 Missing Identifier Value response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 400,
        "response_code": "MISSING_IDENTIFIER_VALUE",
        "audit_msg": "The 'identifier' parameter is required",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Missing RelatedPerson NHS number.",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected MISSING_IDENTIFIER_VALUE, got {payload['error']}"


def assert_400_invalid_correlation_id(payload: dict) -> None:
    """Asserts the payload is a 400 Invalid Correlation ID response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 400,
        "response_code": "BAD_REQUEST",
        "audit_msg": "Invalid request with error - X-Correlation-ID header invalid",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Required header parameter(s) are invalid.",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected INVALID_CORRELATION_ID, got {payload['error']}"


def assert_400_invalid_request_id(payload: dict) -> None:
    """Asserts the payload is a 400 Invalid Request ID response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 400,
        "response_code": "BAD_REQUEST",
        "audit_msg": "Invalid request with error - X-Request-ID header invalid",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Required header parameter(s) are invalid.",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected INVALID_CORRELATION_ID, got {payload['error']}"


def assert_400_missing_identifier_value(payload: dict) -> None:
    """Asserts the payload is a 400 Missing Identifier Value response

    Args:
        payload (dict): The response payload
    """
    assert payload["error"] == {
        "http_status": 400,
        "response_code": "MISSING_IDENTIFIER_VALUE",
        "audit_msg": "The 'identifier' parameter is required",
        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
        "version": "1",
        "display": "Missing RelatedPerson NHS number.",
        "severity": "error",
        "issue_code": "invalid",
    }, f"Expected MISSING_IDENTIFIER_VALUE, got {payload['error']}"
