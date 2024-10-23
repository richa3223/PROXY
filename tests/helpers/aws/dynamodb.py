from dataclasses import dataclass
from datetime import datetime, timedelta
from time import time
from typing import Optional
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from ..environment_variables import WORKSPACE

DYNAMODB_TABLE_NAME = f"{WORKSPACE}-pvrs-patient-relationship"
dynamodb = client("dynamodb")
tomorrow = datetime.now() + timedelta(days=1)
TTL = round(tomorrow.timestamp() * 1000)


@dataclass(init=True)
class StoreAccessRequest:
    """
    Duplication of the main dynamo db record class
    Duplicated here to avoid adding a dependency on an implementation
    Any changes to the main should be reflected here when applicable to tests
    """

    ReferenceCode: str
    ProxyNHSNumber: str
    PatientNHSNumber: str
    TTL: int
    ApplicationStatus: Optional[str] = None
    QuestionnaireData: Optional[dict] = None

    def to_dict(self) -> dict:
        """Create a dict representation of the object for DynamoDB. Only fields with values are included."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(init=True)
class AccessRequestReadyForAuthorisation(StoreAccessRequest):
    PatientPDSPatientRecord: Optional[str] = None
    ProxyPDSPatientRecord: Optional[str] = None


@dataclass(init=True)
class GPAccessRequestSentForAuthorisation(AccessRequestReadyForAuthorisation):
    GPEmailAddresses: Optional[list[str]] = None
    S3Key: Optional[str] = None


def put_item(serialized_data: dict) -> None:
    """Put an item into the DynamoDB table

    Args:
        serialized_data (dict): The data to be put into the table
    """
    dynamodb.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item=serialized_data,
    )


def get_item(reference_code: str) -> dict:
    """Get an item from the DynamoDB table

    Args:
        reference_code (str): The reference code to get the item for

    Returns:
        dict: The item from the table
    """
    response = dynamodb.get_item(
        TableName=DYNAMODB_TABLE_NAME, Key={"ReferenceCode": {"S": reference_code}}
    )
    return deserialize_data(response["Item"])


def get_time_to_live() -> int:
    return int(time()) + 86000  # One Day


def serialize_list(data: list) -> dict:
    """Serialize the data ready for DynamoDB

    Args:
        data (list): The data to be serialized

    Returns:
        dict: The serialized data
    """
    return TypeSerializer().serialize(data)


def serialize_dict(data: dict) -> dict:
    """Serialize the data ready for DynamoDB

    Args:
        data (dict): The data to be serialized

    Returns:
        dict: The serialized data
    """
    return {k: TypeSerializer().serialize(v) for k, v in data.items()}


def deserialize_data(data: dict) -> dict:
    """Deserialize the data ready for DynamoDB

    Args:
        data (dict): The data to be deserialized

    Returns:
        dict: The deserialized data
    """
    return {k: TypeDeserializer().deserialize(v) for k, v in data.items()}
