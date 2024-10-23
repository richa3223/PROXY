import traceback
from os import environ
from uuid import uuid4

from boto3.dynamodb.types import TypeDeserializer
from spine_aws_common import LambdaApplication

from lambdas.create_merged_email.email import Email
from lambdas.utils.aws.s3 import put_s3_file
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log

deserializer = TypeDeserializer()


class CreateMergedEmail(LambdaApplication):

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Create Merged Email"""
        try:
            # Get Email Variables
            email = self.__create_email()
            item = self.__deserialize_dynamodb_item(self.event.get("Item"))

            reference_code = item.get("ReferenceCode")
            ods_code = self.__get_ods_code(self.event.get("PatientPDSPatientRecord"))

            file_name = f"{reference_code}-{str(uuid4())}.json"
            # Update Email with variables
            email.replace_with_variables(
                {"reference_code": reference_code, "ods_code": ods_code}
            )
            # Upload Email to S3
            put_s3_file(
                environ["HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET"],
                file_name,
                email.to_json(),
            )
            self.response = {"file_name": file_name}
            write_log("INFO", {"info": "Email created successfully"})
        except Exception as error:  # pylint: disable=broad-except
            write_log(
                "ERROR",
                {
                    "info": f"Error merging email template and content - {error}",
                    "error": traceback.format_exc(),
                },
            )
            raise error

    def __create_email(self) -> Email:
        email_details = self.event.get("email_details").get("email_content")
        return Email(
            email_subject=email_details.get("email_subject"),
            email_body=email_details.get("email_body"),
        )

    def __deserialize_dynamodb_item(self, dynamodb_item: dict) -> dict:
        """Deserialize DynamoDB item

        Args:
            dynamodb_item (dict): DynamoDB item to deserialize

        Returns:
            dict: Deserialized item
        """
        return {k: deserializer.deserialize(v) for k, v in dynamodb_item.items()}

    def __get_ods_code(self, patient_pds_patient_record: dict) -> str:
        """Get ODS Code from Patient PDS Patient Record

        Args:
            patient_pds_patient_record (dict): Patient PDS Patient Record (deserialized from DynamoDB)

        Returns:
            str: ODS Code
        """
        try:
            return (
                patient_pds_patient_record.get("generalPractitioner")[0]
                .get("identifier")
                .get("value")
            )
        except Exception:  # pylint: disable=broad-except
            write_log(
                "ERROR",
                {
                    "info": "Odscode not found in Patient PDS Patient Record (DynamoDB Item)",
                    "error": traceback.format_exc(),
                },
            )
            return "Unknown"


create_merged_email = CreateMergedEmail(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """

    Args:
        event (dict): Parameters to supply to CreateMergedEmail
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return create_merged_email.main(event, context)
