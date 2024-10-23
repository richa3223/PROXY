import traceback
from json import loads
from os import getenv

from spine_aws_common import LambdaApplication

from lambdas.utils.aws.s3 import get_s3_file
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log


class GetEmailTemplate(LambdaApplication):

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Get Email Template"""
        try:
            self.response = loads(self.get_file_contents())
            write_log("INFO", {"info": "Email created successfully"})
        except Exception as error:  # pylint: disable=broad-except
            write_log(
                "ERROR",
                {
                    "info": f"Error creating email - {error}",
                    "error": traceback.format_exc(),
                },
            )
            raise error

    def get_file_contents(self) -> str:
        """Get the contents of a file from an S3 bucket

        Returns:
            str: The contents of the file
        """
        template_name = self.get_email_template_name(
            self.event.get("template_identifier")
        )
        return get_s3_file(
            bucket=getenv("EMAIL_TEMPLATE_BUCKET"), file_name=template_name
        )

    def get_email_template_name(self, template_identifier) -> str:
        """Get the email template name

        Args:
            template_identifier (str): The template identifier

        Returns:
            str: The template name
        """
        template_name = ""
        if template_identifier == "adult_to_child":
            template_name = "adult_to_child_template.json"
        else:
            raise ValueError("Invalid template name")
        return template_name


get_email_template = GetEmailTemplate(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """

    Args:
        event (dict): Parameters to supply to GetEmailTemplate
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return get_email_template.main(event, context)
