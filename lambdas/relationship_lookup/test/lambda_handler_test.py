"""
Collection of tests for the Relationship lambda function.
"""

import json as JSONReader
import os
from http import HTTPStatus

import pytest
from fhirclient.server import FHIRNotFoundException
from pytest_mock import MockerFixture
from requests import Session

import lambdas.utils.pds.errors as err
from lambdas.relationship_lookup.main import RelationshipLookup, lambda_handler


@pytest.fixture(name="lambda_instance")
def setup_lambda_test_instance(monkeypatch):
    monkeypatch.setenv("PDS_BASE_URL", "http://someurl.com")
    """Create and return an instance of the Lambda Function Class"""
    lambda_instance = RelationshipLookup()
    lambda_instance.initialise()
    return lambda_instance


def test_token_is_added_to_request(mocker: MockerFixture):
    """Confirm that a validtion token is added to the request to the server"""

    # Arrange
    sut = RelationshipLookup()
    sut.SETTINGS["api_base"] = "http://someurl.com"

    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.OK)
    mocked_get = mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "value"
    expected_header = "Bearer " + fake_bearer

    # Act
    sut.retrieve_relationship(nhs_number, fake_bearer)

    # Assert
    my_args = mocked_get.call_args
    actual_headers = my_args[1]["headers"]
    assert actual_headers["Authorization"] == expected_header


def test_retrieves_related_person_when_requested(mocker: MockerFixture):
    """Test to confirm expected data is returned"""

    # Arrange
    sut = RelationshipLookup()

    fake_resp = helper_fake_resp_with_json(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "90000000009"
    fake_bearer = "value"

    # Act
    actual = sut.retrieve_relationship(nhs_number, fake_bearer)

    # Assert
    assert len(actual) == 2
    assert actual[0]["patient"]["identifier"]["value"] == nhs_number


def test_error_raised_when_record_not_found(mocker: MockerFixture):
    """Confirm an error is raised when record cannot be found"""

    # Arrange
    sut = RelationshipLookup()

    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.NOT_FOUND)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "value"

    # Act
    # Assert
    with pytest.raises(FHIRNotFoundException):
        sut.retrieve_relationship(nhs_number, fake_bearer)


def test_empty_result_returned_when_record_has_no_relationships(mocker: MockerFixture):
    """Test to check a empty result is returned"""

    # Arrange
    sut = RelationshipLookup()

    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "value"

    # Act
    actual = sut.retrieve_relationship(nhs_number, fake_bearer)

    # Assert
    assert len(actual) == 0


def test_retrieve_related_person_when_using_lambda(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check if a related person result is returned through the lambda"""

    # Arrange
    fake_resp = helper_fake_resp_with_json(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "fakebearertoken"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.OK
    assert len(lambda_instance.response["body"]["pdsRelationshipRecord"]) == 2
    assert lambda_instance.response["body"]["error"] is None


def test_error_raised_on_record_not_found_when_using_lambda(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check a non found result is returned through the lambda"""

    # Arrange
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.NOT_FOUND)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "fakebearertoken"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.NOT_FOUND
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_RECORD_NOT_FOUND


def test_error_raised_on_record_has_no_relationships_when_using_lambda(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check if an empty result is returned through the lambda"""

    # Arrange
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "fakebearertoken"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.OK
    assert len(lambda_instance.response["body"]["pdsRelationshipRecord"]) == 0
    assert lambda_instance.response["body"]["error"] is None


def test_error_raised_on_missing_nhsnumber_parameter_when_using_lambda(
    lambda_instance: RelationshipLookup,
):
    """Test to check if an error is returned through the lambda when the NHS Number is missing"""

    # Arrange
    fake_bearer = "value"

    lambda_instance.event = {"authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_NHS_NUMBER_REQUIRED


def test_error_raised_on_missing_bearertoken_parameter_when_using_lambda(
    lambda_instance: RelationshipLookup,
):
    """Test to check if an error is returned through the lambda when the bearer token is missing"""

    # Arrange
    nhs_number = "9000000009"

    lambda_instance.event = {"nhsNumber": nhs_number}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_AUTH_TKN_REQUIRED


def test_error_raised_when_using_lambda_and_nhsnumber_is_not_valid(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check if an error is returned through the lambda when the NHS Number is missing"""

    # Arrange
    nhs_number = "9000000000"
    fake_bearer = "value"
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.UNAUTHORIZED)
    fake_request = mocker.patch.object(Session, "get", return_value=fake_resp)

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_NHS_NUMBER_INVALID
    assert fake_request.call_count == 0  # Should never be invoked


def test_token_is_empty_then_bad_request_is_returned(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check if an empty token returns an error"""

    # Arrange
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = None

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_AUTH_TKN_INVALID


def test_token_is_too_short_then_bad_request_is_returned(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check if an invalid token length returns an error"""

    # Arrange
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.OK)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "shorttkn"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_AUTH_TKN_INVALID


def test_lambda_handler_invokes_main_method(mocker: MockerFixture):
    """Test to ensure lambda handler is call the correct underlying function"""

    # Arrange
    invocation = mocker.patch.object(RelationshipLookup, "main", return_value=None)
    event_args = {"somekey": "somevalue"}
    context_args = {"somecontxtkey": "somecontextvalue"}

    # Act
    lambda_handler(event_args, context_args)

    # Assert
    assert invocation.call_count == 1
    args = invocation.call_args
    assert args[0][0] == event_args
    assert args[0][1] == context_args


def test_error_response_when_unauthorised_result_returned_in_lamdba(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check a non found result is returned through the lambda"""

    # Arrange
    fake_resp = helper_fake_resp_empty(mocker, HTTPStatus.UNAUTHORIZED)
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "fakebearertoken"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.UNAUTHORIZED
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_UNAUTHORIZED


def test_error_response_when_unhandled_error_result_returned_in_lamdba(
    lambda_instance: RelationshipLookup, mocker: MockerFixture
):
    """Test to check an error is raised when operation fails"""

    # Arrange
    error = HTTPStatus.INTERNAL_SERVER_ERROR
    fake_resp = mocker.Mock()
    json = None
    fake_resp.json = mocker.Mock(return_value=json)
    fake_resp.status_code = error
    mocker.patch.object(Session, "get", return_value=fake_resp)

    nhs_number = "9000000009"
    fake_bearer = "fakebearertoken"

    lambda_instance.event = {"nhsNumber": nhs_number, "authToken": fake_bearer}

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == error
    assert lambda_instance.response["body"]["pdsRelationshipRecord"] is None
    assert lambda_instance.response["body"]["error"] == err.ERROR_OPERATION_FAILED


# Helper functions
def helper_fake_resp_empty(mocker: MockerFixture, status_code: int):
    """Helper function that mocks an empty response"""

    fake_resp = mocker.Mock()
    json = {"resourceType": "Bundle", "type": "searchset", "total": 0}
    fake_resp.json = mocker.Mock(return_value=json)
    fake_resp.status_code = status_code
    return fake_resp


def helper_fake_resp_with_json(mocker: MockerFixture, status_code: int):
    """Helper function that mocks a relationship response"""

    fake_resp = mocker.Mock()
    path = os.path.dirname(os.path.realpath(__file__)) + "/sample-relationship.json"
    with open(path, "r", encoding="UTF-8") as file:
        json = JSONReader.load(file)
        file.close()

    fake_resp.json = mocker.Mock(return_value=json)
    fake_resp.status_code = status_code
    return fake_resp
