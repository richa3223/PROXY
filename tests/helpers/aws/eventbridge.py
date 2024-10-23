"""
Helper constants, clients and function used in the eventbridge tests
"""

from datetime import datetime
from json import dumps
from logging import getLogger
from time import sleep
from uuid import uuid4

from boto3 import client

from ..environment_variables import AWS_ACCOUNT_ID, AWS_REGION, WORKSPACE

eventbridge = client("events", region_name=AWS_REGION)
sqs = client("sqs", region_name=AWS_REGION)
iam = client("iam", region_name=AWS_REGION)
sts = client("sts", region_name=AWS_REGION)

# pylint: disable=line-too-long
FIREHOSE_ARN = f"arn:aws:firehose:{AWS_REGION}:{AWS_ACCOUNT_ID}:deliverystream/main-standard-audit-kinesis-firehose"
EVENT_BUS_ARN = f"arn:aws:events:{AWS_REGION}:{AWS_ACCOUNT_ID}:event-bus/main-event-bus"

EVENT_BUS_NAME = f"{WORKSPACE}-event-bus"
EVENT_BUS_RULE_NAME = "main-audit-rule"
TEST_EVENT_BUS_ROLE_NAME = "test-event-bus"

DLQ_ARN = f"arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:main-event-bus-dlq"
DLQ_URL = f"https://sqs.{AWS_REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/main-event-bus-dlq"

TEST_RULE_NAME = "test_dlq"
TEST_TARGET_NAME = "test_standard_firehose"

NUM_EVENTS = 10
WAIT_FOR_RULE = 120

TEST_SOURCE = "dlq_test"

TAGS = [
    {"Key": "purpose", "Value": "testing"},
    {"Key": "description", "Value": "Short lived resource for testing"},
    {"Key": "TestSource", "Value": "dlq_test"},
    {"Key": "TestSuite", "Value": "test_infrastructure"},
]

logger = getLogger(__name__)


def put_events(message, num_events=NUM_EVENTS) -> str:
    """
    Put events to the bus
    """
    test_run_id = str(uuid4())
    logger.info("Test run: %s", test_run_id)

    for i in range(num_events):
        entries = []
        detail = dumps(
            {
                "content": f"event {i:04d} {message}",
                "test_run": test_run_id,
                "event_num": i,
            }
        )
        entries.append(
            {
                "Time": datetime.now(),
                "Source": TEST_SOURCE,
                "DetailType": "test",
                "Detail": detail,
                "EventBusName": EVENT_BUS_NAME,
            },
        )
        event_response = eventbridge.put_events(
            Entries=entries,
        )
        logger.info(str(detail))
        logger.info(str(event_response))
        sleep(1)

    return test_run_id
