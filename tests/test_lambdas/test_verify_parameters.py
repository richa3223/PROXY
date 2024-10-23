"""
Test the verify parameters Lambda
"""

from ..helpers import WORKSPACE, helpers
from ..helpers.assertions.verify_parameters import (
    assert_400_invalid_correlation_id,
    assert_400_invalid_request_id,
    assert_400_missing_identifier_value,
    assert_400_x_request_id_not_found_error,
    assert_500_internal_server_error,
    assert_success,
)

FUNCTION_NAME = f"{WORKSPACE}-verify_parameters"


def test_expected_input(helpers: helpers) -> None:
    """
    Test expected input returns 200
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_success(payload, test_data)


def test_missing_proxy_nhs_number(helpers: helpers) -> None:
    """
    Test missing proxy nhs number returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["proxyNhsNumber"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_missing_identifier_value(payload)


def test_missing_patient_nhs_number(helpers: helpers) -> None:
    """
    Test missing patient nhs number returns success
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["patientNhsNumber"]

    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    expected_response = test_data
    expected_response["patientNhsNumber"] = None
    assert_success(payload, expected_response)


def test_missing__include(helpers: helpers) -> None:
    """
    Test missing _include returns success
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["_include"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    expected_response = test_data
    expected_response["_include"] = ""
    assert_success(payload, test_data)


def test_missing_original_request_url(helpers: helpers) -> None:
    """
    Test missing original_request_url returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["originalRequestUrl"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_500_internal_server_error(payload)


def test_empty_proxy_nhs_number(helpers: helpers) -> None:
    """
    Test empty proxy nhs number returns 400 missing identifier value
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["accesstoken.auth_user_id"] = ""
    test_data["proxyNhsNumber"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_missing_identifier_value(payload)


def test_empty_patient_nhs_number(helpers: helpers) -> None:
    """
    Test empty patient nhs number returns success
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["patientNhsNumber"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_success(payload, test_data)


def test_empty__include(helpers: helpers) -> None:
    """
    Test empty _include returns success
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["_include"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_success(payload, test_data)


def test_missing_request_id(helpers: helpers) -> None:
    """
    Test missing request_id returns 400
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["requestId"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_x_request_id_not_found_error(payload)


def test_missing_correlation_id(helpers: helpers) -> None:
    """
    Test missing correlation_id returns success, also generates a new correlation_id
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["correlationId"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    expected_response = test_data
    del expected_response["correlationId"]
    correlation_id = payload["correlationId"]
    del payload["correlationId"]
    assert_success(payload, expected_response)
    assert isinstance(correlation_id, str)
    assert len(correlation_id) == 36


def test_empty_original_request_url(helpers: helpers) -> None:
    """
    Test empty original_request_url returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["originalRequestUrl"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_500_internal_server_error(payload)


def test_missing_proxy_and_patient_nhs_number(helpers: helpers) -> None:
    """
    Test missing proxy and patient nhs number returns 400
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["accesstoken.auth_user_id"] = ""
    test_data["proxyNhsNumber"] = ""
    test_data["patientNhsNumber"] = ""
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_missing_identifier_value(payload)


def test_invalid_request_id(helpers: helpers) -> None:
    """
    Test invalid requestId returns 400
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["requestId"] = "invalid"
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_invalid_request_id(payload)


def test_invalid_correlation_id(helpers: helpers) -> None:
    """
    Test invalid correlationId returns 400
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["correlationId"] = "invalid"
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_400_invalid_correlation_id(payload)
