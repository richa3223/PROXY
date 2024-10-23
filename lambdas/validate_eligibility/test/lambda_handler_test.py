"""
Collection of tests for the Validate Proxy Eligibility lambda function.
"""

import json
import os
from http import HTTPStatus

import pytest
from fhirclient.models.relatedperson import RelatedPerson
from pytest_mock import MockerFixture

from lambdas.utils.event_utilities.event_publisher import ValidationResultEventPublisher
from lambdas.utils.validation import codes
from lambdas.validate_eligibility.main import ValidateEligibility

DATAPATH = "../../utils/pds/sample_data/"
DATA_PROXY_DETAILS_VALID = DATAPATH + "patient_details/proxy_valid.json"
DATA_RELATIONSHIP_THREE_CHILDREN = (
    DATAPATH + "related_person/proxy_valid_three_children.json"
)


@pytest.fixture(name="lambda_instance")
def setup_lambda_test_instance():
    """Create and return an instance of the Lambda Function Class"""
    return ValidateEligibility()


def test_person_array_filter_single_match():
    """Test filter_related_person_array returns single array instance,
    with matching NHS Number value
    """

    # Arrange
    mock_relationships = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_RELATIONSHIP_THREE_CHILDREN,
        )
    )

    fhir_relationships = []
    for relationship in mock_relationships:
        fhir_relationships.append(RelatedPerson(relationship))

    nhs_number = "5993544619"

    sut = ValidateEligibility()
    res = sut.filter_related_person_array(fhir_relationships, nhs_number)

    assert len(res) == 1
    assert res[0].patient.identifier.value == nhs_number


def test_person_array_filter_no_match():
    """Test filter_related_person_array returns empty array when no match is found"""

    # Arrange
    mock_relationships = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_RELATIONSHIP_THREE_CHILDREN,
        )
    )

    fhir_relationships = []
    for relationship in mock_relationships:
        fhir_relationships.append(RelatedPerson(relationship))

    sut = ValidateEligibility()
    res = sut.filter_related_person_array(fhir_relationships, "test")

    assert len(res) == 0


def setup_lambda_instance_for_error_test(
    lambda_instance: ValidateEligibility,
    missing_parameter: str,
    expected_error_code: HTTPStatus,
):
    """Helper function to set up lambda_instance for parameter error tests."""

    # Arrange
    mock_proxy_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        DATA_PROXY_DETAILS_VALID,
    )
    mock_proxy = load_mock_record(mock_proxy_file)

    lambda_instance.event = {
        "pdsProxyDetails": mock_proxy,
        "pdsProxyStatusCode": 200,
        "pdsRelationshipLookup": {},
        "pdsRelationshipLookupStatusCode": 200,
        "patientNhsNumber": None,
    }
    lambda_instance.event.pop(missing_parameter, None)

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["error"] == expected_error_code


def test_error_on_missing_pds_proxy_details_parameter(
    lambda_instance: ValidateEligibility,
):
    """Test error response when 'pdsProxyDetails' parameter is missing"""
    setup_lambda_instance_for_error_test(
        lambda_instance,
        "pdsProxyDetails",
        lambda_instance.PARAMETER_PDS_PROXY_DETAILS_NOT_FOUND,
    )


def test_error_on_missing_pds_proxy_details_status_code_parameter(
    lambda_instance: ValidateEligibility,
):
    """Test error response when 'pdsProxyStatusCode' parameter is missing"""
    setup_lambda_instance_for_error_test(
        lambda_instance,
        "pdsProxyStatusCode",
        lambda_instance.PARAMETER_PDS_PROXY_STATUS_CODE_NOT_FOUND,
    )


def test_error_on_missing_pds_relationship_parameter(
    lambda_instance: ValidateEligibility,
):
    """Test error response when 'pdsRelationshipLookup' parameter is missing"""

    setup_lambda_instance_for_error_test(
        lambda_instance,
        "pdsRelationshipLookup",
        lambda_instance.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_NOT_FOUND,
    )


