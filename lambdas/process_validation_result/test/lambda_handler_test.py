"""
Collection of tests for the process validation result lambda function.
"""

import json
import os
from http import HTTPStatus

import pytest
from fhirclient.models.bundle import Bundle
from fhirclient.models.identifier import Identifier
from fhirclient.models.operationoutcome import OperationOutcome
from pytest_mock import MockerFixture

from lambdas.process_validation_result.main import (
    ProcessValidationResult,
    lambda_handler,
)
from lambdas.utils.pds.errors import INTERNAL_SERVER_ERROR
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper


@pytest.fixture(name="fake_op_outcome")
def setup_fake_op_outcome():
    """Returns a fake outcome result"""

    return OperationOutcome()


@pytest.fixture(name="fake_bundle")
def setup_fake_bundle() -> Bundle:
    """Returns a fake outcome result"""

    return Bundle()


def test_handle_error_output_returns_expected_error_message(
    mocker: MockerFixture, fake_op_outcome
):
    """Test to confirm the handle_error_output function generates expected output"""

    expected_error = INTERNAL_SERVER_ERROR
    expected_json = "operational outcome as json"

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_json)
    mocker.patch.object(
        FHIRObjectMapper, "create_operation_outcome", return_value=fake_op_outcome
    )

    sut = ProcessValidationResult()
    sut.handle_error_output(expected_error)

    assert sut.response["statusCode"] == int(expected_error["http_status"])
    assert sut.response["body"] == expected_json


def test_handle_success_output_with_no_data_returns_expected_bundle_response(
    mocker: MockerFixture, fake_bundle
):
    """Test to confirm the handle_success_output function generates expected output"""
    expected_status = HTTPStatus.OK
    expected_json = {}

    mocker.patch.object(Bundle, "as_json", return_value=expected_json)
    mocker.patch.object(
        FHIRObjectMapper, "create_related_person_bundle", return_value=fake_bundle
    )
    proxy_identifier_dict = {"value": "identifier_value", "system": "identifier_system"}

    event = {
        "originalRequestUrl": "test-url",
        "proxyIdentifier": proxy_identifier_dict,
    }

    sut = ProcessValidationResult()
    sut.event = event
    sut.handle_success_output([], Identifier(proxy_identifier_dict))

    assert sut.response["statusCode"] == int(expected_status)
    assert sut.response["body"] == expected_json


