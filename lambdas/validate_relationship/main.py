"""Validates the eligibility and relationship of the given record
"""

import os
from http import HTTPStatus
from typing import List

from fhirclient.models.fhirabstractbase import FHIRValidationError
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson
from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds import errors, pdsdata
from lambdas.utils.validation import codes
from lambdas.utils.validation.publish_validation_audit_event import (
    validation_result_event,
)


class ValidateRelationship(LambdaApplication):
    """Validates the eligibility and relationship of the given record"""

    MOTHER_RELATION_CODE = "MTH"
    MOTHER_CHILD_AGE_LIMIT = 13
    PATIENT_RECORD_UNRESTRICTED = "U"

    PARAM_MOTHER_NHS_NO = "proxyNhsNumber"
    PARAM_PATIENT_STATUS = "pdsPatientStatus"
    PARAM_RELATION_STATUS = "pdsRelationshipLookupStatus"
    PARAM_PATIENT = "pdsPatient"
    PARAM_RELATION = "pdsRelationshipLookup"
    PARAM_CORRELATION_ID = "correlationId"
    PARAM_REQUEST_ID = "requestId"

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def is_eligible(
        self, proxy_nhs_num: str, patient: Patient, related: List[RelatedPerson]
    ) -> tuple:
        """
        Determines if the given patient is eligibile based on the patient
        and relationship information provided

        Args:
            proxy_nhs_num (str): The nhs number of the proxy
            patient (Patient): The patient record for whom to the check eligibility
            related ([RelatedPerson]): List of all relationships for the patient

        Returns:
            tuple: (ErrorProxyValidation, json) Validation result
            and the related person json record
        """
        # Default to not related result
        result = codes.PATIENT_NOT_RELATED
        related_person = ""

        if pdsdata.get_is_person_deceased(patient):
            # Patient is deceased
            result = codes.PATIENT_DECEASED
        elif pdsdata.get_security_code(patient) != self.PATIENT_RECORD_UNRESTRICTED:
            # Patient PDS record is restricted
            result = codes.NO_PATIENT_CONSENT
        elif pdsdata.get_patient_age(patient) >= self.MOTHER_CHILD_AGE_LIMIT:
            # Patient did not meet the minimum age requirements
            result = codes.PATIENT_NOT_ELIGIBLE_OVER_13
        else:
            for rel in related:
                related_num = rel.patient.identifier.value
                relationship_type = pdsdata.get_relationship(rel)

                # Check if related person is mother
                if (
                    self.MOTHER_RELATION_CODE in relationship_type
                    and proxy_nhs_num == related_num
                ):
                    result = codes.VALIDATED_RELATIONSHIP
                    related_person = rel
                    break

        return (result, related_person)

    def start(self) -> None:
        """Validates that patient is eligible for relationship"""

        write_log("DEBUG", {"info": "Validate Relationship ran"})
        try:
            if self.__are_parameters_present():
                input_patient = self.event.get(self.PARAM_PATIENT, 0)
                input_related = self.event.get(self.PARAM_RELATION, 0)
                mother_num = self.event.get(self.PARAM_MOTHER_NHS_NO, 0)
                correlation_id = self.event.get(self.PARAM_CORRELATION_ID, None)
                request_id = self.event.get(self.PARAM_REQUEST_ID, None)

                if self.__are_statuses_okay(
                    mother_num, input_patient, input_related, correlation_id, request_id
                ):
                    related = []
                    for rel in input_related:
                        related.append(RelatedPerson(rel))
                    patient = Patient(input_patient)
                    result = self.is_eligible(mother_num, patient, related)
                    output_related = ""

                    if result[1] != "":
                        for relate in input_related:
                            if result[1].id == relate["id"]:
                                output_related = relate
                                break

                    write_log("DEBUG", {"info": "Generating validation result"})
                    self.__handle_validation_result(
                        patient.identifier[0].value,
                        mother_num,
                        result[0],
                        input_patient,
                        output_related,
                        correlation_id,
                        request_id,
                    )

        except FHIRValidationError as parse_error:
            write_log(
                "ERROR",
                {
                    "info": "Error when attempting to parse input",
                    "error": parse_error,
                },
            )
            self.__handle_error(errors.INTERNAL_SERVER_ERROR)
        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when attempting to confirm eligibility",
                    "error": error,
                },
            )
            self.__handle_error(errors.INTERNAL_SERVER_ERROR)

    def __are_statuses_okay(
        self,
        mother_nhs_num: str,
        input_patient: str,
        input_related: str,
        correlation_id: str,
        request_id: str,
    ) -> bool:
        """Determines if the PDS status codes have valid records attached

        Args:
            mother_nhs_num (str): id of the patient
            input_patient (str): Contains the patient JSON
            input_related (str): Contains the relationship JSON
            correlation_id: str: Correlation id to be used for Audit request

        Returns:
            bool: Returns False if PDS checks are not successful
        """
        result = True
        patient_status = self.event.get(self.PARAM_PATIENT_STATUS)
        relation_status = self.event.get(self.PARAM_RELATION_STATUS)

        if patient_status == HTTPStatus.NOT_FOUND:
            # Retrieve patient returned not found
            self.__handle_validation_result(
                "",
                mother_nhs_num,
                codes.PATIENT_NOT_FOUND,
                input_patient,
                input_related,
                correlation_id,
                request_id,
            )
            result = False
        elif patient_status != HTTPStatus.OK:
            # Retrieve patient did not return success
            self.__handle_error(codes.PATIENT_STATUS_FAIL)
            result = False
        elif relation_status == HTTPStatus.NOT_FOUND:
            # Retrieve relation returned not found result
            self.__handle_validation_result(
                "",
                mother_nhs_num,
                codes.RELATION_NOT_FOUND,
                input_patient,
                input_related,
                correlation_id,
                request_id,
            )
            result = False
        elif relation_status != HTTPStatus.OK:
            # Retrieve relation was not successful
            self.__handle_error(codes.RELATION_STATUS_FAIL)
            result = False

        return result

    def __are_parameters_present(self) -> bool:
        """Determines if all the required parameters are in self.event

        Returns:
            bool: Returns False if a required parameter is missing, True otherwise
        """
        result = True

        if self.PARAM_MOTHER_NHS_NO not in self.event:
            # Status - Bad Request
            self.__handle_parameter_error(
                errors.INTERNAL_SERVER_ERROR, self.PARAM_MOTHER_NHS_NO
            )
            result = False
        if self.PARAM_PATIENT_STATUS not in self.event:
            # Status - Bad Request
            self.__handle_parameter_error(
                errors.INTERNAL_SERVER_ERROR, self.PARAM_PATIENT_STATUS
            )
            result = False
        if self.PARAM_RELATION_STATUS not in self.event:
            # Status - Bad Request
            self.__handle_parameter_error(
                errors.INTERNAL_SERVER_ERROR, self.PARAM_RELATION_STATUS
            )
            result = False
        if self.PARAM_PATIENT not in self.event:
            self.__handle_parameter_error(
                errors.INTERNAL_SERVER_ERROR, self.PARAM_PATIENT
            )
            result = False
        if self.PARAM_RELATION not in self.event:
            self.__handle_parameter_error(
                errors.INTERNAL_SERVER_ERROR, self.PARAM_RELATION
            )
            result = False

        return result

    def __handle_parameter_error(self, details: dict, parameter: str):
        """Updates the self.response with a parameter error

        Args:
            details (dict): Details of the error
            parameter (str): The name of the parameter that caused the error
        """
        write_log(
            "ERROR",
            {"info": f"Required parameter '{parameter}' is missing", "error": ""},
        )
        self.response = {
            "statusCode": details["http_status"],
            "body": {"error": details["response_code"]},
        }

    def __handle_error(self, details: dict):
        """Updates the self.response with an error

        Args:
            details (dict): Details of the error
            ex (Exception): The exception that caused the error
        """
        self.response = {
            "statusCode": details["http_status"],
            "body": {"error": details["response_code"]},
        }

    def __handle_validation_result(
        self,
        patient_id: str,
        related_id: str,
        details: dict,
        pds_patient: str,
        pds_relationship: str,
        correlation_id: str,
        request_id: str,
    ):
        """Updates the self.response with a validation result output

        Args:
            patient_id (str): id of the patient
            related_id (str): id of the related person
            details (dict): Details on the validation result
            pds_patient (str): A string containing the patient JSON
            pds_relationship (str): A string containing the relationship JSON
            correlation_id: str: Correlation id to be used for Audit request
            request_id: str: Request id to be used for Audit request
        """

        # Set the response object
        if details["eligibility"]:
            self.response = {
                "statusCode": details["http_status"],
                "body": {
                    self.PARAM_PATIENT: pds_patient,
                    self.PARAM_RELATION: pds_relationship,
                },
            }
        else:
            self.__handle_error(details)

        validation_result_event(
            patient_id, related_id, details, request_id, correlation_id
        )


validate_relation = ValidateRelationship(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Generates a FHIR response based on the event input using the ValidateRelationship.

    Args:
        event (dict): Parameters to supply to ValidateRelationship
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return validate_relation.main(event, context)
