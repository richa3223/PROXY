"""Slack alerts"""

from os import getenv

from aws_lambda_powertools import Logger
from requests import post

logger = Logger()


def slack_alerts(event: dict) -> None:
    """Sends a message to Slack

    Args:
        event (dict): Parameters to supply to SlackAlerts
    """
    try:
        # Consider any transformation of the event if not already a slack message
        send_slack_message(event)
    except Exception as error:
        logger.exception("Unable to send Slack alert")
        raise error


def send_slack_message(message: dict) -> None:
    """Sends a message to Slack

    Args:
        message (dict): Message to send to Slack
    """
    response = post(getenv("SLACK_WEBHOOK_URL"), json=message)
    logger.info(
        "Sent to Slack",
        status_code=response.status_code,
        reason=response.reason,
        text=response.text,
    )
    if response.status_code != 200:
        raise ValueError(
            f"Slack alert failed with {response.status_code=} {response.reason=}"
        )


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: dict) -> dict:
    """Sends a message to Slack

    Args:
        event (dict): Parameters to supply to SlackAlerts
        context (LambdaContext): Lambda context

    Returns:
        dict: Generated response or error.
    """
    slack_alerts(event)
    return {"statusCode": 200, "body": "Slack alerts sent"}
