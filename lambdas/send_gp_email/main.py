from http import HTTPStatus
from json import loads
from os import getenv
from typing import Optional

from spine_aws_common import LambdaApplication

from lambdas.utils.aws.dynamodb import AccessRequestStates, get_item, update_status
from lambdas.utils.aws.s3 import get_s3_file
from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.email import send_email
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log


class SendGPEmail(LambdaApplication):
    """Send an email using NHSUK SendNHSMail API"""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

        self.EMAIL_BUCKET = getenv("HYDRATED_EMAIL_BUCKET")

        self.secret_manager = SecretManager("SEND_NHS_MAIL_API_CREDENTIALS")

    def start(self) -> None:
        """Handles the lambda actions"""
        try:
            event_contents = self.__get_event_contents()

            # Verify the event type if correct
            if self.__event_type_is_correct(event_contents) == False:
                return self.__result_handler(
                    HTTPStatus.BAD_REQUEST, "Event status is not valid."
                )

            # Get the record from dynamo db
            rec = self.__get_item(event_contents)
            if "GPEmailAddresses" not in rec:
                return self.__result_handler(
                    HTTPStatus.BAD_REQUEST, "Email address is not valid"
                )
            # Get the email
            email_contents = self.__load_email_content(rec)
            # Send the email
            email_addr = rec["GPEmailAddresses"]["L"]
            self.send_gp_email(email_addr, email_contents)
            # Update status to mark it as sent
            self.__update_status(event_contents)

            # Completed successfully - return
            return self.__result_handler(200, "OK")

        except Exception as ex:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Unexpected error in processing.",
                    "error": ex,
                },
            )
            self.__result_handler(HTTPStatus.INTERNAL_SERVER_ERROR, str(ex))

    def __get_item(self, rec: dict) -> dict:
        """Retrieves the required record from Dynamo Db

        Args:
            rec (dict): Input event details

        Returns:
            dict: Retrieved record from Dynamo Db
        """
        return get_item(rec["detail"]["referenceCode"])

    def __load_email_content(self, rec: dict) -> dict:
        """Load the email contents from S3

        Args:
            rec (dict): Event contents

        Returns:
            dict: Email contents
        """
        s3_loc = rec["S3Key"]["S"]
        write_log(
            "INFO",
            {"info": f"Requesting file {s3_loc} from {self.EMAIL_BUCKET}"},
        )
        file_contents = get_s3_file(self.EMAIL_BUCKET, s3_loc)
        return loads(file_contents)

    def __get_event_contents(self) -> dict:
        """Retrieve event parameters

        Returns:
            dict: Event contents
        """
        return self.event

    def __event_type_is_correct(self, event_contents: dict) -> bool:
        """Check event status

        Args:
            event_contents (dict): Lambda event contents.

        Returns:
            bool: True if the event is valid, False otherwise
        """
        return (
            event_contents["detail"]["eventType"]
            == AccessRequestStates.GP_AUTH_REQUEST_CREATED.value
        )

    def __result_handler(self, status_code: int, msg: str) -> None:
        """Handles the result event

        Args:
            status_code (int): Status code result
            msg (str): Result message
        """
        self.response = {"statusCode": status_code, "body": {"message": msg}}

    def __update_status(self, rec: dict) -> None:
        """Updates the status of the dynamo db record

        Args:
            rec (dict): Event details
        """
        update_status(
            rec["detail"]["referenceCode"], AccessRequestStates.ACCESS_REQUEST_SENT
        )

    def send_gp_email(self, email_addr: list, contents: dict) -> Optional[str]:
        """Send an email using NHSUK SendNHSMail API

        Args:
            event_contents (dict): The contents of the event

        Returns:
            str: Success message
        """
        api_url = self.secret_manager.get_secret("API_URL")
        subscription_key = self.secret_manager.get_secret("SUBSCRIPTION_KEY")

        for email in email_addr:
            to_email_address = email["S"]
            subject = contents["email_subject"]
            body = contents["email_body"]

            write_log("INFO", {"info": f"Sending email to : {to_email_address}"})
            # Send mail raises exception on failed emails
            # Allow exception to bubble up as it cause lambda to fail and rety
            send_email(to_email_address, subject, body, api_url, subscription_key)
        return "Email sent successfully."


send_gp_email = SendGPEmail(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """

    Args:
        event (dict): Parameters to supply to SendGPEmail
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return send_gp_email.main(event, context)
