"""This module contains functions to interact with DynamoDB"""

from dataclasses import dataclass
from enum import Enum
from os import getenv
from time import time

from boto3 import client
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import DataNotFoundError

from lambdas.utils.logging.logger import write_log

TTL = int(getenv("DYNAMODB_TTL", "604800"))


class AccessRequestStates(Enum):
    ACCESS_REQUEST_CREATED = "ACCESS_REQUEST_CREATED"
    GP_AUTH_REQUEST_CREATED = "GP_AUTHORISATION_REQUEST_CREATED"
    ACCESS_REQUEST_SENT = "ACCESS_REQUEST_SENT_FOR_AUTHORISATION"


@dataclass(init=True)
class StoreAccessRequest:
    ReferenceCode: str
    ProxyNHSNumber: str
    PatientNHSNumber: str
    QuestionnaireData: dict
    ApplicationStatus: str


def put_item(access_request: StoreAccessRequest) -> dict:
    """Put an item into DynamoDB

    Args:
        access_request (StoreAccessRequest): The access request to be stored

    Returns:
        dict: The response from DynamoDB
    """
    dynamodb = client("dynamodb", region_name="eu-west-2")
    setattr(access_request, "TTL", __get_time_to_live())
    serialized_data = __serialize_data(access_request.__dict__)
    response = dynamodb.put_item(
        TableName=getenv("DYNAMODB_TABLE_NAME"),
        Item=serialized_data,
    )
    write_log(
        "INFO", {"info": f"Item saved to DynamoDB: {access_request.ReferenceCode}"}
    )
    return response


def get_item(reference_code: str) -> dict:
    """Get an item from DynamoDB

    Args:
        reference_code (str): The reference code of the access request

    Returns:
        dict: The response from DynamoDB
    """
    dynamodb = client("dynamodb", region_name="eu-west-2")
    key = {"ReferenceCode": {"S": str(reference_code)}}
    rec = dynamodb.get_item(TableName=getenv("DYNAMODB_TABLE_NAME"), Key=key)

    # Some error handling might be needed here
    # For now surfacing the errors as needed
    if "Item" not in rec:
        raise DataNotFoundError(f"Record with key '{reference_code}' not found")

    rtn = rec["Item"]
    write_log(
        "INFO", {"info": f"Item retrieved from DynamoDB: {rtn['ReferenceCode']['S']}"}
    )
    return rtn


def update_status(reference_code: str, status: AccessRequestStates) -> None:
    dynamodb = client("dynamodb", region_name="eu-west-2")
    key = {"ReferenceCode": {"S": str(reference_code)}}

    response = dynamodb.update_item(
        TableName=getenv("DYNAMODB_TABLE_NAME"),
        Key=key,
        UpdateExpression="set ApplicationStatus = :status",
        ExpressionAttributeValues={":status": {"S": str(status.value)}},
    )

    write_log(
        "INFO", {"info": f"Item updated in DynamoDB: {reference_code} : {response}"}
    )


def __get_time_to_live() -> int:
    return int(time()) + TTL


def __serialize_data(data: dict) -> dict:
    """Serialize the data ready for DynamoDB

    Args:
        data (dict): The data to be serialized

    Returns:
        dict: The serialized data
    """
    return {k: TypeSerializer().serialize(v) for k, v in data.items()}
