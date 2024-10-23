"""
Test get ODS Lookup
"""

import pytest

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-ods_lookup"


@pytest.mark.parametrize(
    "ods_code,expected_response",
    [("A20047", {"L": [{"S": "dev.proxyaccess.gp1@mailinator.com"}]})],
)
def test_valid_ods_code(
    ods_code: str, expected_response: dict, helpers: Helpers
) -> None:
    """
    Confirm we can retrieve ODS lookup details
    """
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {"ods_code": ods_code})
    # Assert
    assert payload == expected_response, f"Expected {expected_response}, got {payload}"


@pytest.mark.parametrize("request_payload", [{"ods_code": ""}, {}])
def test_invalid_request(request_payload: dict, helpers: Helpers) -> None:
    """
    Confirm an empty request returns error
    """
    # Act
    response, payload = helpers.invoke_lambda_function_with_response(
        FUNCTION_NAME, request_payload
    )
    # Assert
    assert response["StatusCode"] == 200, f"Expected 200, got {response['StatusCode']}"
    assert (
        payload["errorType"] == "ValueError"
    ), f"Expected ValueError, got {payload['errorType']}"
    assert (
        payload["errorMessage"] == "ods_code is required"
    ), f"Expected 'ods_code is required', got {payload['errorMessage']}"


@pytest.mark.parametrize(
    "request_payload", [{"ods_code": "blah"}, {"ods_code": "FXXX1"}]
)
def test_invalid_ods_code(request_payload: dict, helpers: Helpers) -> None:
    """
    Confirm an invalid ODS code returns error
    """
    # Act
    response, payload = helpers.invoke_lambda_function_with_response(
        FUNCTION_NAME, request_payload
    )
    # Assert
    assert response["StatusCode"] == 200, f"Expected 200, got {response['StatusCode']}"
    assert (
        payload["errorType"] == "HTTPError"
    ), f"Expected ValueError, got {payload['errorType']}"
    assert (
        payload["errorMessage"] == "Failed to get 200 response from remote."
    ), f"Expected 'ods_code is required', got {payload['errorMessage']}"
