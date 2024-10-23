""" Lambda function to handle questionnaire responses """

import traceback
from json import loads

from spine_aws_common import LambdaApplication

from lambdas.utils.aws.dynamodb import AccessRequestStates, StoreAccessRequest, put_item
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds import errors
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper
from lambdas.utils.reference_code.ref_code import ReferenceCode
from lambdas.utils.validation.fhir_validate_questionnaire import (
    FHIRValidateQuestionnaire,
)

BAD_REQUEST = {
    "issue": [
        {
            "code": "invalid",
            "details": {
                "coding": [
                    {
                        "code": "BAD_REQUEST",
                        "display": "The request could not be processed.",
                        "system": "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode",
                        "version": "1",
                    }
                ]
            },
            "diagnostics": "The supplied input is not a valid FHIR QuestionnaireResponse.",
            "severity": "error",
        }
    ],
    "resourceType": "OperationOutcome",
}


class DynamoDBError(Exception):
    """Exception to handle DynamoDB errors"""


class CreateAccessRequest(LambdaApplication):
    """Lambda function to handle questionnaire responses"""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Process the questionnaire response"""
        try:
            write_log("DEBUG", {"info": "CreateAccessRequest : Start ran"})
            lambda_input = dict(self.event)

            validator = FHIRValidateQuestionnaire()

            if "body" in lambda_input and validator.validate_questionnaire_response(
                lambda_input["body"]
            ):
                body = lambda_input["body"]
                questionnaire = loads(body)
                reference_code = ReferenceCode().create_reference_code()
                self._save_to_dynamodb(questionnaire, reference_code)
                self.__handle_success(reference_code)
            else:
                self.__handle_failure(400, BAD_REQUEST)
        except Exception as error:
            operational_outcome = FHIRObjectMapper().create_operation_outcome(
                errors.INTERNAL_SERVER_ERROR
            )
            write_log(
                "ERROR",
                {
                    "info": f"Error while running creation of access request - {error}",
                    "error": traceback.format_exc(),
                },
            )
            self.__handle_failure(500, operational_outcome.as_json())

    def _save_to_dynamodb(
        self, questionnaire_response: dict, reference_code: str
    ) -> None:
        """
        Saves the questionnaire response to DynamoDB

        Args:
            response (dict): The questionnaire response
            reference_code (str): The reference code
        """
        max_retries = 3
        write_log("DEBUG", {"info": f"Saving to DynamoDB - {reference_code}"})
        for count in range(1, max_retries + 1):
            try:
                response = put_item(
                    StoreAccessRequest(
                        ReferenceCode=reference_code,
                        ProxyNHSNumber=self.__get_nhs_number(
                            questionnaire_response, "proxy_details"
                        ),
                        PatientNHSNumber=self.__get_nhs_number(
                            questionnaire_response, "patient_details"
                        ),
                        QuestionnaireData=questionnaire_response,
                        ApplicationStatus=AccessRequestStates.ACCESS_REQUEST_CREATED.value,
                    )
                )
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    break
            except Exception as error:
                write_log(
                    "ERROR",
                    {
                        "info": f"Error while saving to DynamoDB - {error}",
                        "error": traceback.format_exc(),
                    },
                )
            if count >= max_retries:
                raise DynamoDBError("Unable to save QuestionnaireResponse to DynamoDB")

    def __get_nhs_number(self, questionnaire: dict, link_id: str) -> str:
        """
        Extracts the NHS number from the response

        Args:
            questionnaire (dict): The questionnaire to extract the NHS number from
            link_id (str): The link id to extract the NHS number from

        Returns:
            str: The NHS number
        """
        attributes = [
            item["item"] for item in questionnaire["item"] if item["linkId"] == link_id
        ][0]
        nhs_number = [
            item["answer"][0]["valueString"]
            for item in attributes
            if item["linkId"] == "nhs_number"
        ][0]
        return nhs_number

    def __handle_failure(self, status_code: int, operation_outcome: dict):
        """
        Generates the output for when questionnaire response is not valid
        """

        self.response = {"statusCode": status_code, "body": operation_outcome}
        write_log("ERROR", {"info": "Invalid questionnaire response", "error": ""})

    def __handle_success(self, reference_code: str):
        """
        Generates the output for when questionnaire response is valid
        """
        response_to_send = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "information",
                    "code": "informational",
                    "details": {
                        "coding": [
                            {
                                "code": f"{reference_code}",
                                "display": f"{reference_code}",
                            }
                        ]
                    },
                }
            ],
        }
        write_log(
            "DEBUG",
            {
                "info": f"QuestionnaireResponse : Completed - Reference code {reference_code}"
            },
        )
        self.response = {"statusCode": 200, "body": response_to_send}


create_access_request = CreateAccessRequest(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """
    Generic handler to call the underlying handler

    Args:
        event (dict): Parameters to supply to CreateAccessRequest
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return create_access_request.main(event, context)
