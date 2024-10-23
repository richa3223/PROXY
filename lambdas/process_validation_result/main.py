"""Generates either an operation outcome or bundle from the supplied inputs.
"""

from http import HTTPStatus

from fhirclient.models.identifier import Identifier
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson
from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds.errors import INTERNAL_SERVER_ERROR, OperationalOutcomeResult
from lambdas.utils.pds.fhirobjectmapper import FHIRObjectMapper


class ProcessValidationResult(LambdaApplication):
    """Lambda process to generate a FHIR response in the form of Bundle or Operation outcome."""

    BAD_REQUEST = HTTPStatus.BAD_REQUEST
    INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR

    PARAM_ERROR = "error"
    PARAM_PDS_PATIENT_RELATIONSHIP = "pdsPatientRelationship"
    PARAM_PDS_PATIENT_RELATIONSHIP__PATIENT = "pdsPatient"
    PARAM_PDS_PATIENT_RELATIONSHIP__RELATIONSHIP = "pdsRelationship"
    PARAM_HEADER_ORIGINAL_URL = "originalRequestUrl"
    PARAM_INCLUDE = "_include"
    PARAM_INCLUDE__RELATEDPERSON_PATIENT = "RelatedPerson:patient"
    PARAM_PROXY_IDENTIFIER = "proxyIdentifier"

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def handle_error_output(self, error: OperationalOutcomeResult) -> None:
        """Generates an operation outcome FHIR object from the supplied parameters.

        Args:
            error (OperationalOutcomeResult): Details of the error
        """

        write_log(
            "ERROR",
            {
                "info": f"error received '{error.get('response_code')}' with message: '{error.get('audit_msg')}'.",
                "error": "",
            },
        )

        resp = FHIRObjectMapper()
        result = resp.create_operation_outcome(error)

        # Make FHIR operation response object
        self.response = {
            "statusCode": int(error.get("http_status", 0)),
            "body": result.as_json(),
        }

    def handle_success_output(self, relations, proxy_identifier: Identifier) -> None:
        """Generates a bundle based on the supplied patient and relationship information.

        Args:
            relations([Patient, RelatedPerson, bool]): A tuple of related records to output
            identifier (Identifier): The identifier of the proxy
        """

        write_log("DEBUG", {"info": "generating relationship information"})

        response = FHIRObjectMapper()

        result = response.create_related_person_bundle(
            relations, self.event.get(self.PARAM_HEADER_ORIGINAL_URL), proxy_identifier
        )
        # Make FHIR result object
        self.response = {"statusCode": HTTPStatus.OK, "body": result.as_json()}

    def start(self) -> None:
        """Generates a Bundle or Operation outcome based on the event inputs for the lambda."""

        write_log("DEBUG", {"info": "Start ran"})

        try:
            if self.PARAM_ERROR in self.event:
                error = self.event.get(self.PARAM_ERROR)
                op_outcome = (
                    OperationalOutcomeResult.create_operation_outcome_result_from_event(
                        error
                    )
                )
                self.handle_error_output(op_outcome)
                return

            if self.PARAM_PDS_PATIENT_RELATIONSHIP not in self.event:
                # PDS patient information not supplied
                # Bad request - Not enough information to generate output
                write_log(
                    "WARNING", {"info": "PDS patient or error information not supplied"}
                )
                self.handle_error_output(INTERNAL_SERVER_ERROR)
                return

            if self.PARAM_HEADER_ORIGINAL_URL not in self.event or not self.event.get(
                self.PARAM_HEADER_ORIGINAL_URL, ""
            ):
                write_log("WARNING", {"info": "Original request URL not supplied"})
                self.handle_error_output(INTERNAL_SERVER_ERROR)
                return

            if self.PARAM_PROXY_IDENTIFIER not in self.event:
                write_log("WARNING", {"info": "Proxy identifier not supplied"})
                self.handle_error_output(INTERNAL_SERVER_ERROR)
                return
            elif not (
                proxy_identifier := self.event.get(self.PARAM_PROXY_IDENTIFIER, None)
            ):
                write_log("WARNING", {"info": "Proxy identifier is empty"})
                self.handle_error_output(INTERNAL_SERVER_ERROR)
                return

            proxy_identifier = Identifier(proxy_identifier)

            relationships = list()

            input_value = self.event.get(self.PARAM_PDS_PATIENT_RELATIONSHIP, 0)
            include = self.event.get(self.PARAM_INCLUDE, False)

            try:
                for value in input_value:
                    if (
                        value is not None
                        and self.PARAM_PDS_PATIENT_RELATIONSHIP__PATIENT in value
                        and self.PARAM_PDS_PATIENT_RELATIONSHIP__RELATIONSHIP in value
                    ):
                        patient = Patient(
                            value[self.PARAM_PDS_PATIENT_RELATIONSHIP__PATIENT]
                        )
                        related = RelatedPerson(
                            value[self.PARAM_PDS_PATIENT_RELATIONSHIP__RELATIONSHIP]
                        )

                        relationships.append((patient, related, include))
            except Exception as error:  # pylint: disable=broad-exception-caught
                write_log(
                    "ERROR",
                    {
                        "info": "Error when attempting to read parameters to generate output",
                        "error": error,
                    },
                )
                self.handle_error_output(INTERNAL_SERVER_ERROR)
                return

            self.handle_success_output(relationships, proxy_identifier)

        except Exception as error:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when generating output",
                    "error": error,
                },
            )
            self.handle_error_output(INTERNAL_SERVER_ERROR)


process_result = ProcessValidationResult(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Generates a FHIR response based on the event input using the ProcessValidationResult.

    Args:
        event (dict): Parameters to supply to ProcessValidationResult
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """

    return process_result.main(event, context)
