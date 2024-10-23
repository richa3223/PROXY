"""
Test get candidate relationships Lambda
"""

import pytest

from ..helpers import WORKSPACE, helpers
from ..helpers.assertions.generic import assert_500_internal_server_error
from ..helpers.assertions.get_candidate_relationships import (
    assert_401_insufficient_authorisation,
    assert_403_forbidden,
)

FUNCTION_NAME = f"{WORKSPACE}-get_candidate_relationships"


@pytest.mark.pds_api_call
def test_expected_input(helpers: helpers) -> None:
    """
    Test expected input returns 200
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/get_candidate_relationships/success_input.json"
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert payload["status_code"] == 200
    assert isinstance(payload["body"], dict)


def test_missing_accesstoken_auth_user_id(helpers: helpers) -> None:
    """
    Test missing accesstoken_auth_user_id returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["accesstoken.auth_user_id"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_500_internal_server_error(payload)


def test_missing_accesstoken_auth_level(helpers: helpers) -> None:
    """
    Test missing accesstoken_auth_level returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["accesstoken.auth_level"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_500_internal_server_error(payload)


def test_missing_accesstoken_auth_user_id(helpers: helpers) -> None:
    """
    Test missing accesstoken_auth_user_id returns 500
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    del test_data["accesstoken.auth_user_id"]
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_500_internal_server_error(payload)


def test_auth_not_p9(helpers: helpers) -> None:
    """
    Test auth not p9 returns 401
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["accesstoken.auth_level"] = "P8"
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_401_insufficient_authorisation(payload)


def test_auth_id_mismatch_request_id(helpers: helpers) -> None:
    """
    Test auth id mismatch request id returns 403
    """
    # Arrange
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/verify_parameters/success_input.json"
    )
    test_data["accesstoken.auth_user_id"] = "9000000025"
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    # Assert
    assert_403_forbidden(payload)
