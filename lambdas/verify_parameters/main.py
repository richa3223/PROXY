"""Validates the parameters that are supplied to the validate relationships step function."""

import traceback
import uuid

from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds import errors
from lambdas.utils.pds.errors import OperationalOutcomeResult
from lambdas.utils.pds.nhsnumber import NHSNumber


class VerifyParameters(LambdaApplication):
    """Verifies the parameters for the step function."""

    PARAM_HEADER_CORRELATION_ID = "correlationId"
    PARAM_HEADER_ORIGINAL_URL = "originalRequestUrl"
    PARAM_HEADER_REQUEST_ID = "requestId"

    PARAM_PROXY_NHS_NO = "proxyNhsNumber"
    PARAM_PATIENT_NHS_NO = "patientNhsNumber"
    PARAM_INCLUDE = "_include"

    RELATED_PERSON_RESOURCE_INCLUDE = "RelatedPerson:patient"

    correlation_id = ""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Verifies the parameters are correct"""

        write_log("DEBUG", {"info": "Verify Parameters ran"})

        try:
            if self.__check_headers() and self.__check_parameters_present():
                self.__output_success()

        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": f"Error when attempting to verify parameters - {error}",
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
        if not self.event.get(self.PARAM_HEADER_REQUEST_ID):
            # Check Request ID header is present - if not, return an error
            self.__output_error(errors.HEADER_MISSING_REQUEST_ID)
            result = False
        elif self.__verify_is_guid(self.PARAM_HEADER_REQUEST_ID) is False:
            # Check Request ID header is UUID - if present, return an error
            self.__output_error(errors.HEADER_INVALID_REQUEST_ID)
            result = False
        elif (
            self.event.get(self.PARAM_HEADER_CORRELATION_ID)
            and self.__verify_is_guid(self.PARAM_HEADER_CORRELATION_ID) is False
        ):
            # Check if the header is not default value set by mapping template/getting from the event
            # and if it is not a valid UUID
            self.__output_error(errors.HEADER_INVALID_CORRELATION_ID)
            result = False
        else:
            result = True

        # Correlation ID header is optional
        # If present, use the value supplied otherwise, use uuid
        self.correlation_id = self.event.get(self.PARAM_HEADER_CORRELATION_ID) or str(
            uuid.uuid4()
        )

        return result

    def __check_parameters_present(self) -> bool:
        """Determines if all the required parameters are in self.event

        Returns:
            bool: Returns False if a required parameter is missing, True otherwise
        """
        result = False

        if self.event.get(self.PARAM_PROXY_NHS_NO) and self.event.get(
            self.PARAM_PATIENT_NHS_NO
        ):
            # Both parameters are present
            write_log("DEBUG", {"info": "Both Proxy and Patient NHS Number supplied"})
            result = True

        if self.event.get(self.PARAM_PROXY_NHS_NO) and not self.event.get(
            self.PARAM_PATIENT_NHS_NO
        ):
            # Only proxy number - list relations
            write_log("DEBUG", {"info": "Only Proxy NHS Number supplied"})
            result = True

        if not self.event.get(self.PARAM_PROXY_NHS_NO):
            write_log("ERROR", {"info": "Proxy NHS Number not supplied", "error": ""})
            self.__output_error(errors.MISSING_IDENTIFIER_VALUE)
            return False

        if self.event.get(
            self.PARAM_PROXY_NHS_NO
        ) and not self.__check_nhs_number_is_valid(
            self.event.get(self.PARAM_PROXY_NHS_NO)
        ):
            write_log("ERROR", {"info": "Proxy Identifier not valid", "error": ""})
            self.__output_error(errors.INVALID_IDENTIFIER_VALUE)
            return False

        if self.event.get(
            self.PARAM_PATIENT_NHS_NO
        ) and not self.__check_nhs_number_is_valid(
            self.event.get(self.PARAM_PATIENT_NHS_NO)
        ):
            write_log("ERROR", {"info": "Patient Identifier not valid", "error": ""})
            self.__output_error(errors.INVALID_PATIENT_IDENTIFIER_VALUE)
            return False

        if (
            self.event.get(self.PARAM_PROXY_NHS_NO)
            and not self.__check_nhs_number_system(
                self.event.get(self.PARAM_PROXY_NHS_NO)
            )
            and self.event.get(self.PARAM_PATIENT_NHS_NO)
            and not self.__check_nhs_number_system(
                self.event.get(self.PARAM_PATIENT_NHS_NO)
            )
        ):
            write_log(
                "ERROR",
                {"info": "Proxy and Patient Identifier Systems not valid", "error": ""},
            )
            self.__output_error(errors.INVALID_IDENTIFIER_SYSTEM)
            return False

        if self.event.get(
            self.PARAM_PROXY_NHS_NO
        ) and not self.__check_nhs_number_system(
            self.event.get(self.PARAM_PROXY_NHS_NO)
        ):
            write_log(
                "ERROR", {"info": "Proxy Identifier System not valid", "error": ""}
            )
            self.__output_error(errors.INVALID_IDENTIFIER_SYSTEM)
            return False

        if self.event.get(
            self.PARAM_PATIENT_NHS_NO
        ) and not self.__check_nhs_number_system(
            self.event.get(self.PARAM_PATIENT_NHS_NO)
        ):
            write_log(
                "ERROR", {"info": "Patient Identifier System not valid", "error": ""}
            )
            self.__output_error(errors.INVALID_IDENTIFIER_SYSTEM)
            return False

        if self.PARAM_HEADER_ORIGINAL_URL not in self.event or not self.event.get(
            self.PARAM_HEADER_ORIGINAL_URL
        ):
            # No query parameters present
            write_log(
                "ERROR", {"info": "Original request URL not supplied", "error": ""}
            )
            self.__output_error(errors.INTERNAL_SERVER_ERROR)
            result = False

        if (
            not self.event.get(self.PARAM_PROXY_NHS_NO)
            and not self.event.get(self.PARAM_PATIENT_NHS_NO)
            or not self.event.get(self.PARAM_PROXY_NHS_NO)
            and self.event.get(self.PARAM_PATIENT_NHS_NO)
        ):
            # Last check - if no parameters are present, return an error (should never happen)
            write_log("ERROR", {"info": "No correct parameters supplied", "error": ""})
            self.__output_error(errors.NOT_SUPPORTED)

        return result

    def __check_nhs_number_system(self, nhs_number: str) -> bool:
        """Determines if the NHS Number System is correct (if set)

        Args:
            nhs_number (str): The NHS Number to check

        Returns:
            bool: Returns True if the NHS Number System is correct, False otherwise
        """
        nhs_number_class = NHSNumber()
        return nhs_number_class.is_correct_nhs_number_system(nhs_number)

    def __check_nhs_number_is_valid(self, nhs_number: str) -> bool:
        """Determines if the NHS Number Type is valid

        Args:
            nhs_number (str): The NHS Number to check

        Returns:
            bool: Returns True if the NHS Number is valid, False otherwise
        """
        nhs_number_class = NHSNumber()
        nhs_number = nhs_number_class.extract_nhs_number(nhs_number)
        return nhs_number_class.is_valid_nhs_number(nhs_number)

    def __verify_is_guid(self, parameter_header: str) -> bool:
        """Determines if the parameter is a valid UUID

        Args:
            parameter_header (str): The header to check

        Returns:
            bool: True if the parameter is a valid UUID, False otherwise
        """
        try:
            uuid.UUID(self.event.get(parameter_header))
            return True
        except Exception:
            write_log("WARNING", {"info": f"{parameter_header=}: Not a valid UUID"})
            return False

    def __output_error(self, details: OperationalOutcomeResult):
        """Updates the self.response with an error

        Args:
            details (OperationalOutcomeResult): Details of the error
        """
        write_log("ERROR", {"info": details, "error": "details"})
        self.response = {"error": details}

    def __output_success(self):
        """Outputs the required parameters"""
        patient_nhs_number = self.event.get(self.PARAM_PATIENT_NHS_NO)
        proxy_nhs_number = self.event.get(self.PARAM_PROXY_NHS_NO)

        nhs_number = NHSNumber()

        resp = {
            "patientNhsNumber": nhs_number.extract_nhs_number(patient_nhs_number),
            "proxyNhsNumber": nhs_number.extract_nhs_number(proxy_nhs_number),
            "correlationId": self.correlation_id,
            "originalRequestUrl": self.event.get(self.PARAM_HEADER_ORIGINAL_URL),
            self.PARAM_INCLUDE: "",
            self.PARAM_HEADER_REQUEST_ID: self.event.get(self.PARAM_HEADER_REQUEST_ID),
        }

        # Only allowing RELATED_PERSON_RESOURCE at the moment
        include = self.event.get(self.PARAM_INCLUDE, None)
        if include == self.RELATED_PERSON_RESOURCE_INCLUDE:
            resp[self.PARAM_INCLUDE] = self.RELATED_PERSON_RESOURCE_INCLUDE

        self.response = resp

        # Only allowing RELATED_PERSON_RESOURCE at the moment
        include = self.event.get(self.PARAM_INCLUDE, None)
        if include == self.RELATED_PERSON_RESOURCE_INCLUDE:
            resp[self.PARAM_INCLUDE] = self.RELATED_PERSON_RESOURCE_INCLUDE

        self.response = resp


verify_parameters = VerifyParameters(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Verifies the supplied parameters and headers

    Args:
        event (dict): Parameters to supply to the lambda
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return verify_parameters.main(event, context)
