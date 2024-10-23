"""Trigger a Slack alert"""

import traceback
from json import dumps, loads
from os import getenv

from boto3 import client

from lambdas.utils.logging.logger import write_log

EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME = "expiry_warning_slack_alert_template.json"
UNABLE_TO_PROCESS_CERTIFICATE_SLACK_ALERT_TEMPLATE_NAME = (
    "unable_to_process_certificate.json"
)


def hydrate_slack_alert_and_send(file_name: str, content_to_replace: dict) -> None:
    """Hydrate a slack alert message and send it

    Args:
        file_name (str): The file name
        content_to_replace (dict): The content to replace
    """
    slack_message = hydrate_slack_alert_message(file_name, content_to_replace)
    send_slack_alert(slack_message)


def send_slack_alert(message: dict) -> None:
    """Send a Slack alert

    Args:
        message (dict): The message to send
    """
    write_log("INFO", {"info": "Sending Slack alert"})
    try:
        lambda_client = client("lambda")
        response = lambda_client.invoke(
            FunctionName=getenv("SLACK_ALERTS_LAMBDA_FUNCTION_NAME"),
            InvocationType="RequestResponse",
            Payload=dumps(message),
        )
        write_log("DEBUG", {"info": f"Message sent to Slack: {message}"})
        write_log("DEBUG", {"info": f"Response from Slack: {response}"})
    except Exception as error:
        write_log(
            "ERROR",
            {
                "info": f"An error occurred in the Slack alert lambda: {error=}",
                "error": traceback.format_exc(),
            },
        )


def hydrate_slack_alert_message(file_name: str, content_to_replace: dict) -> str:
    """Hydrate a slack alert message from a template

    Args:
        file_name (str): The file name
        content_to_replace (dict): The content to replace

    Returns:
        str: The Slack alert message
    """
    slack_message_template = get_slack_message_template(file_name)
    for key, value in content_to_replace.items():
        slack_message_template = slack_message_template.replace(f"<{key}>", value)

    return loads(slack_message_template)


def get_slack_message_template(file_name: str) -> str:
    """Get the Slack message

    Args:
        file_name (str): The name of the file to load

    Returns:
        str: slack template
    """
    with open(
        f"lambdas/raise_certificate_alert/slack_alert_templates/{file_name}", "r"
    ) as file:
        return file.read()
