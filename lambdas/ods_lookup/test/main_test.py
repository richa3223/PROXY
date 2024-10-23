"""
Collection of tests for the ods_lookup lambda function
"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from requests import Response
from requests.exceptions import HTTPError, Timeout

from lambdas.ods_lookup.main import ODSLookup, lambda_handler

FILE_PATH = "lambdas.ods_lookup.main"


@pytest.fixture(name="fake_secret")
def setup_fake_secret(mocker: MockerFixture):
    """Create and return a fake SecretManager.get_secret"""
    return mocker.patch(
        "lambdas.utils.aws.secret_manager.SecretManager.get_secret", return_value=""
    )


@pytest.fixture(name="fake_get")
def setup_fake_get(mocker: MockerFixture):
    """Create and return an fake requests.get"""
    return mocker.patch(f"{FILE_PATH}.get", return_value="")


def test_odslookup_when_parameter_missing_returns_error() -> None:
    """
    Test Function : main.start
    Scenario: When start function is called without args
    Expected Result: A unhandled exception is raised
    """
    # Arrange
    ods = ODSLookup()
    ods.event = {}

    # Act
    with pytest.raises(ValueError, match="ods_code is required"):
        ods.start()


def test_odslookup_when_parameter_is_empty_returns_error() -> None:
    """
    Test Function : main.start
    Scenario: When start function is called without args
    Expected Result: A unhandled exception is raised
    """
    # Arrange
    ods = ODSLookup()
    ods.event = {"ods_code": ""}

    # Act
    with pytest.raises(ValueError, match="ods_code is required"):
        ods.start()


def test_odslookup_when_secrets_lookup_fails_returns_error(
    fake_secret: MagicMock, fake_get: MagicMock
) -> None:
    """
    Test Function : main.start
    Scenario: When start function is called without args
    Expected Result: Then TypeError is returned
    """
    # Arrange
    error_message = "Failed to get 200 response from remote."
    fake_secret.side_effect = TypeError(error_message)
    ods = ODSLookup()
    ods.event = {"ods_code": "Test"}

    # Act & Assert
    with pytest.raises(TypeError, match=error_message):
        ods.start()
    fake_get.assert_not_called()


@pytest.mark.parametrize(
    "error, error_type",
    [
        (Exception("Test"), Exception),
        (Timeout(), Timeout),
        (HTTPError(), HTTPError),
        (ConnectionError(), ConnectionError),
    ],
)
def test_odslookup_when_api_returns_error(
    error: Exception, error_type: Exception, fake_secret: MagicMock, fake_get: MagicMock
) -> None:
    """
    Test Function : main.start
    Scenario: When request to api times out
    Expected Result: Then error is returned
    """
    # Arrange
    fake_get.side_effect = error
    ods = ODSLookup()
    ods.event = {"ods_code": "Test"}

    # Act
    with pytest.raises(error_type):
        ods.start()

    # Assert
    fake_secret.assert_called_once()


@pytest.mark.parametrize("status_code", [400, 404, 429, 500])
def test_odslookup_when_not_successful_response(
    status_code: Response, fake_secret: MagicMock, fake_get: MagicMock
) -> None:
    """
    Test Function : main.start
    Scenario: When request results in a 404
    Expected Result: Then 404 - not found is returned
    """
    # Arrange
    response = MagicMock(spec=Response)
    response.status_code = status_code
    fake_resp = response
    fake_get.return_value = fake_resp
    ods = ODSLookup()
    ods.event = {"ods_code": "Test"}
    # Act
    with pytest.raises(HTTPError, match="Failed to get 200 response from remote."):
        ods.start()
    # Assert
    fake_secret.assert_called_once()


def test_odslookup_when_not_successful_response(
    fake_secret: MagicMock, fake_get: MagicMock
) -> None:
    """
    Test Function : main.start
    Scenario: When request results in a 404
    Expected Result: Then 404 - not found is returned
    """
    # Arrange
    response = Response()
    response.status_code = 200
    response._content = bytes(
        '{"email": "test@test.com:test2@test.com:test3@test.com"}', encoding="utf8"
    )
    fake_get.return_value = response
    ods = ODSLookup()
    ods.event = {"ods_code": "Test"}
    # Act
    ods.start()
    # Assert
    assert ods.response == {
        "L": [
            {"S": "test@test.com"},
            {"S": "test2@test.com"},
            {"S": "test3@test.com"},
        ]
    }
    fake_secret.assert_called_once()


def test_lambda_handler_calls_odslookup(mocker: MockerFixture) -> None:
    """
    Test Function : lambda_handler
    Scenario: When function is invoked
    Expected Result: Then odslookup.start is called
    """
    # Arrange
    event = {"some": "event"}
    context = {"some": "context"}
    mock = mocker.patch.object(ODSLookup, "main", return_value={"some": "resp"})

    # Act
    lambda_handler(event, context)

    # Assert
    mock.assert_called_with(event, context)
