"""
Test create access request Lambda
"""

from datetime import datetime, timezone
from json import loads

import pytest
from boto3 import Session

# NB We seem to have workspace defined twice - in helpers and in helpers.environment_variables
from ..helpers import Helpers
from ..helpers.assertions.create_access_request import assert_400_bad_request
from ..helpers.assertions.generic import assert_500_internal_server_error
from ..helpers.aws.lambda_functions import (
    get_lambda_environment_variables,
    set_lambda_environment_variables,
)
from ..helpers.environment_variables import AWS_REGION, WORKSPACE

FUNCTION_NAME = f"{WORKSPACE}-create_access_request"


@pytest.mark.pds_api_call
def test_when_valid_input_then_dynamodb_record_is_created(helpers: Helpers) -> None:
    """
    Scenario: Creates a access request based on the json provided
    Expected Outcome: Lambda returns a successful result,
    and record is added to the patient-relationship DynamoDB table
    No errors.
    """
    # Arrange
    ttl = 6  # How long we want to keep the record in DynamoDB
    text_file = helpers.load_test_data_as_str(
        "test_lambdas/test_input/create_access_request/martha_timmy.json"
    )
    json_file = loads(text_file)
    # No headers are required at present
    request = {"body": text_file, "headers": {}}
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, request)
    # Assert
    # Test lambda response
    assert payload["statusCode"] == 200
    response_body = payload["body"]
    assert response_body["resourceType"] == "OperationOutcome"
    assert response_body["issue"][0]["code"] == "informational"
    actual_coding = response_body["issue"][0]["details"]["coding"][0]
    assert ["code", "display"] == list(actual_coding.keys())
    assert actual_coding["code"] == actual_coding["display"]
    assert actual_coding["code"].isalnum()
    assert len(actual_coding["code"]) == 10

    # Test record written to DynamoDB
    session = Session(region_name=AWS_REGION)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(f"{WORKSPACE}-pvrs-patient-relationship")

    key = {"ReferenceCode": actual_coding["code"]}

    item = table.get_item(Key=key)["Item"]
    assert item["ApplicationStatus"] == "ACCESS_REQUEST_CREATED"
    assert item["QuestionnaireData"] == json_file
    assert item["ProxyNHSNumber"] == json_file["source"]["identifier"]["value"]

    patient_details = next(
        (d for d in json_file["item"] if d.get("linkId") == "patient_details"), None
    )
    patient_nhs_number = next(
        (d for d in patient_details["item"] if d.get("linkId") == "nhs_number"), None
    )
    assert item["PatientNHSNumber"] == patient_nhs_number["answer"][0]["valueString"]

    future_date = datetime.fromtimestamp(float(item["TTL"]), tz=timezone.utc)
    time_difference = future_date - datetime.now(tz=timezone.utc)

    assert time_difference.days == ttl

    # Delete the test record. Do this here rather than in a tear down fixture so
    # we can inspect unsuccessful test results

    table.delete_item(Key=key)


@pytest.mark.pds_api_call
def test_when_body_key_not_present_raises_400_error(
    helpers: Helpers,
) -> None:
    """
    Scenario: Lambda is invoked but parameters do not contain body key
    Expected Response: Lambda returns a 400 error
    """
    # Arrange
    text_file = helpers.load_test_data_as_str(
        "test_lambdas/test_input/create_access_request/martha_timmy_invalid_fhir.json"
    )
    # No headers are required at present
    test_data = {"someotherkey": text_file, "headers": {}}

    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    assert payload["statusCode"] == 400
    assert_400_bad_request(payload)


@pytest.mark.pds_api_call
def test_when_body_content_is_invalid_raises_error(helpers: Helpers) -> None:
    """
    Scenario: Lambda is invoked with correct keys but invalid FHIR content
    Expected Response: Lambda returns a 400 error
    """
    # Arrange
    text_file = helpers.load_test_data_as_str(
        "test_lambdas/test_input/create_access_request/martha_timmy_invalid_fhir.json"
    )
    # No headers are required at present
    test_data = {"body": text_file, "headers": {}}

    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    # Assert
    assert payload["statusCode"] == 400
    assert_400_bad_request(payload)


def test_when_empty_json_then_raises_error(helpers: Helpers) -> None:
    """
    Scenario: Lambda is invoked with empty questionnaire response
    Expected Response: Lambda returns a 400 error
    """
    # Arrange
    # No headers are required at present
    test_data = {"body": {}, "headers": {}}

    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    # Assert
    assert payload["statusCode"] == 400
    assert_400_bad_request(payload)


def test_when_multiple_requests_reference_code_matches_expected(
    helpers: Helpers,
) -> None:
    """
    Scenario: Lambda response contains a code with the expected format
    Expected Output: Reference code is valid
    """
    # Arrange
    text_file = helpers.load_test_data_as_str(
        "test_lambdas/test_input/create_access_request/martha_timmy.json"
    )
    # No headers are required at present
    test_data = {"body": text_file, "headers": {}}

    # Act
    payload1 = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    payload2 = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    # Assert
    reference_code1 = payload1["body"]["issue"][0]["details"]["coding"][0]["code"]
    reference_code2 = payload2["body"]["issue"][0]["details"]["coding"][0]["code"]
    assert (
        reference_code1[:4] == reference_code2[:4]
    ), "Reference code prefix should be the same based on the date"
    assert len(reference_code1) == 10
