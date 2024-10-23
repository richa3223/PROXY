"""Email alerts"""

from os import getenv

from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.email import send_email
from lambdas.utils.logging.logger import write_log

CERTIFICATE_EXPIRY_WARNING_SUBJECT = (
    " Certificate: (CERTIFICATE_NAME) in (ENVIRONMENT) is about to expire!"
)
CERTIFICATE_EXPIRY_WARNING_MESSAGE = "<!doctypehtml><html lang=en><meta charset=UTF-8><title>Expiry Warning</title><p>(MESSAGE)<p>Environment=(ENVIRONMENT)<p>Workspace=(WORKSPACE)<p>Issuer=(ISSUER)<p>Not valid after UTC=(NOT_VALID_AFTER_UTC)"


def hydrate_email_alert_and_send(
    subject: str, template: str, content_to_replace: dict, secret_manager: SecretManager
) -> None:
    """Hydrate an email alert message and send it

    Args:
        template (str): The template to use (Can be HTML)
        content_to_replace (dict): The content to replace

    """
    email_subject, email_message = hydrate_email_alert_message(
        subject, template, content_to_replace
    )
    write_log("DEBUG", {"info": f"Email message: {email_message}"})
    email_alert(email_subject, email_message, secret_manager)


def email_alert(subject: str, message: str, secret_manager: SecretManager) -> None:
    """Send an email alert

    Args:
        subject (str): Subject of the email
        message (str): Message of the email (Can be HTML)
        secret_manager (SecretManager): Secret manager to retrieve secrets
    """
    try:
        response = send_email(
            to_email_address=getenv("TEAM_EMAIL"),
            subject=subject,
            body=message,
            api_url=secret_manager.get_secret("API_URL"),
            subscription_key=secret_manager.get_secret("SUBSCRIPTION_KEY"),
        )
        write_log("DEBUG", {"info": f"Email response: {response}"})
    except ValueError as error:
        write_log("ERROR", {"info": "Error sending email", "error": str(error)})


def hydrate_email_alert_message(
    subject: str, template: str, content_to_replace: dict
) -> tuple[str, str]:
    """Hydrate a email alert message from a template

    Args:
        subject (str): Subject of the email
        template (str): The template to use (Can be HTML)
        content_to_replace (dict): The content to replace

    Returns:
        tuple[str,str]: The email subject and content
    """
    for key, value in content_to_replace.items():
        subject = subject.replace(f"({key})", value)
        template = template.replace(f"({key})", value)

    return subject, template
