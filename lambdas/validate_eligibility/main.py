"""Lambda function for checking Users Eligibility
"""

import os
from http import HTTPStatus
from typing import Optional

from fhirclient.models.fhirabstractbase import FHIRValidationError
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson
from spine_aws_common import LambdaApplication

import lambdas.utils.validation.codes as code
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds.pdsdata import get_is_person_deceased, get_security_code
from lambdas.utils.validation.publish_validation_audit_event import (
    validation_result_event,
)


class ValidateEligibility(LambdaApplication):
    """Checks Users Eligibility based on parameter values"""

    # Parameters
    PARAMETER_PDS_PROXY_DETAILS = "pdsProxyDetails"
    PARAMETER_PDS_PROXY_STATUS_CODE = "pdsProxyStatusCode"
    PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY = "pdsRelationshipLookup"
    PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE = (
        "pdsRelationshipLookupStatusCode"
    )
    PARAMETER_PATIENT_NHS_NUMBER = "patientNhsNumber"
    PARAMETERS_CORRELATION_ID = "correlationId"
    PARAMETERS_REQUEST_ID = "requestId"

    # Parameter Error Strings
    PARAMETER_PDS_PROXY_DETAILS_NOT_FOUND = "PDS Details (Proxy) is required"
    PARAMETER_PDS_PROXY_STATUS_CODE_NOT_FOUND = "PDS Status Code (Proxy) is required"
    PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_NOT_FOUND = (
        "PDS Relationship Lookup is required"
    )
    PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_NOT_FOUND = (
        "PDS Relationship Lookup Status Code is required"
    )
    PARAMETER_PDS_PROXY_STATUS_CODE_INVALID = "PDS Status Code is invalid"
    PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_INVALID = (
        "PDS Relationship Lookup Status Code is invalid"
    )

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def handle_success(
        self,
        proxy_nhs_number: str,
        validation_outcome: code,
        request_id: str,
        correlation_id: str,
        relationship_arr: Optional[list[RelatedPerson]] = None,
    ) -> None:
        """
        Sets the response for a successful condition.

        The method constructs a successful response with the provided validation
        code object and the final relationship array to be returned.

        Args:
            proxy_nhs_number (str): NHS Number of the patient
            validation_outcome (code): A dictionary representing the validation outcome,
                        typically containing keys such as 'http_status','eligibility',
                        and 'audit_msg'.
            request_id (str): The request id for the API request.
            correlation_id: str: The correlation id for the request.
            relationship_arr (list[RelatedPerson]): A list of RelatedPerson objects representing
                        the final relationship array to be included in the response.

        Returns:
            None
        """
        validation_result_event(
            proxy_nhs_number, "", validation_outcome, request_id, correlation_id
        )

        serialised_relationship_arr = (
            [item.as_json() for item in relationship_arr] if relationship_arr else None
        )

        self.response = {
            "statusCode": validation_outcome["http_status"],
            "body": {
                "eligibility": validation_outcome["eligibility"],
                "relationshipArr": serialised_relationship_arr,
            },
        }

    def handle_error(self, status_code: int, error_message: str) -> None:
        """Sets the response for an error condition.

        The method constructs an error response with the provided status code
        and error message.

        Args:
            status_code (HTTPStatus): The HTTP status code to be included in the response.
            error_message (str): The error message or description to be included
                in the response.
        """

        write_log("ERROR", {"info": error_message, "error": ""})

        self.response = {
            "statusCode": status_code,
            "body": {
                "error": error_message,
            },
        }

    def filter_related_person_array(
        self, related_people: list[RelatedPerson], nhs_number: str
    ) -> list[RelatedPerson]:
        """
        Filters a list of RelatedPerson objects based on the NHS number.

        Args:
            related_people (list[RelatedPerson]): A list of RelatedPerson objects
                    to be filtered.
            nhs_number (str): The NHS number used as the filter criteria.

        Returns:
            list[RelatedPerson]: A filtered list of RelatedPerson objects that
                    match the provided NHS number.
        """
        return [
            item
            for item in related_people
            if item.patient
            and item.patient.identifier
            and item.patient.identifier.value == nhs_number
        ]

    def start(self) -> None:
        """Checks Users Eligibility based on parameter values"""
        write_log("DEBUG", {"info": "Start ran"})
        try:
            if self.PARAMETER_PDS_PROXY_STATUS_CODE not in self.event:
                err_msg = self.PARAMETER_PDS_PROXY_STATUS_CODE_NOT_FOUND
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            if (
                self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE
                not in self.event
            ):
                err_msg = (
                    self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_NOT_FOUND
                )
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            correlation_id = self.event.get(self.PARAMETERS_CORRELATION_ID, None)
            request_id = self.event.get(self.PARAMETERS_REQUEST_ID, "RequestIDNotSet")
            pds_proxy_status_code = self.event.get(
                self.PARAMETER_PDS_PROXY_STATUS_CODE, 0
            )
            pds_relationship_status_code = self.event.get(
                self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE, 0
            )
            patient_nhs_number = self.event.get(self.PARAMETER_PATIENT_NHS_NUMBER, None)

            # Invalid Parameter checks
            if pds_proxy_status_code not in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]:
                err_msg = self.PARAMETER_PDS_PROXY_STATUS_CODE_INVALID
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            if pds_relationship_status_code not in [
                HTTPStatus.OK,
                HTTPStatus.NOT_FOUND,
            ]:
                err_msg = (
                    self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_STATUS_CODE_INVALID
                )
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            # Checks PDS Details record found
            if pds_proxy_status_code == HTTPStatus.NOT_FOUND:
                write_log("DEBUG", {"info": code.PROXY_NOT_FOUND["validation_code"]})
                self.handle_success(
                    "", code.PROXY_NOT_FOUND, request_id, correlation_id
                )
                return

            # Bad request if no PDS details provided after 200 status code
            if self.PARAMETER_PDS_PROXY_DETAILS not in self.event:
                err_msg = self.PARAMETER_PDS_PROXY_DETAILS_NOT_FOUND
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            pds_proxy_details = self.event.get(self.PARAMETER_PDS_PROXY_DETAILS, 0)

            # Check PDS valid FHIR format
            fhir_patient = Patient(pds_proxy_details)
            proxy_nhs_number = fhir_patient.identifier[0].value

            # Proxy eligibility checks
            if get_is_person_deceased(fhir_patient):
                write_log("DEBUG", {"info": code.PROXY_DECEASED["validation_code"]})
                self.handle_success(
                    proxy_nhs_number, code.PROXY_DECEASED, request_id, correlation_id
                )
                return

            proxy_flag = get_security_code(fhir_patient)
            if proxy_flag != "U":
                write_log("DEBUG", {"info": code.NO_PROXY_CONSENT["validation_code"]})
                self.handle_success(
                    proxy_nhs_number, code.NO_PROXY_CONSENT, request_id, correlation_id
                )
                return

            # Relationship valid check
            if pds_relationship_status_code == HTTPStatus.NOT_FOUND:
                write_log(
                    "DEBUG",
                    {"info": code.PROXY_NO_RELATIONSHIPS_FOUND["validation_code"]},
                )
                self.handle_success(
                    proxy_nhs_number,
                    code.PROXY_NO_RELATIONSHIPS_FOUND,
                    request_id,
                    correlation_id,
                )
                return

            # Bad request if no relationship Look up provided after 200 status code
            if self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY not in self.event:
                err_msg = self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY_NOT_FOUND
                self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
                return

            pds_relationships = self.event.get(
                self.PARAMETER_PDS_RELATIONSHIP_LOOKUP_PROXY, 0
            )

            # Check Relationships valid FHIR format
            fhir_relationships = []
            for relationship in pds_relationships:
                fhir_relationships.append(RelatedPerson(relationship))

            new_relationship_arr = (
                self.filter_related_person_array(fhir_relationships, patient_nhs_number)
                if patient_nhs_number
                else fhir_relationships
            )

            write_log("DEBUG", {"info": "Lambda completed"})

            self.handle_success(
                proxy_nhs_number,
                code.VALIDATED_PROXY,
                request_id,
                correlation_id,
                new_relationship_arr,
            )
        except (
            FHIRValidationError
        ) as parse_error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when attempting to read parameters to generate output",
                    "error": parse_error,
                },
            )
            err_msg = "Supplied data cannot be processed"
            self.handle_error(HTTPStatus.BAD_REQUEST, err_msg)
            return
        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when attempting to confirm eligibility",
                    "error": error,
                },
            )
            err_msg = "Error when attempting to confirm eligibility"
            self.handle_error(HTTPStatus.INTERNAL_SERVER_ERROR, err_msg)
            return


validate_eligibility = ValidateEligibility(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Lambda handler function for confirming the eligibility of the User, and
       filters the relationship array based on 1:1 validation.

    Args:
        event (dict): Input event containing the following:
                        - pdsProxyDetails
                        - pdsProxyStatusCode
                        - pdsRelationshipLookup
                        - pdsRelationshipLookupStatusCode
                        - patientNhsNumber [Optional]
        context (dict): Current context

    Returns:
        dict:   200 - Response contains the eligibility of the User
                4XX - Errors handling bad inputs
                5XX - Any other errors
    """

    return validate_eligibility.main(event, context)
