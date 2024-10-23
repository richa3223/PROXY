"""
Collection of tests for the validate relationship lambda function.
"""

import json
import os
from http import HTTPStatus
from typing import List

import pytest
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson
from pytest_mock import MockerFixture

from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher
from lambdas.utils.pds import pdsdata
from lambdas.utils.validation import codes
from lambdas.validate_relationship.main import ValidateRelationship, lambda_handler


@pytest.fixture(name="patient")
def load_patient_record() -> Patient:
    """Returns a fake patient result"""
    return Patient(load_mock_record(patient_file))


@pytest.fixture(name="related")
def load_related_person_record() -> List[RelatedPerson]:
    """Returns a fake RelatedPerson result"""
    json_record = load_mock_record(relationship_file)
    rtn = []
    for record in json_record:
        rtn.append(RelatedPerson(record))

    return rtn


# Reference to a json file with patient information
patient_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../utils/pds/sample_data/patient_details/sample_sandpit_patient.json",
)

# Reference to a json file with relationship information
relationship_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../utils/pds/sample_data/related_person/sample_sandpit_two_related_person.json",
)


def test_is_eligible_when_patient_deceased_returns_fail(
    patient: Patient, related: List[RelatedPerson], mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: When patient is marked as deceased
    Expected Result: Deceased result is returned
    """
    # Arrange
    proxy_nhs_number = "9000000009"
    expected = (codes.PATIENT_DECEASED, "")
    patch_pds_data(mocker)

    # Return false from deceased lookup
    mocker.patch.object(pdsdata, "get_is_person_deceased", return_value=True)

    sut = ValidateRelationship(None)

    # Act
    actual = sut.is_eligible(proxy_nhs_number, patient, related)

    # Assert
    assert actual == expected


def test_is_eligible_when_patient_is_not_unrestricted_returns_fail(
    patient: Patient,
    related: List[RelatedPerson],
    mocker: MockerFixture,
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: When restricted flag is present on patient
    Expected Result: Patient consent result is returned
    """
    # Arrange
    proxy_nhs_number = "9000000009"
    expected = (codes.NO_PATIENT_CONSENT, "")

    patch_pds_data(mocker)

    # Return "S" - Sensitive
    mocker.patch.object(pdsdata, "get_security_code", return_value="S")

    sut = ValidateRelationship(None)

    # Act
    actual = sut.is_eligible(proxy_nhs_number, patient, related)

    # Assert
    assert actual == expected


@pytest.mark.parametrize(
    "age",
    [pytest.param(13), pytest.param(14), pytest.param(100)],
)
def test_is_eligible_when_age_check_fails_then_age_error_returned(
    patient: Patient, related: RelatedPerson, age, mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: Whe patient is same age or older than age requirement
    Expected Result: Patient not found dictionary
    """
    # Arrange
    expected = (codes.PATIENT_NOT_ELIGIBLE_OVER_13, "")
    mother_nhs_no = "9000000009"
    patch_pds_data(mocker)

    # Overwrite patient age check to return expected value
    mocker.patch.object(pdsdata, "get_patient_age", return_value=age)

    sut = ValidateRelationship()

    # Act
    actual = sut.is_eligible(mother_nhs_no, patient, related)

    # Assert
    assert actual == expected


def test_is_eligible_when_patient_not_related_then_error_returned(
    patient: Patient,
    related: List[RelatedPerson],
    mocker: MockerFixture,
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: When proxy is not related
    Expected Result: Not related result
    """
    # Arrange
    expected = (codes.PATIENT_NOT_RELATED, "")
    mother_nhs_no = "9000000009"
    patch_pds_data(mocker)

    # Overwrite with relationship failed
    mocker.patch.object(pdsdata, "get_relationship", return_value="Sister")

    sut = ValidateRelationship()

    # Act
    actual = sut.is_eligible(mother_nhs_no, patient, related)

    # Assert
    assert actual == expected


def test_is_eligible_when_patient_nhsno_does_not_match_related_then_error(
    patient: Patient,
    related: List[RelatedPerson],
    mocker: MockerFixture,
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: When patient and related person nhs number does not match
    Expected Result: Not related result
    """
    # Arrange
    patch_pds_data(mocker)
    mother_nhs_no = "9000000025"
    expected = (codes.PATIENT_NOT_RELATED, "")

    # Change related person identifier to cause failure
    related[0].patient.identifier.value = "9000000017"

    sut = ValidateRelationship()

    # Act
    actual = sut.is_eligible(mother_nhs_no, patient, related)

    # Assert
    assert actual == expected


def test_is_eligible_when_all_checks_pass_then_validated_returned(
    patient: Patient,
    related: RelatedPerson,
    mocker: MockerFixture,
):
    """
    Test Function : ValidateRelationship.is_eligible
    Scenario: When all eligibility check pass
    Expected Result: Valdated relationship dict is returned
    """

    # Arrange
    patch_pds_data(mocker)
    mother_nhs_no = "9000000009"
    expected = (codes.VALIDATED_RELATIONSHIP, related[0])

    sut = ValidateRelationship()
    # Act
    actual = sut.is_eligible(mother_nhs_no, patient, related)

    # Assert
    assert actual == expected


# Lambda -> start
@pytest.mark.parametrize(
    "event",
    [
        pytest.param(
            {
                # ValidateRelationship.PARAM_MOTHER_NHS_NO: "9000000009",
                # "pdsPatientStatus": int(HTTPStatus.BAD_REQUEST),
                # "pdsPatient":"",
                # "pdsRelationship": "",
                # "pdsRelationshipStatus": int(HTTPStatus.BAD_REQUEST),
            }
        ),
        pytest.param(
            {
                ValidateRelationship.PARAM_MOTHER_NHS_NO: "9000000009",
                # "pdsPatientStatus": int(HTTPStatus.BAD_REQUEST),
                # "pdsPatient":"",
                # "pdsRelationship": "",
                # "pdsRelationshipStatus": int(HTTPStatus.BAD_REQUEST),
            }
        ),
        pytest.param(
            {
                ValidateRelationship.PARAM_MOTHER_NHS_NO: "9000000009",
                "pdsPatientStatus": int(HTTPStatus.BAD_REQUEST),
                # "pdsPatient":"",
                # "pdsRelationship": "",
                # "pdsRelationshipStatus": int(HTTPStatus.BAD_REQUEST),
            }
        ),
        pytest.param(
            {
                ValidateRelationship.PARAM_MOTHER_NHS_NO: "9000000009",
                "pdsPatientStatus": int(HTTPStatus.BAD_REQUEST),
                "pdsPatient": "",
                # "pdsRelationship": "",
                # "pdsRelationshipStatus": int(HTTPStatus.BAD_REQUEST),
            }
        ),
        pytest.param(
            {
                ValidateRelationship.PARAM_MOTHER_NHS_NO: "9000000009",
                "pdsPatientStatus": int(HTTPStatus.BAD_REQUEST),
                "pdsPatient": "",
                "pdsRelationship": "",
                # "pdsRelationshipStatus": int(HTTPStatus.BAD_REQUEST),
            }
        ),
    ],
)
def test_start_when_parameters_missing_then_bad_request_returned(
    event, mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.start
    Scenario: When one or more parameters are missing
    Expected Result: HTTP Bad request status returned
    """
    # Arrange
    eligibile = mocker.patch.object(
        ValidateRelationship, "is_eligible", return_value=None
    )
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    eligibile.assert_not_called()
    publish.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        pytest.param(int(HTTPStatus.BAD_REQUEST)),
        pytest.param(int(HTTPStatus.FORBIDDEN)),
        pytest.param(int(HTTPStatus.INTERNAL_SERVER_ERROR)),
    ],
)
def test_start_when_patient_lookup_failed_then_raises_error(
    status: int, mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.start
    Scenario: When 'pdsPatientStatus' status is not 200
    Expected Result: Patient not found
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    expected = codes.PATIENT_STATUS_FAIL

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009", status, patient_json, int(HTTPStatus.OK), relationship_json
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(expected["http_status"])
    # data is not included
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    # Error is output
    assert sut.response["body"]["error"] == expected["response_code"]
    publish.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        pytest.param(int(HTTPStatus.BAD_REQUEST)),
        pytest.param(int(HTTPStatus.FORBIDDEN)),
        pytest.param(int(HTTPStatus.INTERNAL_SERVER_ERROR)),
    ],
)
def test_start_when_relationship_lookup_failed_then_raises_error(
    status: int, mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.start
    Scenario: When 'pdsRelationshipStatus' status is not 200
    Expected Result: Relationship not found
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    expected = codes.RELATION_STATUS_FAIL

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009", int(HTTPStatus.OK), patient_json, status, relationship_json
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(expected["http_status"])
    # data is not included
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    # Error is output
    assert sut.response["body"]["error"] == expected["response_code"]
    publish.assert_not_called()


def test_start_when_patient_is_empty_then_raises_error(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When 'pdsPatient' parameter is empty
    Expected Result: HTTP internal error status returned
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    patient_json = ""
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009",
        int(HTTPStatus.OK),
        patient_json,
        int(HTTPStatus.OK),
        relationship_json,
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    publish.assert_not_called()


def test_start_when_patient_not_found_then_raises_not_found(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When 'pdsPatientStatus' status is not 200
    Expected Result: Patient not found
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    expected = codes.PATIENT_NOT_FOUND

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009",
        int(HTTPStatus.NOT_FOUND),
        patient_json,
        int(HTTPStatus.OK),
        relationship_json,
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(expected["http_status"])
    # data is not included
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    # Error is output
    assert sut.response["body"]["error"] == expected["response_code"]
    publish.assert_called_once()


def test_start_when_relationship_not_found_then_raises_not_found(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When 'pdsRelationship' status is not 200
    Expected Result: Relationship not found
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    expected = codes.RELATION_NOT_FOUND

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009",
        int(HTTPStatus.OK),
        patient_json,
        int(HTTPStatus.NOT_FOUND),
        relationship_json,
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(expected["http_status"])
    # data is not included
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    # Error is output
    assert sut.response["body"]["error"] == expected["response_code"]
    publish.assert_called_once()


def test_start_when_relationship_is_empty_then_raises_error(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When relationship info is empty
    Expected Result: HTTP internal error status returned
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    patient_json = load_mock_record(patient_file)
    relationship_json = " "

    event = create_event(
        "9000000009",
        int(HTTPStatus.OK),
        patient_json,
        int(HTTPStatus.OK),
        relationship_json,
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    publish.assert_not_called()


def test_start_when_general_error_then_raises_error(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When an unexpected error occurs
    Expected Result: HTTP internal error status returned
    """
    # Arrange
    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    mocker.patch.object(
        ValidateRelationship,
        "_ValidateRelationship__are_parameters_present",
        return_value=True,
    )
    mock = mocker.patch.object(ValidateRelationship, "is_eligible", return_value=None)
    mock.side_effect = Exception()

    sut = ValidateRelationship()
    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == int(HTTPStatus.INTERNAL_SERVER_ERROR)
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    publish.assert_not_called()


@pytest.mark.parametrize(
    "eligbility_result",
    [
        pytest.param(codes.PATIENT_DECEASED),
        pytest.param(codes.NO_PATIENT_CONSENT),
        pytest.param(codes.PATIENT_NOT_FOUND),
        pytest.param(codes.PATIENT_STATUS_FAIL),
        pytest.param(codes.RELATION_NOT_FOUND),
        pytest.param(codes.RELATION_STATUS_FAIL),
        pytest.param(codes.PATIENT_NOT_ELIGIBLE_OVER_13),
    ],
)
def test_start_when_eligibility_fails_then_empty_result_returned(
    eligbility_result, mocker: MockerFixture
):
    """
    Test Function : ValidateRelationship.start
    Scenario: When validation process fails
    Expected Result: Expected result returned
    """
    # Arrange
    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)

    event = create_event(
        "9000000009",
        int(HTTPStatus.OK),
        patient_json,
        int(HTTPStatus.OK),
        relationship_json,
    )

    # Patch eligibility to return expected outcome
    mocker.patch.object(
        ValidateRelationship, "is_eligible", return_value=(eligbility_result, "")
    )

    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == eligbility_result["http_status"]
    # Check that patient / relationship data is not returned
    assert "pdsPatient" not in sut.response["body"]
    assert "pdsRelationship" not in sut.response["body"]
    # Check the inputs are returned too
    assert sut.response["body"]["error"] == eligbility_result["response_code"]
    publish.assert_called_once()


def test_start_when_valid_then_return_true(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When validation process completes
    Expected Result: Expected relationship result
    """
    # Arrange
    eligbility_result = codes.VALIDATED_RELATIONSHIP

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)
    expected_relation = relationship_json[1]

    event = create_event(
        "9000000009",
        int(HTTPStatus.OK),
        patient_json,
        int(HTTPStatus.OK),
        relationship_json,
    )

    # Patch eligibility to return expected outcome
    mocker.patch.object(
        ValidateRelationship,
        "is_eligible",
        return_value=(eligbility_result, RelatedPerson(expected_relation)),
    )

    publish = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    assert sut.response["statusCode"] == eligbility_result["http_status"]
    # Check the inputs are returned too
    assert sut.response["body"][ValidateRelationship.PARAM_PATIENT] == patient_json
    assert (
        sut.response["body"][ValidateRelationship.PARAM_RELATION] == expected_relation
    )
    publish.assert_called_once()


# lambda_handler
def test_lambda_handler_when_invoked_then_calls_start_is_called(mocker: MockerFixture):
    """
    Test Function : lambda_handler
    Scenario: When function is invoked calls underlying class
    Expected Result: Underlying function invoked once only
    """
    # Arrange
    event = {}
    context = {}
    mock = mocker.patch.object(ValidateRelationship, "start", return_value=None)

    # Act
    lambda_handler(event, context)

    # Assert
    mock.assert_called_once()


def test_start_correct_correlation_id_pass_to_audit(mocker: MockerFixture):
    """
    Test Function : ValidateRelationship.start
    Scenario: When validation process fails (relationship not found)
    Expected Result: Expected audit event to be called with the passing correlation ID
    """
    # Arrange
    validation_result_event = mocker.patch(
        "lambdas.validate_relationship.main.validation_result_event", return_value=None
    )

    patient_json = load_mock_record(patient_file)
    relationship_json = load_mock_record(relationship_file)
    correlation_id = "test-id"
    request_id = "test-request-id"
    mother_nhs_number = "9000000009"

    event = {
        ValidateRelationship.PARAM_MOTHER_NHS_NO: mother_nhs_number,
        ValidateRelationship.PARAM_PATIENT_STATUS: int(HTTPStatus.OK),
        ValidateRelationship.PARAM_PATIENT: patient_json,
        ValidateRelationship.PARAM_RELATION: relationship_json,
        ValidateRelationship.PARAM_RELATION_STATUS: int(HTTPStatus.NOT_FOUND),
        ValidateRelationship.PARAM_CORRELATION_ID: correlation_id,
        ValidateRelationship.PARAM_REQUEST_ID: request_id,
    }

    sut = ValidateRelationship()
    sut.event = event

    # Act
    sut.start()

    # Assert
    validation_result_event.assert_called_with(
        "", mother_nhs_number, codes.RELATION_NOT_FOUND, request_id, correlation_id
    )


def load_mock_record(file_path):
    """
    Load a mock record from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the mock record.

    Returns:
        dict: The loaded mock record as a Python dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def patch_pds_data(mocker: MockerFixture):
    """Patches pdsdata methods with data that will result in a pass"""
    relationships = [ValidateRelationship.MOTHER_RELATION_CODE]
    unrestricted = "U"
    age = 5

    mocker.patch.object(pdsdata, "get_is_person_deceased", return_value=False)
    mocker.patch.object(pdsdata, "get_security_code", return_value=unrestricted)
    mocker.patch.object(pdsdata, "get_relationship", return_value=relationships)

    # Overwrite the get_patient_age to return test value
    mocker.patch.object(pdsdata, "get_patient_age", return_value=age)


def create_event(proxy_nhs_no, patient_status, patient, relation_status, relation):
    """Creates a collection that can as an event input"""
    return {
        ValidateRelationship.PARAM_MOTHER_NHS_NO: proxy_nhs_no,
        ValidateRelationship.PARAM_PATIENT_STATUS: patient_status,
        ValidateRelationship.PARAM_PATIENT: patient,
        ValidateRelationship.PARAM_RELATION: relation,
        ValidateRelationship.PARAM_RELATION_STATUS: relation_status,
    }
