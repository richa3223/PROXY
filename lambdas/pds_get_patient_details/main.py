""" Lambda function for fetching PDS Patient Details.

    This Lambda function is designed to retrieve Personal Demographics
    Service (PDS) Patient Details for a given NHS Number. It handles
    authorization, error responses, and provides success responses
    with patient details.
"""

import os
from http import HTTPStatus

from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.server import FHIRNotFoundException, FHIRUnauthorizedException
from spine_aws_common import LambdaApplication

import lambdas.utils.pds.errors as err
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds.nhsnumber import NHSNumber
from lambdas.utils.pds.pdsfhirclient import PDSFHIRClient


class PdsGetPatientDetails(LambdaApplication):
    """Retrieves the PDS Patient Details"""

    SETTINGS = {
        "app_id": "lambda_pds_patient",
        "api_base": "",
    }

    PARAMETER_NHSNUMBER = "nhsNumber"
    PARAMETER_AUTH_TKN = "authToken"

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)
        self.SETTINGS["api_base"] = os.getenv("PDS_BASE_URL")

    def handle_success(self, data) -> None:
        """Sets the response for a successful operation.

        The method constructs a successful response with a 200 status code
        and includes the provided data in the 'pdsPatientRecord' field.

        Args:
            data (dict): The data to include in the response body.

        Returns:
            None
        """

        self.response = {
            "statusCode": HTTPStatus.OK,
            "body": {"pdsPatientRecord": data, "error": None},
        }

    def handle_error(self, status_code, error_message) -> None:
        """Sets the response for an error condition.

        The method constructs an error response with the provided status code
        and error message.

        By default 'pdsPatientRecord' is set to None.

        Args:
          status_code (int): The HTTP status code to be included in the response.
          error_message (str): The error message or description to be included
                                in the response.

        Returns:
            None
        """

        self.response = {
            "statusCode": status_code,
            "body": {
                "pdsPatientRecord": None,
                "error": error_message,
            },
        }

    def start(self) -> None:
        """Retrieves the PDS Patient Details of the provided NHS Number"""
        write_log("DEBUG", {"info": "Start ran"})

        input_nhs_number = self.event.get(self.PARAMETER_NHSNUMBER, 0)
        input_auth_token = self.event.get(self.PARAMETER_AUTH_TKN, 0)

        if self.PARAMETER_AUTH_TKN not in self.event:
            write_log("WARNING", {"info": err.ERROR_AUTH_TKN_REQUIRED})
            self.handle_error(HTTPStatus.BAD_REQUEST, err.ERROR_AUTH_TKN_REQUIRED)
            return

        if self.PARAMETER_NHSNUMBER not in self.event:
            write_log("WARNING", {"info": err.ERROR_NHS_NUMBER_REQUIRED})
            self.handle_error(HTTPStatus.BAD_REQUEST, err.ERROR_NHS_NUMBER_REQUIRED)
            return

        nhs_number = str(input_nhs_number)
        auth_token = str(input_auth_token)

        validator = NHSNumber()
        if not validator.is_valid_nhs_number(nhs_number):
            write_log("WARNING", {"info": err.ERROR_NHS_NUMBER_INVALID})
            self.handle_error(HTTPStatus.BAD_REQUEST, err.ERROR_NHS_NUMBER_INVALID)
            return

        if input_auth_token is None or len(auth_token) < 10:
            write_log("WARNING", {"info": err.ERROR_AUTH_TKN_INVALID})
            self.handle_error(HTTPStatus.BAD_REQUEST, err.ERROR_AUTH_TKN_INVALID)
            return

        try:
            smart_client = client.FHIRClient(settings=self.SETTINGS)
            smart = PDSFHIRClient(smart_client, self.SETTINGS["api_base"])
            smart.headers["Authorization"] = f"Bearer {auth_token}"

            patient = Patient.read(nhs_number, smart)
            patient_data = patient.as_json()

            self.handle_success(patient_data)

        except FHIRUnauthorizedException:
            write_log(
                "WARNING",
                {"info": err.ERROR_UNAUTHORIZED},
            )
            self.handle_error(HTTPStatus.UNAUTHORIZED, err.ERROR_UNAUTHORIZED)

        except FHIRNotFoundException:
            self.handle_error(HTTPStatus.NOT_FOUND, err.ERROR_RECORD_NOT_FOUND)

        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when requesting patient record",
                    "error": error,
                },
            )
            self.handle_error(
                HTTPStatus.INTERNAL_SERVER_ERROR, err.ERROR_OPERATION_FAILED
            )


pds_get_patient_details = PdsGetPatientDetails(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Lambda handler function for fetching the PDS Patient Details of the
        provided NHS Number

    Args:
        event (dict): Input event containing 'nhsNumber' & 'authToken'
        context (dict): AWS Lambda context

    Returns:
        dict:   200 - Response contains the whole PDS Patient Details
                4XX - Errors handling bad inputs and PDS errors
                5XX - Any other errors
    """
    return pds_get_patient_details.main(event, context)
