"""Unit tests for the dynamodb module."""

from os import environ

from boto3 import client
from pytest_mock import MockerFixture

from lambdas.utils.aws.dynamodb import (
    AccessRequestStates,
    StoreAccessRequest,
    get_item,
    put_item,
    update_status,
)


def test_put_item(mocker: MockerFixture) -> None:
    # Arrange
    environ["DYNAMODB_TABLE_NAME"] = dynamodb_table_name = "DYNAMODB_TABLE_NAME"
    environ["DYNAMODB_TTL"] = "604800"

    mock_client = mocker.patch("lambdas.utils.aws.dynamodb.client")
    mock_time = mocker.patch("lambdas.utils.aws.dynamodb.time")
    mock_time.return_value = 1234567890

    data = StoreAccessRequest(
        ReferenceCode="ABC123",
        ProxyNHSNumber="1234567890",
        PatientNHSNumber="0987654321",
        QuestionnaireData={"question1": "answer1", "question2": "answer2"},
        ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
    )
    # Act
    put_item(data)
    # Assert
    expected_ttl = 1234567890 + 604800
    mock_client.assert_called_once_with("dynamodb", region_name="eu-west-2")
    mock_client.return_value.put_item.assert_called_once_with(
        TableName=dynamodb_table_name,
        Item={
            "ReferenceCode": {"S": "ABC123"},
            "ProxyNHSNumber": {"S": "1234567890"},
            "PatientNHSNumber": {"S": "0987654321"},
            "QuestionnaireData": {
                "M": {"question1": {"S": "answer1"}, "question2": {"S": "answer2"}}
            },
            "ApplicationStatus": {
                "S": AccessRequestStates.ACCESS_REQUEST_CREATED.value
            },
            "TTL": {"N": str(expected_ttl)},
        },
    )
    # Cleanup
    del environ["DYNAMODB_TABLE_NAME"]
    del environ["DYNAMODB_TTL"]


def test_get_item(mocker: MockerFixture) -> None:
    # Arrange
    reference_code = "ABC123"
    rtn = {"Item": {"ReferenceCode": {"S": reference_code}}}

    environ["DYNAMODB_TABLE_NAME"] = dynamodb_table_name = "DYNAMODB_TABLE_NAME"
    mock_client = mocker.patch("lambdas.utils.aws.dynamodb.client")
    mock_client.return_value.get_item.return_value = rtn

    # Act
    get_item(reference_code)

    # Assert
    mock_client.assert_called_once_with("dynamodb", region_name="eu-west-2")
    mock_client.return_value.get_item.assert_called_once_with(
        TableName=dynamodb_table_name, Key={"ReferenceCode": {"S": str(reference_code)}}
    )
    # Cleanup
    del environ["DYNAMODB_TABLE_NAME"]


def test_update_status(mocker: MockerFixture) -> None:
    # Arrange
    environ["DYNAMODB_TABLE_NAME"] = dynamodb_table_name = "DYNAMODB_TABLE_NAME"

    mock_client = mocker.patch("lambdas.utils.aws.dynamodb.client")

    reference_code = "ABC123"
    key = {"ReferenceCode": {"S": str(reference_code)}}
    status = AccessRequestStates.ACCESS_REQUEST_SENT

    # Act
    update_status(reference_code, status)

    # Assert
    mock_client.assert_called_once_with("dynamodb", region_name="eu-west-2")
    mock_client.return_value.update_item.assert_called_once_with(
        TableName=dynamodb_table_name,
        Key=key,
        UpdateExpression="set ApplicationStatus = :status",
        ExpressionAttributeValues={":status": {"S": str(status.value)}},
    )

    # Cleanup
    del environ["DYNAMODB_TABLE_NAME"]
