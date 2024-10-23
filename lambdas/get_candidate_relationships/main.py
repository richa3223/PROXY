"""Get Candidate Relationships to verify api parameters and trigger validate relationship step function"""

import traceback
import uuid
from json import dumps, loads
from os import getenv

from boto3 import client
from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds import errors
from lambdas.utils.pds.errors import OperationalOutcomeResult
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper
from lambdas.utils.pds.nhsnumber import NHSNumber


class GetCandidateRelationships(LambdaApplication):
    """Validates the api parameters that are supplied to related person step function"""

    PARAM_HEADER_AUTH_LEVEL = "accesstoken.auth_level"
    PARAM_HEADER_NHS_NO = "accesstoken.auth_user_id"
    PARAM_HEADER_CORRELATION_ID = "correlationId"
    PARAM_HEADER_ORIGINAL_URL = "originalRequestUrl"
    PARAM_HEADER_REQUEST_ID = "requestId"

    PARAM_PROXY_NHS_NO = "proxyNhsNumber"
    PARAM_PATIENT_NHS_NO = "patientNhsNumber"
    PARAM_INCLUDE = "_include"

    RELATED_PERSON_RESOURCE_INCLUDE = "RelatedPerson:patient"
    P9_LEVEL = "P9"

    correlation_id = ""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Verifies the api parameters are correct and triggers the relationship validation"""
        self.correlation_id = ""
        try:
            if self.__check_headers():
                response = self.__trigger_validate_relationship()
                self.__handle_step_function_response(response)

        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": f"Error while running get candidate relationships - {error}",
                    "error": traceback.format_exc(),
                },
            )
            self.__output_error(errors.INTERNAL_SERVER_ERROR)

    def __check_headers(self) -> bool:
        """Determines if all the required headers are present in self.event

        Returns:
            bool: Returns False if a required header is missing, True otherwise.
        """
        # Class variables are shared between runs of a lambda
        # So, variables should not be persisted at class level
        if self.PARAM_HEADER_AUTH_LEVEL not in self.event:
            write_log(
                "ERROR",
                {
                    "info": "Invalid request with error - 'accesstoken.auth_level' header must be supplied.",
                    "error": "",
                },
            )
            self.__output_error(errors.INTERNAL_SERVER_ERROR)
            result = False
        elif self.PARAM_HEADER_NHS_NO not in self.event:
            write_log(
                "ERROR",
                {
                    "info": "Invalid request with error - 'accesstoken.auth_user_id' header must be supplied.",
                    "error": "",
                },
            )
            self.__output_error(errors.INTERNAL_SERVER_ERROR)
            result = False
        else:
            result = (
                self.__check_p_level_matches_patient()
                and self.__check_nhs_number_matches_patient()
            )

        # Correlation ID header is optional
        # If present, use the value supplied otherwise, use uuid
        self.correlation_id = self.event.get(self.PARAM_HEADER_CORRELATION_ID) or str(
            uuid.uuid4()
        )

        return result

    def __check_nhs_number_matches_patient(self) -> bool:
        """Determines if the parameter and header nhs numbers match

        Returns:
            bool: Returns True if the header and parameter nhs numbers match,
            False otherwise
        """

        result = False
        requester_nhs_no = self.event.get(self.PARAM_HEADER_NHS_NO, 0)
        proxy_nhs_no = self.event.get(self.PARAM_PROXY_NHS_NO, 0)
        nhs_number = NHSNumber()
        extracted_number = nhs_number.extract_nhs_number(proxy_nhs_no).split("|")[-1]
        if requester_nhs_no == extracted_number:
            result = True
        else:
            write_log(
                "ERROR",
                {"info": "Parameter and header NHS numbers do not match.", "error": ""},
            )
            self.__output_error(errors.FORBIDDEN)

        return result

    def __check_p_level_matches_patient(self) -> bool:
        """Determines if the p level in the header is correct

        Returns:
            bool: Returns True if the header contains p level, False otherwise.
        """
        result = False

        plevel = self.event.get(self.PARAM_HEADER_AUTH_LEVEL, 0)
        if plevel == self.P9_LEVEL:
            result = True
        else:
            self.__output_error(errors.INSUFFICIENT_AUTH_LEVEL)
        return result

    def __output_error(self, operation_outcome: OperationalOutcomeResult):
        """Updates the self.response with an error

        Args:
            operation_outcome (OperationalOutcomeResult): Details of the error
        """
        write_log("WARNING", {"info": operation_outcome})
        result = FHIRObjectMapper().create_operation_outcome(operation_outcome)
        write_log("ERROR", {"info": result.as_json(), "error": ""})
        self.response = {
            "status_code": operation_outcome["http_status"].value,
            "body": result.as_json(),
        }

    def __trigger_validate_relationship(self) -> dict:
        """Triggers the validation of relationship using step function workflow"""
        sfn_client = client("stepfunctions")
        input_data = self.__get_step_function_inputs()
        write_log("DEBUG", {"info": f"Triggering step function with {input_data}"})
        return sfn_client.start_sync_execution(
            stateMachineArn=getenv("VALIDATE_RELATIONSHIPS_STATE_MACHINE_ARN"),
            input=input_data,
        )

    def __get_step_function_inputs(self) -> str:
        """Get the inputs for the step function"""
        return dumps(
            {
                "proxyNhsNumber": self.event.get(self.PARAM_PROXY_NHS_NO),
                "patientNhsNumber": self.event.get(self.PARAM_PATIENT_NHS_NO),
                "_include": self.event.get(self.PARAM_INCLUDE),
                "correlationId": self.correlation_id,
                "requestId": self.event.get(self.PARAM_HEADER_REQUEST_ID),
                "originalRequestUrl": self.event.get(self.PARAM_HEADER_ORIGINAL_URL),
            }
        )

    def __handle_step_function_response(self, response: dict) -> None:
        """Handles the response from the step function

        Args:
            response (dict): Response from the step function
        """
        write_log("DEBUG", {"info": f"Step function response - {response}"})
        if response.get("status") == "FAILED" or response.get("status") == "TIMED_OUT":
            self.__output_error(errors.INTERNAL_SERVER_ERROR)
            return
        # If the response is not failed or timed out, the response is successful and can be converted to a FHIR object (if necessary)
        state_machine_output = loads(response.get("output"))
        response_body = state_machine_output.get("body")
        status_code = state_machine_output.get("statusCode")
        write_log(
            "DEBUG",
            {
                "info": f"Evaluating response from step function - {status_code=}- {response_body=}"
            },
        )
        if response_body:
            self.response = {
                "status_code": status_code,
                "body": response_body,
            }
        else:
            write_log(
                "ERROR",
                {"info": "Failed to parse response from step function.", "error": ""},
            )
            self.__output_error(errors.INTERNAL_SERVER_ERROR)


get_candidate_relationships = GetCandidateRelationships(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Lambda handler for get_candidate_relationships

    Args:
        event (dict): Parameters to supply to the lambda
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return get_candidate_relationships.main(event, context)
