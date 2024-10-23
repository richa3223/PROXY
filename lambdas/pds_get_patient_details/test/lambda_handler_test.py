""" Unit tests for the 'PdsGetPatientDetails' Lambda Function """

import json as JSONReader
import os
from http import HTTPStatus

import pytest
from requests import Session

import lambdas.utils.pds.errors as err
from lambdas.pds_get_patient_details.main import PdsGetPatientDetails


@pytest.fixture(name="lambda_instance")
def setup_lambda_test_instance(monkeypatch):
    monkeypatch.setenv("PDS_BASE_URL", "http://someurl.com")
    """Create and return an instance of the Lambda Function Class"""
    lambda_instance = PdsGetPatientDetails()
    lambda_instance.initialise()
    return lambda_instance


def test_handle_success_correct_response(lambda_instance):
    """ "Test handle_success method for success case"""

    # Arrange
    data = {"some": "patient_data"}

    # Act
    lambda_instance.handle_success(data)
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 200
    assert response["body"]["pdsPatientRecord"] == data
    assert response["body"]["error"] is None


def test_handle_error_correct_response(lambda_instance):
    """Test handle_error method for an error case"""

    # Arrange
    status_code = 400
    error_message = "Bad Request"

    # Act
    lambda_instance.handle_error(status_code, error_message)
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == status_code
    assert response["body"]["pdsPatientRecord"] is None
    assert response["body"]["error"] == error_message


def test_missing_auth_token_event_value(lambda_instance):
    """Test that the Lambda function returns an error when the access token is not provided"""

    # Act
    lambda_instance.event = {"nhsNumber": "9000000009"}
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 400
    assert response["body"]["error"] == err.ERROR_AUTH_TKN_REQUIRED


def test_missing_nhs_number_event_value(lambda_instance):
    """Test that the Lambda function returns an error when the NHS Number is not provided"""

    # Act
    lambda_instance.event = {"authToken": "mock-access-token-abc-123"}
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 400
    assert response["body"]["error"] == err.ERROR_NHS_NUMBER_REQUIRED


def test_null_token_returns_error(lambda_instance):
    """Test that the Lambda function returns an error when the token value is None"""

    # Act
    lambda_instance.event = {"authToken": None, "nhsNumber": "9000000009"}
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 400
    assert response["body"]["error"] == err.ERROR_AUTH_TKN_INVALID


def test_short_token_return_error(lambda_instance):
    """Test that the Lambda function returns an error when the NHS Number is not provided"""

    # Act
    lambda_instance.event = {"authToken": "shorttkn", "nhsNumber": "9000000009"}
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 400
    assert response["body"]["error"] == err.ERROR_AUTH_TKN_INVALID


def test_invalid_nhs_number_provided_error(lambda_instance):
    """Test that the Lambda function returns an error when an invalid NHS Number is provided"""

    # Act
    lambda_instance.event = {
        "authToken": "mock-access-token-abc-123",
        "nhsNumber": "abcd1234",
    }
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 400
    assert response["body"]["error"] == err.ERROR_NHS_NUMBER_INVALID


def test_retrieves_patient_valid_check(lambda_instance, mocker):
    """Test that the Lambda function returns correct status and data on valid API"""

    # Arrange
    nhs_number = "9000000009"
    fake_resp = helper_fake_resp_with_json(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    # Act
    lambda_instance.event = {
        "nhsNumber": nhs_number,
        "authToken": "mock-access-token-abc-123",
    }
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 200
    assert response["body"]["pdsPatientRecord"]["id"] == nhs_number


def test_retrieves_patient_error_401(lambda_instance, mocker):
    """Test that the Lambda function returns correct status from the API"""

    # Arrange
    nhs_number = "9000000009"
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.UNAUTHORIZED)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    # Act
    lambda_instance.event = {
        "nhsNumber": nhs_number,
        "authToken": "mock-access-token-abc-123",
    }
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 401
    assert response["body"]["pdsPatientRecord"] is None


def test_retrieves_patient_error_404(lambda_instance, mocker):
    """Test that the Lambda function returns correct status from the API"""

    # Arrange
    nhs_number = "9000000009"
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.NOT_FOUND)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    # Act
    lambda_instance.event = {
        "nhsNumber": nhs_number,
        "authToken": "mock-access-token-abc-123",
    }
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 404
    assert response["body"]["pdsPatientRecord"] is None
    assert response["body"]["error"] == err.ERROR_RECORD_NOT_FOUND


def test_retrieves_patient_error_too_many_requests(lambda_instance, mocker):
    """Test that the Lambda function returns correct status for all other errors"""

    # Arrange
    nhs_number = "9000000009"
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.TOO_MANY_REQUESTS)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    # Act
    lambda_instance.event = {
        "nhsNumber": nhs_number,
        "authToken": "mock-access-token-abc-123",
    }
    lambda_instance.start()
    response = lambda_instance.response

    # Assert
    assert response["statusCode"] == 500
    assert response["body"]["pdsPatientRecord"] is None


# Helper functions
def helper_fake_resp_empty(mocker, status_code):
    """Helper function that mocks an empty response"""

    fake_resp = mocker.Mock()
    json = {"resourceType": "OperationOutcome"}
    fake_resp.json = mocker.Mock(return_value=json)
    fake_resp.status_code = status_code
    return fake_resp


def helper_fake_resp_with_json(mocker, status_code):
    """Helper function that mocks a patient API response"""
    fake_resp = mocker.Mock()
    path = os.path.dirname(os.path.realpath(__file__)) + "/sample-patient.json"
    json = load_json_contents(path)

    fake_resp.json = mocker.Mock(return_value=json)
    fake_resp.status_code = status_code
    return fake_resp


def load_json_contents(filepath: str) -> any:
    """Returns the contents of the given file as json"""
    with open(filepath, "r", encoding="UTF-8") as file:
        json = JSONReader.load(file)
        file.close()
        return json
