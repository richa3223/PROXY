"""
Test that an insert or update to a DynamoDB record
results in an event being published to the Event Bus
"""

from datetime import datetime
from json import loads
from logging import getLogger
from time import sleep
from uuid import uuid4

import pytest
from boto3 import Session, client

from ..helpers.environment_variables import AWS_REGION, WORKSPACE

logger = getLogger(__name__)

REFERENCE_CODE = str(uuid4())


@pytest.mark.parametrize(
    "application_status",
    [
        "ACCESS_REQUEST_CREATED",
        "ACCESS_REQUEST_READY_FOR_AUTHORISATION",
        "GP_AUTHORISATION_REQUEST_CREATED",
    ],
)
def test_dynamodb_create_to_eventbridge_event(application_status: str):
    """
    Check that an event is published for record creation,
    transition from creation to updated and from updated
    to updated.
    """
    log_client = client("logs")

    seconds_since_epoch = int(datetime.now().timestamp())
    start_time = seconds_since_epoch * 1000

    # Initialize a session using Amazon DynamoDB Streams
    session = Session(region_name=AWS_REGION)

    table_name = f"{WORKSPACE}-pvrs-patient-relationship"

    # Initialize DynamoDB resource
    dynamodb = session.resource("dynamodb")

    # Specify the table
    table = dynamodb.Table(table_name)

    # Define the record to be inserted with a given primary key
    item = {
        "ReferenceCode": REFERENCE_CODE,
        "ApplicationStatus": application_status,
        # Add more attributes as needed
    }

    # Insert the item into the table
    response = table.put_item(Item=item)
    logger.info(response)

    log_group_name = "/aws/events/main-event-bus-logs"
    log_stream_name = "event-bus-logs"
    log_events = []
    seconds = 10
    logger.info(f"Checking for log events in {log_group_name}")
    for counter in range(18):
        log_events = log_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startTime=start_time,
        )
        found = False
        if log_events["events"]:
            for event in log_events["events"]:
                message = loads(event["message"])
                try:
                    if (
                        message["detail-type"] == "Event from aws:dynamodb"
                        and message["detail"]["referenceCode"] == REFERENCE_CODE
                        and message["detail"]["eventType"] == application_status
                    ):
                        logger.info(f"{message['time']}:{message}")
                        found = True
                except KeyError as e:
                    logger.debug(f"{e}:{message}")
            if found:
                break
        logger.info(f"Counter: {counter}, Sleeping for {seconds} seconds...")
        sleep(seconds)
        logger.info(f"Waited for {(counter+1)*seconds} seconds...")
    else:
        logger.error("Timed out waiting for log events to be available")
        raise TimeoutError("Timed out waiting for log events to be available.")
