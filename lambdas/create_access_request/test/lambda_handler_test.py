"""
Collection of tests for the create access request lambda function.
"""

from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from lambdas.create_access_request.main import (
    CreateAccessRequest,
    DynamoDBError,
    lambda_handler,
)
from lambdas.utils.aws.dynamodb import AccessRequestStates, StoreAccessRequest
from lambdas.utils.validation.fhir_validate_questionnaire import (
    FHIRValidateQuestionnaire,
)

SUCCESS_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "information",
            "code": "informational",
            "details": {"coding": [{"code": "8xx4m2wl5", "display": "8xx4m2wl5"}]},
        }
    ],
}

FAILURE_RESPONSE = {
    "issue": [
        {
            "code": "invalid",
            "details": {
                "coding": [
                    {
                        "code": "BAD_REQUEST",
                        "display": "The request could not be processed.",
                        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version": "1",
                    }
                ]
            },
            "diagnostics": "The supplied input is not a valid FHIR QuestionnaireResponse.",
            "severity": "error",
        }
    ],
    "resourceType": "OperationOutcome",
}

INVALID_SERVER_ERROR_RESPONSE = {
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

SAMPLE_REQUEST = {
    "headers": "",
    "body": '{"item": [{"linkId": "proxy_details","item": [{"linkId": "nhs_number", "answer": [{"valueString": "1234567890"}]}]},{"linkId": "patient_details","item": [{"linkId": "nhs_number", "answer": [{"valueString": "0987654321"}]}]}]}',
}


def test_start_when_parameter_not_present_return_bad_request() -> None:
    """
    Test Function : create_access_request.main.CreateAccessRequest.start
    Scenario: When parameters are not present
    Expected Result: Then bad request response is returned
    """

    # Act
    actual = lambda_handler({}, {})
    # Assert
    assert actual["statusCode"] == 400
    assert actual["body"] == FAILURE_RESPONSE


def test_start_when_validation_succeeds_returns_ok(mocker: MockerFixture) -> None:
    """
    Test the lambda handler function returns precanned response
    """

    # Arrange
    mocker.patch.object(
        FHIRValidateQuestionnaire, "validate_questionnaire_response", return_value=True
    )
    mocker.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.create_reference_code",
        return_value="8xx4m2wl5",
    )
    mocker.patch.object(
        CreateAccessRequest,
        "_save_to_dynamodb",
        return_value=None,
    )

    # Act
    response = lambda_handler({"header": "", "body": '{"somethign":"else"}'}, {})

    # Assert
    assert response["body"] == SUCCESS_RESPONSE


def test_start_when_validation_failed_returns_bad_request(
    mocker: MockerFixture,
) -> None:
    """
    Test Function : create_access_request.main.CreateAccessRequest.start
    Scenario: When validation fails
    Expected Result: Then bad request response is returned
    """
    # Arrange
    resp = CreateAccessRequest()
    resp.event = SAMPLE_REQUEST
    validation = mocker.patch.object(
        FHIRValidateQuestionnaire, "validate_questionnaire_response", return_value=False
    )

    # Act
    resp.start()
    actual = resp.response

    # Assert
    assert actual["statusCode"] == 400
    assert actual["body"] == FAILURE_RESPONSE

    validation.assert_called_once()


def test_lambda_handler_invokes_start(mocker: MockerFixture):
    """
    Test Function : create_access_request.main.lambda_handler
    Scenario: When lambda_handler is called
    Expected Result: Then CreateAccessRequest.start is invoked
    """

    # Arrange
    mock = mocker.patch.object(CreateAccessRequest, "start", return_value=None)

    # Act
    lambda_handler({}, {})

    # Assert
    mock.assert_called_once()


def test_save_to_dynamodb_happy_path(mocker: MockerFixture) -> None:
    # Arrange
    mock_put_item = mocker.patch(
        "lambdas.create_access_request.main.put_item",
        return_value={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )
    response = {
        "item": [
            {
                "linkId": "proxy_details",
                "item": [
                    {"linkId": "nhs_number", "answer": [{"valueString": "1234567890"}]}
                ],
            },
            {
                "linkId": "patient_details",
                "item": [
                    {"linkId": "nhs_number", "answer": [{"valueString": "0987654321"}]}
                ],
            },
        ]
    }
    reference_code = "ABC123"
    # Act
    create_access_request = CreateAccessRequest()
    create_access_request._save_to_dynamodb(response, reference_code)

    # Assert
    mock_put_item.assert_called_once_with(
        StoreAccessRequest(
            ReferenceCode=reference_code,
            ProxyNHSNumber="1234567890",
            PatientNHSNumber="0987654321",
            QuestionnaireData=response,
            ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
        )
    )


def test_save_to_dynamodb_max_retries_exceeded(mocker: MockerFixture) -> None:
    # Arrange
    mock_put_item = mocker.patch(
        "lambdas.create_access_request.main.put_item",
        return_value={"ResponseMetadata": {"HTTPStatusCode": 400}},
    )
    response = {
        "item": [
            {
                "linkId": "proxy_details",
                "item": [
                    {"linkId": "nhs_number", "answer": [{"valueString": "1234567890"}]}
                ],
            },
            {
                "linkId": "patient_details",
                "item": [
                    {"linkId": "nhs_number", "answer": [{"valueString": "0987654321"}]}
                ],
            },
        ]
    }
    reference_code = "ABC123"
    # Act
    create_access_request = CreateAccessRequest()
    with pytest.raises(DynamoDBError):
        create_access_request._save_to_dynamodb(response, reference_code)
    # Assert
    mock_put_item.assert_has_calls(
        [
            call(
                StoreAccessRequest(
                    ReferenceCode=reference_code,
                    ProxyNHSNumber="1234567890",
                    PatientNHSNumber="0987654321",
                    QuestionnaireData=response,
                    ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
                )
            ),
            call(
                StoreAccessRequest(
                    ReferenceCode=reference_code,
                    ProxyNHSNumber="1234567890",
                    PatientNHSNumber="0987654321",
                    QuestionnaireData=response,
                    ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
                )
            ),
            call(
                StoreAccessRequest(
                    ReferenceCode=reference_code,
                    ProxyNHSNumber="1234567890",
                    PatientNHSNumber="0987654321",
                    QuestionnaireData=response,
                    ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
                )
            ),
        ]
    )


def test_lambda_handler_start__500_error(mocker: MockerFixture):
    """
    Test Function : create_access_request..main.lambda_handler
    Scenario: When lambda_handler is called and an exception is raised
    Expected Result: Then a 500 error is returned
    """
    # Arrange
    mocker.patch.object(
        FHIRValidateQuestionnaire, "validate_questionnaire_response", return_value=True
    )
    reference_code = mocker.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.create_reference_code"
    )
    reference_code.return_value = "somekey"
    put_item = mocker.patch(
        "lambdas.create_access_request.main.put_item",
        side_effect=Exception("mock error"),
    )
    # Act
    actual = lambda_handler(SAMPLE_REQUEST, {})

    # Assert
    assert actual["statusCode"] == 500
    assert actual["body"] == INVALID_SERVER_ERROR_RESPONSE

    reference_code.assert_called_once()
    put_item.call_count == 3
