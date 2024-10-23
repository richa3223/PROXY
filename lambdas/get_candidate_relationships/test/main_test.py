from json import dumps
from os import environ
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from lambdas.get_candidate_relationships.main import GetCandidateRelationships, errors
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper

FILE_PATH = "lambdas.get_candidate_relationships.main"

# NHS number constants
STANDARD_NHS_NUMBER = "9730675929"
NHS_NUMBER_09 = "9000000009"
NHS_NUMBER_17 = "9000000017"


@pytest.fixture(name="sut")
def create_sut() -> GetCandidateRelationships:
    """Returns an instance of the sut"""
    return GetCandidateRelationships()


@pytest.fixture(name="event")
def create_event() -> dict:
    """Returns a valid event data"""
    return {
        GetCandidateRelationships.PARAM_HEADER_AUTH_LEVEL: GetCandidateRelationships.P9_LEVEL,
        GetCandidateRelationships.PARAM_HEADER_NHS_NO: NHS_NUMBER_17,
        GetCandidateRelationships.PARAM_PROXY_NHS_NO: NHS_NUMBER_17,
        GetCandidateRelationships.PARAM_PATIENT_NHS_NO: NHS_NUMBER_09,
        GetCandidateRelationships.PARAM_HEADER_ORIGINAL_URL: "test-url",
        GetCandidateRelationships.PARAM_HEADER_CORRELATION_ID: str(uuid4()),
        GetCandidateRelationships.PARAM_HEADER_REQUEST_ID: str(uuid4()),
        GetCandidateRelationships.PARAM_INCLUDE: "test-include",
    }.copy()


INTERNAL_SERVER_ERROR = {
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
}

FORBIDDEN = {
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
}

INSUFFICIENT_AUTH_LEVEL = {
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
}


def test_start_when_header_p_level_missing_then_returns_error(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.start
    When p level is missing
    Expected Result: internal server error is returned
    """
    # Arrange
    event.pop(GetCandidateRelationships.PARAM_HEADER_AUTH_LEVEL)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == {"status_code": 500, "body": INTERNAL_SERVER_ERROR}


def test_start_when_header_p_level_invalid_then_returns_error(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.start
    When p level is not valid
    Expected Result: p level error is returned
    """
    # Arrange
    event[GetCandidateRelationships.PARAM_HEADER_AUTH_LEVEL] = "P0"
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == {"status_code": 401, "body": INSUFFICIENT_AUTH_LEVEL}


def test_start_when_header_nhs_number_missing_then_returns_error(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.start
    When headers nhs number is missing
    Expected Result: internal server error is returned
    """
    # Arrange
    event.pop(GetCandidateRelationships.PARAM_HEADER_NHS_NO)
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == {"status_code": 500, "body": INTERNAL_SERVER_ERROR}


def test_start_when_header_nhs_number_mismatch_then_returns_error(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.start
    When headers nhs number does not match proxy nhs number
    Expected Result: nhs number error is returned
    """
    # Arrange
    event[GetCandidateRelationships.PARAM_HEADER_NHS_NO] = NHS_NUMBER_09
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response == {"status_code": 403, "body": FORBIDDEN}


@patch.object(
    GetCandidateRelationships, "_GetCandidateRelationships__get_step_function_inputs"
)
@patch(f"{FILE_PATH}.client")
def test__trigger_validate_relationship(
    mock_client: MagicMock,
    mock__get_step_function_inputs: MagicMock,
    sut: GetCandidateRelationships,
    event: dict,
) -> None:
    """
    Test Function: GetCandidateRelationships.__trigger_validate_relationship
    When called
    Expected Result: returns a dictionary
    """
    # Arrange
    mock__get_step_function_inputs.return_value = test_data = {"test": "data"}
    environ["VALIDATE_RELATIONSHIPS_STATE_MACHINE_ARN"] = state_machine_arn = "test-arn"
    sut.event = event
    # Act
    response = sut._GetCandidateRelationships__trigger_validate_relationship()
    # Assert
    mock_client.assert_called_once_with("stepfunctions")
    mock_client.return_value.start_sync_execution.assert_called_once_with(
        stateMachineArn=state_machine_arn, input=test_data
    )
    assert response == mock_client.return_value.start_sync_execution.return_value


def test__get_step_function_inputs(sut: GetCandidateRelationships, event: dict) -> None:
    """
    Test Function: GetCandidateRelationships.__get_step_function_inputs
    When called
    Expected Result: returns a string
    """
    # Arrange
    sut.event = event
    sut.correlation_id = event[GetCandidateRelationships.PARAM_HEADER_CORRELATION_ID]
    # Act
    response = sut._GetCandidateRelationships__get_step_function_inputs()
    # Assert
    assert response == dumps(
        {
            "proxyNhsNumber": event[GetCandidateRelationships.PARAM_PROXY_NHS_NO],
            "patientNhsNumber": event[GetCandidateRelationships.PARAM_PATIENT_NHS_NO],
            "_include": event[GetCandidateRelationships.PARAM_INCLUDE],
            "correlationId": event[
                GetCandidateRelationships.PARAM_HEADER_CORRELATION_ID
            ],
            "requestId": event[GetCandidateRelationships.PARAM_HEADER_REQUEST_ID],
            "originalRequestUrl": event[
                GetCandidateRelationships.PARAM_HEADER_ORIGINAL_URL
            ],
        }
    )


def test___handle_step_function_response_when_failed(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.__handle_step_function_response
    When response is failed
    Expected Result: returns an error
    """
    # Arrange
    response = {"status": "FAILED"}
    sut.event = event
    # Act
    sut._GetCandidateRelationships__handle_step_function_response(response)
    # Assert
    assert sut.response == {"status_code": 500, "body": INTERNAL_SERVER_ERROR}


def test___handle_step_function_response_when_timed_out(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.__handle_step_function_response
    When response is timed out
    Expected Result: returns an error
    """
    # Arrange
    response = {"status": "TIMED_OUT"}
    sut.event = event
    # Act
    sut._GetCandidateRelationships__handle_step_function_response(response)
    # Assert
    assert sut.response == {"status_code": 500, "body": INTERNAL_SERVER_ERROR}


def test___handle_step_function_response_when_successful(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.__handle_step_function_response
    When response is successful
    Expected Result: returns a dictionary
    """
    # Arrange
    response = {
        "status": "SUCCESS",
        "output": dumps(
            {
                "statusCode": 200,
                "body": {"test": "data"},
            }
        ),
    }
    sut.event = event
    # Act
    sut._GetCandidateRelationships__handle_step_function_response(response)
    # Assert
    assert sut.response == {"status_code": 200, "body": {"test": "data"}}


def test___handle_step_function_response_when_not_successful(
    sut: GetCandidateRelationships, event: dict
) -> None:
    """
    Test Function: GetCandidateRelationships.__handle_step_function_response
    When response is not successful
    Expected Result: returns an error
    """
    operational_outcome = (
        FHIRObjectMapper()
        .create_operation_outcome(errors.INVALID_IDENTIFIER_VALUE)
        .as_json()
    )
    # Arrange
    response = {
        "status": "SUCCESS",
        "output": dumps({"statusCode": 400, "body": operational_outcome}),
    }
    sut.event = event
    # Act
    sut._GetCandidateRelationships__handle_step_function_response(response)
    # Assert
    assert sut.response == {"status_code": 400, "body": operational_outcome}
