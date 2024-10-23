"""Raise an alert to warn of TLS Certificate expiration"""

import traceback
from os import getenv

from boto3 import client
from spine_aws_common import LambdaApplication

from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.email import send_email
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log

from .certificates import (
    check_certificate_expiry,
    get_certificate_expiry,
    get_certificate_from_s3,
    list_certificates,
)
from .slack import (
    UNABLE_TO_PROCESS_CERTIFICATE_SLACK_ALERT_TEMPLATE_NAME,
    hydrate_slack_alert_and_send,
)


class RaiseCertificateAlert(LambdaApplication):
    """Raise an alert to warn of TLS Certificate expiration"""

    secret_manager = SecretManager("SEND_NHS_MAIL_API_CREDENTIALS")

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> dict:
        """Check all certificates in the truststore bucket"""
        s3_client = client("s3")
        bucket_name = getenv("MTLS_CERTIFICATE_BUCKET_NAME")
        certificates = list_certificates(s3_client, bucket_name)
        for certificate_name in certificates:
            write_log("INFO", {"info": f"Checking certificate: {certificate_name}"})
            try:
                certificate = get_certificate_from_s3(
                    s3_client, bucket_name, certificate_name
                )
                time_left = get_certificate_expiry(certificate)
                check_certificate_expiry(
                    certificate, certificate_name, time_left, self.secret_manager
                )
            except Exception as error:
                write_log(
                    "ERROR",
                    {
                        "info": f"Error checking certificate, {certificate_name=}, {error=}",
                        "error": traceback.format_exc(),
                    },
                )
                hydrate_slack_alert_and_send(
                    UNABLE_TO_PROCESS_CERTIFICATE_SLACK_ALERT_TEMPLATE_NAME,
                    {"CERTIFICATE_NAME": certificate_name},
                )

        self.response = {"message": "Raise certificate alert lambda complete"}


raise_certificate_alert = RaiseCertificateAlert(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    return raise_certificate_alert.main(event, context)
