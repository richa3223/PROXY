"""
Test generation of CloudWatch metrics from EventBridge
"""

from copy import deepcopy
from json import dumps, loads
from logging import getLogger

from botocore.exceptions import ClientError
from pytest import fixture

from ..helpers.aws.eventbridge import (
    DLQ_URL,
    EVENT_BUS_ARN,
    EVENT_BUS_NAME,
    NUM_EVENTS,
    eventbridge,
    put_events,
    sqs,
)

SPLUNK_INSTRUCTIONS = """
Now go to https://nhsdigital.splunkcloud.com/en-US/app/nhse_vrs_all_sh_all_viz/search
and search for `index="operational_vrs_dev" source="eu-west-2:AWS/Events" %s`
"""

logger = getLogger(__name__)


@fixture(scope="function")
def _disable_renable_dlq():
    """
    Disable ability to send events to DLQ before running
    the test and then reenable once test has finished even if
    test fails.
    """
    attributes = sqs.get_queue_attributes(QueueUrl=DLQ_URL, AttributeNames=["Policy"])
    policy = loads(attributes["Attributes"]["Policy"])
    test_policy = deepcopy(policy)

    test_policy["Statement"][0]["Action"] = "sqs:ReceiveMessage"

    # Change access policy so DLQ will not work

    set_policy_response = sqs.set_queue_attributes(
        QueueUrl=DLQ_URL, Attributes={"Policy": dumps(test_policy)}
    )
    logger.info(
        "Changed DLQ permissions:%s",
        set_policy_response["ResponseMetadata"]["HTTPStatusCode"],
    )

    yield

    # Set policy back to original

    set_policy_response = sqs.set_queue_attributes(
        QueueUrl=DLQ_URL, Attributes={"Policy": dumps(policy)}
    )
    logger.info(
        "Reverted DLQ permissions:%s",
        set_policy_response["ResponseMetadata"]["HTTPStatusCode"],
    )


def test_invalid_dlq(_disable_renable_dlq):
    """
    Test metrics when Event Bus cannot deliver
    to DLQ
    """

    put_events("should not go to the DLQ")
    logger.info(SPLUNK_INSTRUCTIONS, "InvocationsFailedToBeSentToDlq")


@fixture(scope="function")
def _disable_renable_put_events():
    """
    Disable ability to put events to EventBridge before running
    the test and then reenable once test has finished even if
    test fails.
    """
    statement_id = "DenyToPutEvents"

    statement = {
        "Version": "2012-10-17",
        "Statement": {
            "Sid": statement_id,
            "Effect": "Deny",
            "Principal": "*",
            "Action": "events:PutEvents",
            "Resource": EVENT_BUS_ARN,
        },
    }

    # Convert the statement to JSON
    policy = dumps(statement)

    put_permission_response = eventbridge.put_permission(
        EventBusName=EVENT_BUS_NAME, Policy=policy
    )
    logger.info(
        "Changed EventBridge permissions:%s",
        put_permission_response["ResponseMetadata"]["HTTPStatusCode"],
    )

    yield

    remove_permission_response = eventbridge.remove_permission(
        EventBusName=EVENT_BUS_NAME,
        StatementId=statement_id,
        RemoveAllPermissions=False,
    )
    logger.info(
        "Changed EventBridge permissions:%s",
        remove_permission_response["ResponseMetadata"]["HTTPStatusCode"],
    )


def test_failed_put_events(_disable_renable_put_events):
    """
    Test generation of PutEventsApproximateFailedCount metric
    """

    for _ in range(NUM_EVENTS):
        try:
            put_events("should not put events", 1)

        except ClientError as error:
            if str(error).find("AccessDeniedException") > -1:
                logger.info(error)
            else:
                raise

    logger.info(SPLUNK_INSTRUCTIONS, "PutEventsApproximateFailedCount")