def test_error_on_missing_pds_relationship_status_code_parameter(
    lambda_instance: ValidateEligibility,
):
    """Test error response when 'pdsRelationshipLookupStatusCode' parameter is missing"""

    setup_lambda_instance_for_error_test(
        lambda_instance,
        "pdsRelationshipLookupStatusCode",
        lambda_instance.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_NOT_FOUND,
    )


@pytest.mark.parametrize(
    "pds_proxy_status_code, pds_relationship_status_code, expected_error",
    [
        (500, 200, ValidateEligibility.PARAMETER_PDS_PROXY_STATUS_CODE_INVALID),
        (
            200,
            500,
            ValidateEligibility.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_INVALID,
        ),
    ],
)
def test_error_bad_request_pds_invalid_status_codes(
    lambda_instance: ValidateEligibility,
    pds_proxy_status_code,
    pds_relationship_status_code,
    expected_error,
):
    """Test for bad request with invalid PDS status codes"""

    # Arrange
    lambda_instance.event = {
        "pdsProxyStatusCode": pds_proxy_status_code,
        "pdsRelationshipLookupStatusCode": pds_relationship_status_code,
    }

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert lambda_instance.response["body"]["error"] == expected_error


def setup_lambda_instance_for_eligible_test(  # pylint: disable=too-many-arguments
    mocker: MockerFixture,
    lambda_instance,
    pds_proxy_details=None,
    pds_proxy_status_code=200,
    pds_relationship_lookup=None,
    pds_relationship_lookup_status_code=200,
    patient_nhs_number=None,
    correlation_id=None,
    request_id="test-request-id",
):
    """Helper function to set up lambda_instance for eligible tests."""

    mocker.patch.object(ValidationResultEventPublisher, "publish", return_value=None)

    # Arrange
    lambda_instance.event = {
        "pdsProxyDetails": pds_proxy_details,
        "pdsProxyStatusCode": pds_proxy_status_code,
        "pdsRelationshipLookup": pds_relationship_lookup,
        "pdsRelationshipLookupStatusCode": pds_relationship_lookup_status_code,
        "patientNhsNumber": patient_nhs_number,
        "correlationId": correlation_id,
        "requestId": request_id,
    }

    # Act
    lambda_instance.start()

    # Assert
    return (
        lambda_instance.response["statusCode"],
        lambda_instance.response["body"]["eligibility"],
        lambda_instance.response["body"]["relationshipArr"],
    )


