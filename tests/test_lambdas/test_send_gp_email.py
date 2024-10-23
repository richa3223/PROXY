"""
Test send_gp_email Lambda
"""

from uuid import uuid4

from ..helpers import WORKSPACE, Helpers
from ..helpers.aws.dynamodb import (
    TTL,
    GPAccessRequestSentForAuthorisation,
    get_item,
    put_item,
    serialize_dict,
)
from ..helpers.aws.s3 import HYDRATED_EMAIL_BUCKET, put_object

FUNCTION_NAME = f"{WORKSPACE}-send_gp_email"
GP_AUTHORISATION_REQUEST_CREATED = "GP_AUTHORISATION_REQUEST_CREATED"
DEFAULT_EVENT = {
    "version": "0",
    "id": "65790858-9155-42f1-9ae9-d26db6eca858",
    "detail-type": "Event from aws:dynamodb",
    "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
    "account": "123456789012",
    "time": "2024-07-04T14:05:58Z",
    "region": "eu-west-2",
    "resources": [],
    "detail": {
        "eventId": "c787cf53897e03be8810025acdf634d3",
        "eventType": GP_AUTHORISATION_REQUEST_CREATED,
        "referenceCode": "",
    },
}
EMAIL_ADDRESS = "dev.proxyaccess.gp1@mailinator.com"


# Common functions
def set_reference_code(event: dict, reference_code: str) -> dict:
    """Set reference code in event"""
    event = event.copy()
    event["detail"]["referenceCode"] = reference_code
    return event


def load_file(file_name: str) -> str:
    """Load file from test directory"""
    with open(f"test_lambdas/test_input/send_gp_email/{file_name}") as f:
        return f.read()


# Tests
def test_valid_email_event_and_data(helpers: Helpers) -> None:
    """Test the send_gp_email lambda with valid event and DynamoDB data"""
    # Arrange
    reference_code = str(uuid4())
    event = set_reference_code(DEFAULT_EVENT, reference_code)
    s3_key = f"{reference_code}.json"
    put_object(HYDRATED_EMAIL_BUCKET, s3_key, load_file("expected_email_content.json"))
    put_item(
        serialize_dict(
            GPAccessRequestSentForAuthorisation(
                ReferenceCode=reference_code,
                ProxyNHSNumber="1234567890",
                PatientNHSNumber="1234567890",
                GPEmailAddresses=[EMAIL_ADDRESS],
                S3Key=s3_key,
                TTL=TTL,
            ).to_dict()
        )
    )

    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, event)
    # Assert
    assert payload == {"statusCode": 200, "body": {"message": "OK"}}
    item = get_item(reference_code)
    assert item["ApplicationStatus"] == "ACCESS_REQUEST_SENT_FOR_AUTHORISATION"


def test_invalid_email_html(helpers: Helpers) -> None:
    """Test the send_gp_email lambda with invalid html"""
    # Arrange
    reference_code = str(uuid4())
    event = set_reference_code(DEFAULT_EVENT, reference_code)
    s3_key = f"{reference_code}.json"
    put_object(HYDRATED_EMAIL_BUCKET, s3_key, load_file("broken_email_content.json"))
    put_item(
        serialize_dict(
            GPAccessRequestSentForAuthorisation(
                ReferenceCode=reference_code,
                ProxyNHSNumber="1234567890",
                PatientNHSNumber="1234567890",
                GPEmailAddresses=[EMAIL_ADDRESS],
                S3Key=s3_key,
                TTL=TTL,
            ).to_dict()
        )
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, event)
    # Assert
    assert payload == {"statusCode": 200, "body": {"message": "OK"}}
    item = get_item(reference_code)
    assert item["ApplicationStatus"] == "ACCESS_REQUEST_SENT_FOR_AUTHORISATION"


def test_empty_invoke(helpers: Helpers) -> None:
    """
    Lambda receives empty json payload
    Lambda returns an error
    """
    # Arrange
    reference_code = str(uuid4())
    s3_key = f"{reference_code}.json"
    put_object(HYDRATED_EMAIL_BUCKET, s3_key, load_file("expected_email_content.json"))
    put_item(
        serialize_dict(
            GPAccessRequestSentForAuthorisation(
                ReferenceCode=reference_code,
                ApplicationStatus=GP_AUTHORISATION_REQUEST_CREATED,
                ProxyNHSNumber="1234567890",
                PatientNHSNumber="1234567890",
                GPEmailAddresses=[EMAIL_ADDRESS],
                S3Key=s3_key,
                TTL=TTL,
            ).to_dict()
        )
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})
    # Assert
    assert payload["statusCode"] == 500
    item = get_item(reference_code)
    assert item["ApplicationStatus"] == GP_AUTHORISATION_REQUEST_CREATED


def test_no_email_addresses(helpers: Helpers) -> None:
    """
    Lambda receives no email addresses from DynamoDB
    Lambda returns an error
    """
    # Arrange
    reference_code = str(uuid4())
    event = set_reference_code(DEFAULT_EVENT, reference_code)
    s3_key = f"{reference_code}.json"
    put_object(HYDRATED_EMAIL_BUCKET, s3_key, load_file("expected_email_content.json"))
    put_item(
        serialize_dict(
            GPAccessRequestSentForAuthorisation(
                ReferenceCode=reference_code,
                ApplicationStatus=GP_AUTHORISATION_REQUEST_CREATED,
                ProxyNHSNumber="1234567890",
                PatientNHSNumber="1234567890",
                S3Key=s3_key,
                TTL=TTL,
            ).to_dict()
        )
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, event)
    # Assert
    assert payload["statusCode"] == 400
    item = get_item(reference_code)
    assert item["ApplicationStatus"] == GP_AUTHORISATION_REQUEST_CREATED


def test_no_email_file_in_s3(helpers: Helpers) -> None:
    """Test the mail_send_email lambda with valid event and DynamoDB data"""
    # Arrange
    reference_code = str(uuid4())
    event = set_reference_code(DEFAULT_EVENT, reference_code)
    put_item(
        serialize_dict(
            GPAccessRequestSentForAuthorisation(
                ReferenceCode=reference_code,
                ApplicationStatus=GP_AUTHORISATION_REQUEST_CREATED,
                ProxyNHSNumber="1234567890",
                PatientNHSNumber="1234567890",
                GPEmailAddresses=[EMAIL_ADDRESS],
                S3Key=f"{reference_code}.json",
                TTL=TTL,
            ).to_dict()
        )
    )
    # Act
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, event)
    # Assert
    assert payload["statusCode"] == 500
    item = get_item(reference_code)
    assert item["ApplicationStatus"] == GP_AUTHORISATION_REQUEST_CREATED