def test_start_when_error_then_invokes_error_handler(mocker: MockerFixture):
    event = {"error": {"http_status": "500"}, "errorMessage": "some message"}
    expected_body = {}

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == int(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert sut.response["body"] == expected_body


def test_start__proxy_identifier_is_missing_then_internal_server_error_is_returned() -> (
    None
):
    patient = load_json(mock_proxy_file_sandpit_patient)
    related = load_related_person()
    event = {
        "pdsPatientRelationship": [{"pdsPatient": patient, "pdsRelationship": related}],
        "originalRequestUrl": "test-url",
    }

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"]["issue"][0]["code"] == "invalid"


@pytest.mark.parametrize("proxy_identifier", [None, {}, ""])
def test_start__proxy_identifier_empty_then_internal_server_error_is_returned(
    proxy_identifier,
) -> None:
    patient = load_json(mock_proxy_file_sandpit_patient)
    related = load_related_person()
    event = {
        "pdsPatientRelationship": [{"pdsPatient": patient, "pdsRelationship": related}],
        "originalRequestUrl": "test-url",
        "proxyIdentifier": proxy_identifier,
    }

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"]["issue"][0]["code"] == "invalid"


def test_start_when_relationship_data_present_then_bundle_is_returned(
    mocker: MockerFixture, fake_bundle
):
    """Test to confirm the start() function generates the expected bundle response"""

    patient = load_json(mock_proxy_file_sandpit_patient)
    related = load_related_person()
    event = {
        "pdsPatientRelationship": [{"pdsPatient": patient, "pdsRelationship": related}],
        "originalRequestUrl": "test-url",
        "proxyIdentifier": {"value": "identifier_value", "system": "identifier_system"},
    }
    expected_body = {}

    mocker.patch.object(Bundle, "as_json", return_value=expected_body)
    mocker.patch.object(
        FHIRObjectMapper, "create_related_person_bundle", return_value=fake_bundle
    )

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == int(HTTPStatus.OK)
    assert sut.response["body"] == expected_body


def test_start_when_relationship_data_present_check_bundle_length():
    """Test to confirm the start() function generates the expected bundle response"""

    patient = load_json(mock_proxy_file_sandpit_patient)
    related = load_related_person()
    identifier_value = "identifier_value"
    identifier_system = "identifier_system"
    event = {
        "pdsPatientRelationship": [
            {"pdsPatient": patient, "pdsRelationship": related},
            {},
        ],
        "originalRequestUrl": "test-url",
        "proxyIdentifier": {"value": identifier_value, "system": identifier_system},
    }

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == int(HTTPStatus.OK)
    assert len(sut.response["body"]["entry"]) == 1
    assert sut.response["body"]["entry"][0]["search"]["mode"] == "match"
    assert (
        sut.response["body"]["entry"][0]["resource"]["resourceType"] == "RelatedPerson"
    )
    assert sut.response["body"]["entry"][0]["resource"]["identifier"] == [
        {
            "value": identifier_value,
            "system": identifier_system,
        }
    ]


def test_start_when_include_flag_check_bundle_length() -> None:
    """
    Test Function : ProcessValidationResult.start
    Scenario: When '_include' parameter is supplied
    Expected Result: Includes patient information
    """

    patient = load_json(mock_proxy_file_sandpit_patient)
    related = load_related_person()
    identifier_value = "identifier_value"
    identifier_system = "identifier_system"
    event = {
        "pdsPatientRelationship": [{"pdsPatient": patient, "pdsRelationship": related}],
        "originalRequestUrl": "url",
        "_include": "RelatedPerson:patient",
        "proxyIdentifier": {"value": identifier_value, "system": identifier_system},
    }

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    patient = sut.response["body"]["entry"][0]
    related = sut.response["body"]["entry"][1]

    assert sut.response["statusCode"] == int(HTTPStatus.OK)
    assert len(sut.response["body"]["entry"]) == 2
    assert patient["resource"]["resourceType"] == "Patient"
    assert patient["search"]["mode"] == "include"
    assert related["resource"]["resourceType"] == "RelatedPerson"
    assert related["search"]["mode"] == "match"
    assert related["resource"]["identifier"] == [
        {
            "value": identifier_value,
            "system": identifier_system,
        }
    ]


def test_start_when_missing_args_then_error_is_returned(mocker: MockerFixture):
    """Test to confirm if no input are supplied then the start() returns error"""

    event = {}
    expected_body = {}

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"] == expected_body


def test_start_when_unable_to_process_input_then_server_error_is_returned(
    mocker: MockerFixture,
):
    """Test to confirm if values of the arguments are not processable then error is returned"""

    event = {
        "pdsPatientRelationship": [{"pdsPatient": "", "pdsRelationship": ""}],
        "originalRequestUrl": "test-url",
    }
    expected_body = {}

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"] == expected_body


def test_start_when_missing_request_url_then_server_error_is_returned(
    mocker: MockerFixture,
):
    """Test to confirm if request URL is missing then error is returned"""

    event = {"pdsPatientRelationship": [{"pdsPatient": "", "pdsRelationship": ""}]}
    expected_body = {}

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"] == expected_body


def test_start_when_request_url_is_empty_then_server_error_is_returned(
    mocker: MockerFixture,
):
    """Test to confirm if request URL is missing then error is returned"""

    event = {
        "pdsPatientRelationship": [{"pdsPatient": "", "pdsRelationship": ""}],
        "originalRequestUrl": "",
    }
    expected_body = {}

    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"] == expected_body


def test_start_when_exception_then_internal_error_is_returned(
    mocker: MockerFixture, fake_bundle
):
    """Test to confirm if an error occurs during processing then an error is returned"""

    event = {"pdsPatientRelationship": "", "originalRequestUrl": "test-url"}
    expected_body = {}
    mocker.patch.object(OperationOutcome, "as_json", return_value=expected_body)
    as_json = mocker.patch.object(Bundle, "as_json")
    as_json.side_effect = Exception("mock exception")

    sut = ProcessValidationResult()
    sut.event = event
    sut.start()

    assert sut.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert sut.response["body"] == expected_body


def test_lambda_handler_invokes_main_function(mocker: MockerFixture):
    """Test to ensure lambda handler is call the correct underlying function"""

    # Arrange
    invocation = mocker.patch.object(ProcessValidationResult, "main")
    event_args = {"someKey": "someValue"}
    context_args = {"someContextKey": "someContextValue"}

    # Act
    lambda_handler(event_args, context_args)

    # Assert
    assert invocation.call_count == 1
    args = invocation.call_args
    assert args[0][0] == event_args
    assert args[0][1] == context_args


def load_related_person() -> dict:
    """Loads a related person from file"""
    related = load_json(mock_proxy_file_sandpit_two_related_person)
    related = related[0]
    return related


def load_json(file_path: str) -> dict:
    """
    reads the contents of a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The json contents of the file as a Python dictionary.
    """
    with open(file_path, "r") as file:
        return json.load(file)


mock_proxy_file_sandpit_patient = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../utils/pds/sample_data/patient_details/sample_sandpit_patient.json",
)

mock_proxy_file_sandpit_two_related_person = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../utils/pds/sample_data/related_person/sample_sandpit_two_related_person.json",
)
