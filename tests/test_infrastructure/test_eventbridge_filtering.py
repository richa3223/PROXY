"""Test the filtering of Validation Result events received by the eventbridge"""

from datetime import datetime, timezone
from json import dumps, loads
from logging import getLogger
from re import split
from time import sleep
from uuid import uuid4

import pytest
from boto3 import client

from ..helpers import ENVIRONMENT, WORKSPACE

TAGS = {
    "Environment": ENVIRONMENT,
    "Workspace": WORKSPACE,
    "Test": "Infrastructure",
    "TestClass": "TestEventbridgeFiltering",
}

DETAIL_TYPES = ["Validation Successful", "Validation Failed", "Validation Errored"]

log_client = client("logs")
eventbridge_client = client("events")
iam_client = client("iam")
s3_client = client("s3")

logger = getLogger(__name__)


def _event_detail() -> dict:
    """Generate the detail section."""
    event = {
        "Detail": {
            "metadata": {
                "client-key": "739d1cb1-4eba-4201-934f-d354a39e973c",
                "correlation-id": str(uuid4()),
                "created": "2024-06-06T11:41:52.931714",
                "request-id": "7e1a8ef9-d994-4f81-b21f-0ffe75876fa3",
            },
            "sensitive": {
                "patient-identifier": "",
                "proxy-identifier": "9730675929",
            },
            "standard": {
                "proxy-identifier-type": "NHS Number",
                "relationship-type": "MTH",
                "validation-result-info": {
                    "VALIDATED_RELATIONSHIP": "Validated Relationship"
                },
            },
        },
    }
    return event


def test_audit_rule_matches_relationship_validation_events():
    """
    Test that we are only auditing relationship validation events
    """
    expected = {"detail-type": DETAIL_TYPES}

    response = eventbridge_client.describe_rule(
        Name=f"{WORKSPACE}-audit-rule", EventBusName=f"{WORKSPACE}-event-bus"
    )
    assert response["Name"] == f"{WORKSPACE}-audit-rule"
    assert loads(response["EventPattern"]) == expected


def _list_filtered_s3_objects(
    bucket_name: str, prefix: str, start_datetime: datetime
) -> list:
    """
    Get list of filtered S3 Objects
    """
    # Initialize a paginator to handle large lists of objects
    paginator = s3_client.get_paginator("list_objects_v2")

    # Set the initial parameters
    params = {"Bucket": bucket_name}
    if prefix:
        params["Prefix"] = prefix

    # Use the paginator to retrieve objects
    page_iterator = paginator.paginate(**params)

    # Filter objects based on time
    filtered_objects = []
    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                last_modified = obj["LastModified"]
                if start_datetime <= last_modified:
                    filtered_objects.append(obj)

    return filtered_objects


def _lookup_event_in_bucket(
    detail_type: str, event_detail: dict, start_datetime: datetime
) -> bool:
    """
    Lookup an event in the audit bucket
    """
    bucket_name = f"{WORKSPACE}-{ENVIRONMENT}-queryable-audit-events-bucket"

    # The month/day value needs to be 2 digits for forming the S3 key
    month_prefix = str(start_datetime.month).zfill(2)
    day_prefix = str(start_datetime.day).zfill(2)
    prefix = f"{detail_type}/year={start_datetime.year}/month={month_prefix}/day={day_prefix}/"

    event_steam_pattern = r"(?<=\})(?=\{)"

    found = False
    retry = 20
    seconds = 10

    while not found:
        file_list = _list_filtered_s3_objects(bucket_name, prefix, start_datetime)
        for file in file_list:
            response = s3_client.get_object(Bucket=bucket_name, Key=file["Key"])
            content = response["Body"].read().decode("utf-8")
            event_strings = split(event_steam_pattern, content)
            for event_string in event_strings:
                event = loads(event_string)

                if (
                    event["detail"]["metadata"]["correlation-id"]
                    == event_detail["Detail"]["metadata"]["correlation-id"]
                ):
                    logger.info(
                        "Found event with correlation-id:"
                        f"{event_detail['Detail']['metadata']['correlation-id']}"
                    )
                    found = True
                    break

            if found:
                break
        if not found:
            retry -= 1
            if retry < 0:
                break
            logger.info(f"Counter: {retry}, Sleeping for {seconds} seconds...")
            sleep(seconds)

    return found


@pytest.mark.parametrize("detail_type", DETAIL_TYPES)
def test_validation_result_sent_to_audit(detail_type: list):
    """
    On sending a Validation Successful event to the eventbridge, we
    want to show that it is correctly sent to audit following the
    rule we have implemented.
    """

    now = datetime.now(timezone.utc)
    event_detail = _event_detail()
    entries = [
        {
            "Time": now,
            "Source": "Validation Service",
            "Resources": [
                "string",
            ],
            "DetailType": detail_type,
            "Detail": dumps(event_detail["Detail"]),
            "EventBusName": f"{WORKSPACE}-event-bus",
        },
    ]
    response = eventbridge_client.put_events(Entries=entries)
    assert response["FailedEntryCount"] == 0
    logger.info(f"Put {entries} to event bus")

    found = _lookup_event_in_bucket(detail_type, event_detail, now)

    assert found, (
        "Validation event not found in audit bucket for "
        f"correlation-id:{event_detail['Detail']['metadata']['correlation-id']}"
    )


@pytest.mark.parametrize("detail_type", DETAIL_TYPES)
def test_other_event_not_sent_to_audit(detail_type: list):
    """
    Testing that invalid events are not sent to audit.
    """
    now = datetime.now(timezone.utc)
    event_detail = _event_detail()
    invalid_detail_type = "not-a-validation-event"
    resp = eventbridge_client.put_events(
        Entries=[
            {
                "Time": now,
                "Source": "test",
                "Resources": ["string"],
                "DetailType": invalid_detail_type,
                "Detail": dumps(event_detail["Detail"]),
                "EventBusName": f"{WORKSPACE}-event-bus",
            }
        ]
    )
    assert resp["FailedEntryCount"] == 0
    found = _lookup_event_in_bucket(detail_type, event_detail, now)
    assert not found, "Event is not filtered."
