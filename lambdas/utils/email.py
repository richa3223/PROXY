from json import dumps

from requests import Response, post

from .logging.logger import write_log


def send_email(
    to_email_address: str, subject: str, body: str, api_url: str, subscription_key: str
) -> Response:
    """Send an email using NHSUK SendNHSMail API

    Args:
        to_email_address (str): Email address to send to
        subject (str): Email subject
        body (str): Email body
        api_url (str): URL to send email to
        subscription_key (str): API key
    """
    response = post(
        url=api_url,
        headers={"Subscription-Key": subscription_key},
        data=dumps(
            {
                "ToEmail": to_email_address,
                "subject": subject,
                "body": body,
            }
        ),
        timeout=10,
    )

    if response.status_code == 200:
        write_log("INFO", {"info": "Email sent successfully first time."})
    elif response.status_code == 202:
        write_log("INFO", {"info": "Email was queued."})
    else:
        write_log(
            "INFO",
            {
                "info": f"Email failed to be added to queue. Status code: {response.status_code}"
            },
        )
        write_log("INFO", {"info": f"Response: {response.text}"})
        raise ValueError("Email failed to be added to NHS Send Mail queue.")

    return response