def test_error_not_eligible_proxy_not_found(
    mocker: MockerFixture, lambda_instance: ValidateEligibility
):
    """Test when Proxy is not eligible due to no record found in PDS Details"""
    status_code, eligibility, _ = setup_lambda_instance_for_eligible_test(
        mocker, lambda_instance, pds_proxy_status_code=404
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is False


def test_error_bad_request_pds_details_not_fhir_format(
    lambda_instance: ValidateEligibility,
):
    """Test bad request error when PDS Details is not a FHIR format"""

    lambda_instance.event = {
        "pdsProxyDetails": "test-invalid-fhir-patient",
        "pdsProxyStatusCode": 200,
        "pdsRelationshipLookup": {},
        "pdsRelationshipLookupStatusCode": 200,
    }

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert (
        lambda_instance.response["body"]["error"] == "Supplied data cannot be processed"
    )


def test_error_not_eligible_proxy_deceased(
    mocker: MockerFixture, lambda_instance: ValidateEligibility
):
    """Test when Proxy is not eligible due to PDS details showing as a deceased record"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATAPATH + "patient_details/proxy_deceased.json",
        )
    )
    status_code, eligibility, _ = setup_lambda_instance_for_eligible_test(
        mocker, lambda_instance, pds_proxy_details=mock_proxy
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is False


def test_error_not_eligible_proxy_restricted(
    mocker: MockerFixture, lambda_instance: ValidateEligibility
):
    """Test when Proxy is not eligible due to PDS details showing a restricted record"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATAPATH + "patient_details/proxy_restricted.json",
        )
    )
    status_code, eligibility, _ = setup_lambda_instance_for_eligible_test(
        mocker, lambda_instance, pds_proxy_details=mock_proxy
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is False


def test_error_proxy_no_relationship_found(
    mocker: MockerFixture,
    lambda_instance: ValidateEligibility,
):
    """Test when Proxy has no relationships found on PDS"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )
    status_code, eligibility, _ = setup_lambda_instance_for_eligible_test(
        mocker,
        lambda_instance,
        pds_proxy_details=mock_proxy,
        pds_relationship_lookup_status_code=404,
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is False


def test_error_bad_request_pds_relationships_not_fhir_format(
    lambda_instance: ValidateEligibility,
):
    """Test bad request error when PDS Relationships is not a FHIR format"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )

    lambda_instance.event = {
        "pdsProxyDetails": mock_proxy,
        "pdsProxyStatusCode": 200,
        "pdsRelationshipLookup": "test-invalid-fhir-relationship",
        "pdsRelationshipLookupStatusCode": 200,
    }

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert (
        lambda_instance.response["body"]["error"] == "Supplied data cannot be processed"
    )


def test_valid_matching_relationships(
    mocker: MockerFixture,
    lambda_instance: ValidateEligibility,
):
    """Test Valid Proxy eligibility with lookup relationships"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )

    mock_relationships = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_RELATIONSHIP_THREE_CHILDREN,
        )
    )
    (
        status_code,
        eligibility,
        relationship_arr,
    ) = setup_lambda_instance_for_eligible_test(
        mocker,
        lambda_instance,
        pds_proxy_details=mock_proxy,
        pds_relationship_lookup=mock_relationships,
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is True
    assert len(relationship_arr) == 3


def test_valid_matching_relationships_1_to_1(
    mocker: MockerFixture,
    lambda_instance: ValidateEligibility,
):
    """Test Valid Proxy eligibility with 1:1 match"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )

    mock_relationships = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_RELATIONSHIP_THREE_CHILDREN,
        )
    )
    (
        status_code,
        eligibility,
        relationship_arr,
    ) = setup_lambda_instance_for_eligible_test(
        mocker,
        lambda_instance,
        pds_proxy_details=mock_proxy,
        pds_relationship_lookup=mock_relationships,
        patient_nhs_number="5993544619",
    )

    # Assert
    assert status_code == HTTPStatus.OK
    assert eligibility is True
    assert len(relationship_arr) == 1


def test_error_general_500_internal(
    mocker: MockerFixture,
    lambda_instance: ValidateEligibility,
):
    """Test for when an general internal exception happens"""
    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )

    lambda_instance.event = {
        "pdsProxyDetails": mock_proxy,
        "pdsProxyStatusCode": 200,
        "pdsRelationshipLookup": {},
        "pdsRelationshipLookupStatusCode": 200,
    }

    mock = mocker.patch.object(
        ValidationResultEventPublisher, "publish", return_value=None
    )
    mock.side_effect = Exception()

    # Act
    lambda_instance.start()

    # Assert
    assert lambda_instance.response["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    assert (
        lambda_instance.response["body"]["error"]
        == "Error when attempting to confirm eligibility"
    )


def test_validate_eligibility_start_correct_correlation_id_pass_to_audit(
    mocker: MockerFixture, lambda_instance: ValidateEligibility
):
    """
    Test Function : ValidateEligibility.start
    Scenario: When eligibility process fails (relationship not found)
    Expected Result: Expected audit event to be called with the passing correlation ID
    """
    # Arrange
    validation_result_event = mocker.patch(
        "lambdas.validate_eligibility.main.validation_result_event", return_value=None
    )
    correlation_id = "test-id"
    request_id = "test-request-id"

    mock_proxy = load_mock_record(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            DATA_PROXY_DETAILS_VALID,
        )
    )

    _ = setup_lambda_instance_for_eligible_test(
        mocker,
        lambda_instance,
        pds_proxy_details=mock_proxy,
        pds_relationship_lookup_status_code=404,
        correlation_id=correlation_id,
        request_id=request_id,
    )

    # Assert
    validation_result_event.assert_called_with(
        "5993552700", "", codes.PROXY_NO_RELATIONSHIPS_FOUND, request_id, correlation_id
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
