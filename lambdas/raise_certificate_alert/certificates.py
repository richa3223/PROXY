"""Check the expiry date of a certificates"""

from datetime import datetime, timedelta
from os import getenv
from typing import Optional
from zoneinfo import ZoneInfo

from boto3 import client
from cryptography import x509

from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.logging.logger import write_log

from .email import (
    CERTIFICATE_EXPIRY_WARNING_MESSAGE,
    CERTIFICATE_EXPIRY_WARNING_SUBJECT,
    hydrate_email_alert_and_send,
)
from .slack import (
    EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME,
    hydrate_slack_alert_and_send,
)

THREE_MONTHS = timedelta(days=90)
TWO_MONTHS = timedelta(days=60)
ONE_MONTH = timedelta(days=30)
TWO_WEEKS = timedelta(days=14)
ONE_WEEK = timedelta(days=7)


def list_certificates(s3_client: client, bucket_name: str) -> list[str]:
    """List the certificates in the bucket

    Args:
        s3_client (client): The S3 boto3 client
        bucket_name (str): The bucket name

    Returns:
        list[str]: A list of pem file names
    """
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = response["Contents"]
    return [file["Key"] for file in files if file["Key"].endswith(".pem")]


def get_certificate_from_s3(
    s3_client: client, bucket_name: str, key_name: str
) -> x509.Certificate:
    """Get the certificate from s3

    Args:
        s3_client (client): The S3 boto3 client
        bucket_name (str): The bucket name
        key_name (str): The key name

    Returns:
        x509.Certificate: The certificate
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=key_name)
    write_log("DEBUG", {"info": f"Response from S3: {response}"})
    file_contents = response["Body"].read()

    return x509.load_pem_x509_certificate(file_contents)


def get_certificate_expiry(certificate: x509.Certificate) -> timedelta:
    """Check the expiry date of a certificate

    Args:
        certificate (x509.Certificate): The certificate
    """
    not_after = certificate.not_valid_after_utc
    time_left = not_after - datetime.now(tz=ZoneInfo("UTC"))
    write_log("DEBUG", {"info": f"Time left: {time_left}"})
    return time_left


def check_certificate_expiry(
    certificate: x509.Certificate,
    cert_file_name: str,
    time_left: timedelta,
    email_secrets_manager: SecretManager,
) -> None:
    """Check the expiry date of a certificate

    Args:
        certificate (x509.Certificate): The certificate
        cert_file_name (str): The file name
        time_left (timedelta): The time left
        email_secrets_manager (SecretManager): The email secrets manager
    """

    def check_expiry_in_alert_period(period: timedelta) -> Optional[str]:
        """Check the expiry date of a certificate

        Args:
            period (timedelta): The period

        Returns: The message, None if no message
        """
        if time_left >= period and time_left < period + timedelta(days=1):
            return f"Expiry in {period.days} days"
        return None

    if (
        (message := check_expiry_in_alert_period(ONE_WEEK))
        or (message := check_expiry_in_alert_period(TWO_WEEKS))
        or (message := check_expiry_in_alert_period(ONE_MONTH))
        or (message := check_expiry_in_alert_period(TWO_MONTHS))
        or (message := check_expiry_in_alert_period(THREE_MONTHS))
    ):
        write_log(
            "WARNING",
            {"info": f"Certificate expiry warning for {cert_file_name}: {message}"},
        )

        # slack message and email
        hydrate_slack_alert_and_send(
            EXPIRY_WARNING_SLACK_ALERT_TEMPLATE_NAME,
            {
                "MESSAGE": f"Certificate expiry warning for *{cert_file_name}* - {message}",
                "ENVIRONMENT": getenv("ENVIRONMENT", "Unable to get environment"),
                "WORKSPACE": getenv("WORKSPACE", "Unable to get workspace"),
            },
        )
        hydrate_email_alert_and_send(
            CERTIFICATE_EXPIRY_WARNING_SUBJECT,
            CERTIFICATE_EXPIRY_WARNING_MESSAGE,
            {
                "MESSAGE": f"Certificate expiry warning for {cert_file_name} - {message}",
                "CERTIFICATE_NAME": cert_file_name,
                "ENVIRONMENT": getenv("ENVIRONMENT", "Unable to get environment"),
                "WORKSPACE": getenv("WORKSPACE", "Unable to get workspace"),
                "ISSUER": certificate.issuer.rfc4514_string(),
                "NOT_VALID_AFTER_UTC": str(certificate.not_valid_after_utc),
            },
            email_secrets_manager,
        )
    else:
        write_log(
            "INFO",
            {"info": f"{cert_file_name}: Certificate is still valid for {time_left}"},
        )
