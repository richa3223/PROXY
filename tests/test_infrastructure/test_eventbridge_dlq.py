"""
Test sending of failed event delivery on main-event-bus to Dead Letter Queue
"""

from json import dumps, loads
from logging import getLogger
from time import sleep

import pytest
from botocore.exceptions import ClientError, UnauthorizedSSOTokenError

from ..helpers.aws.eventbridge import (
    DLQ_ARN,
    DLQ_URL,
    EVENT_BUS_NAME,
    FIREHOSE_ARN,
    NUM_EVENTS,
    TAGS,
    TEST_EVENT_BUS_ROLE_NAME,
    TEST_RULE_NAME,
    TEST_SOURCE,
    TEST_TARGET_NAME,
    WAIT_FOR_RULE,
    eventbridge,
    iam,
    put_events,
    sqs,
)

logger = getLogger(__name__)


class TestDLQ:
    """Test delivery to the event bus Dead Letter Queue"""

    @pytest.fixture
    def _run_test(self):
        """Run the test"""
        # Set up
        test_event_bus_role_arn = ""
        try:
            create_iam_role_response = iam.create_role(
                RoleName=TEST_EVENT_BUS_ROLE_NAME,
                AssumeRolePolicyDocument=dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "events.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    }
                ),
                Description="Test event bus delivery to DLQ",
                MaxSessionDuration=3600,
                Tags=TAGS,
            )
            test_event_bus_role_arn = create_iam_role_response["Role"]["Arn"]
            logger.info(f"Created iam role {test_event_bus_role_arn=}")
        except ClientError as error:
            logger.warning(error)

        try:
            test_event_bus_role_arn = (
                test_event_bus_role_arn
                if test_event_bus_role_arn
                else iam.get_role(RoleName=TEST_EVENT_BUS_ROLE_NAME)["Role"]["Arn"]
            )
            logger.info(f"Using existing iam role {test_event_bus_role_arn=}")

            put_rule_response = eventbridge.put_rule(
                Name=TEST_RULE_NAME,
                EventPattern='{"source":[{"prefix":""}]}',
                State="ENABLED",
                Description="Short lived rule for testing",
                Tags=TAGS,
                EventBusName=EVENT_BUS_NAME,
            )
            logger.info(f'Created EventBridge rule {put_rule_response["RuleArn"]}')

            put_targets_response = eventbridge.put_targets(
                Rule=TEST_RULE_NAME,
                EventBusName=EVENT_BUS_NAME,
                Targets=[
                    {
                        "Id": TEST_TARGET_NAME,
                        "Arn": FIREHOSE_ARN,
                        "RoleArn": test_event_bus_role_arn,
                        "DeadLetterConfig": {"Arn": DLQ_ARN},
                        "RetryPolicy": {
                            "MaximumRetryAttempts": 1,
                            "MaximumEventAgeInSeconds": 60,
                        },
                    },
                ],
            )

            logger.info(
                f'Created EventBridge target. FailedEntries: {put_targets_response["FailedEntryCount"]}'
            )

        except ClientError as error:
            logger.error(error)

        except UnauthorizedSSOTokenError as error:
            logger.error(error)

        logger.info("Allow a short period of time for changes to take effect.")
        # See:
        # https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-troubleshooting.html#eb-rule-does-not-match
        for i in range(WAIT_FOR_RULE, 0, -10):
            logger.info(f"Waiting for {i} seconds")
            sleep(10)
        yield
        # Clean up
        try:
            remove_target_response = eventbridge.remove_targets(
                Rule=TEST_RULE_NAME,
                EventBusName=EVENT_BUS_NAME,
                Ids=[
                    TEST_TARGET_NAME,
                ],
            )
            logger.info(
                f'Removed eventbridge target: {remove_target_response["ResponseMetadata"]["HTTPStatusCode"]}',
            )
            delete_rule_response = eventbridge.delete_rule(
                Name=TEST_RULE_NAME,
                EventBusName=EVENT_BUS_NAME,
            )
            logger.info(
                f'Removed eventbridge rule: {delete_rule_response["ResponseMetadata"]["HTTPStatusCode"]}'
            )
        except Exception as error:
            logger.error(error)

        try:
            delete_iam_response = iam.delete_role(RoleName=TEST_EVENT_BUS_ROLE_NAME)
            logger.info(
                f'Removed role: {delete_iam_response["ResponseMetadata"]["HTTPStatusCode"]}',
            )
            sqs.purge_queue(QueueUrl=DLQ_URL)
            logger.info("Purged DLQ")
        except Exception as error:
            logger.error(error)

    def test_dlq(self, _run_test) -> None:
        """Send events to the bus"""
        test_run_id = put_events("should go to the DLQ")
        logger.info("Get messages from the DLQ")
        messages = []
        done = False
        poll_count = 100
        while not done:
            if poll_count == 0:
                assert False, "Gave up looking for messages in DLQ"

            logger.info(f"Polling for messages: {poll_count} polls remaining")
            message = sqs.receive_message(
                QueueUrl=DLQ_URL,
                AttributeNames=["All"],
                MaxNumberOfMessages=1,
                MessageAttributeNames=["All"],
                WaitTimeSeconds=2,
            )
            try:
                body = loads(message["Messages"][0]["Body"])

                if body["source"] == TEST_SOURCE:
                    detail = body["detail"]
                    if detail["test_run"] == test_run_id:
                        messages.append(detail)
                        receipt_handle = message["Messages"][0]["ReceiptHandle"]
                        delete_message = sqs.delete_message(
                            QueueUrl=DLQ_URL, ReceiptHandle=receipt_handle
                        )
                        logger.info(
                            f'Deleted message - status code: {delete_message["ResponseMetadata"]["HTTPStatusCode"]}',
                        )

                    if len(messages) == NUM_EVENTS:
                        logger.info("Messages sent to DLQ:")
                        for i in messages:
                            logger.info(i)
                        done = True

            except KeyError:
                logger.info("No messages")

            poll_count -= 1
