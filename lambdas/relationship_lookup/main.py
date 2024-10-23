""" Retrieves the relationship information for a given NHS number.

    If the lookup is successful, then the PDS record is returned.
    Otherwise an error is returned
"""

import os
from http import HTTPStatus

from fhirclient import client
from fhirclient.models.bundle import Bundle
from fhirclient.server import FHIRNotFoundException, FHIRUnauthorizedException
from spine_aws_common import LambdaApplication

import lambdas.utils.pds.errors as err
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log
from lambdas.utils.pds.nhsnumber import NHSNumber
from lambdas.utils.pds.pdsfhirclient import PDSFHIRClient


class RelationshipLookup(LambdaApplication):
    """Retrieves a given relationship record from PDS"""

    SETTINGS = {
        "app_id": "my_web_app",
        "api_base": "",
    }

    PARAMETER_NHSNUMBER = "nhsNumber"
    PARAMETER_AUTH_TKN = "authToken"

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)
        self.SETTINGS["api_base"] = os.getenv("PDS_BASE_URL")

    def start(self) -> None:
        """Retrieves the PDS relationship record based on the given NHS number."""

        write_log("DEBUG", {"info": "RelationshipLookup : Start ran"})

        validator = NHSNumber()
        input_nhs_number = self.event.get(self.PARAMETER_NHSNUMBER, 0)
        input_auth_token = self.event.get(self.PARAMETER_AUTH_TKN, 0)

        # Check parameter - NHS Number - exit if missing
        if self.PARAMETER_NHSNUMBER not in self.event:
            write_log("WARNING", {"info": err.ERROR_NHS_NUMBER_REQUIRED})
            self.generate_response(
                HTTPStatus.BAD_REQUEST, error=err.ERROR_NHS_NUMBER_REQUIRED
            )
            return

        # Check parameter - Auth token - exit if missing
        if self.PARAMETER_AUTH_TKN not in self.event:
            write_log("WARNING", {"info": err.ERROR_AUTH_TKN_REQUIRED})
            self.generate_response(
                HTTPStatus.BAD_REQUEST, error=err.ERROR_AUTH_TKN_REQUIRED
            )
            return

        # Validate NHS Number - Exit if invalid
        if not validator.is_valid_nhs_number(input_nhs_number):
            write_log("WARNING", {"info": err.ERROR_NHS_NUMBER_INVALID})
            self.generate_response(
                HTTPStatus.BAD_REQUEST, error=err.ERROR_NHS_NUMBER_INVALID
            )
            return

        nhs_number = str(input_nhs_number)
        auth_token = str(input_auth_token)

        # Validate Auth token - Exit if invalid
        if input_auth_token is None or len(auth_token) < 10:  # Minimum length 10
            write_log("WARNING", {"info": err.ERROR_AUTH_TKN_INVALID})
            self.generate_response(
                HTTPStatus.BAD_REQUEST, error=err.ERROR_AUTH_TKN_INVALID
            )
            return

        pds_data = []

        try:
            pds_data = self.retrieve_relationship(nhs_number, auth_token)
            self.generate_response(HTTPStatus.OK, pds_data=pds_data)

        except FHIRNotFoundException:
            # Not logging 404 requests
            self.generate_response(
                HTTPStatus.NOT_FOUND, error=err.ERROR_RECORD_NOT_FOUND
            )

        except FHIRUnauthorizedException:
            write_log("WARNING", {"info": err.ERROR_UNAUTHORIZED})
            self.generate_response(
                HTTPStatus.UNAUTHORIZED, error=err.ERROR_UNAUTHORIZED
            )

        except Exception as ex:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Error when requesting relationship record",
                    "error": ex,
                },
            )
            self.generate_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                error=err.ERROR_OPERATION_FAILED,
            )

        write_log("DEBUG", {"info": "RelationshipLookup : completed"})

    def retrieve_relationship(self, nhs_number: str, auth_token: str) -> list:
        """Retrieves the relationship for the given nhs number from pds.

        Args:
            nhs_number (str): The NHS Number to get relationship information for
            auth_token (str): The authentication token to use

        Returns:
            list: _description_
        """
        rtn = []

        smart_client = client.FHIRClient(settings=self.SETTINGS)
        pds = PDSFHIRClient(smart_client, self.SETTINGS["api_base"])
        pds.headers["Authorization"] = f"Bearer {auth_token}"
        other = Bundle.read_from(f"Patient/{nhs_number}/RelatedPerson", pds)

        if other.total > 0:
            for entry in other.entry:  # pylint: disable=not-an-iterable
                rtn.append(entry.resource.as_json())

        return rtn

    def generate_response(
        self, status_code: int, pds_data: list = None, error: str = None
    ):
        """Generates a response based on the supplied parameters"""

        self.response = {
            "statusCode": status_code,
            "body": {"pdsRelationshipRecord": pds_data, "error": error},
        }


relationship_lookup = RelationshipLookup(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> str:
    """Retrieves the PDS Relationship information for a given NHS Number

    Args:
        event (dict): Containing the following keys:
            'nhsNumber' with the number to lookup.
            'authToken' to use for auth.

    Returns:
        dict: Contianing the following keys:
            'pdsRelationships' (json) representing the pds record.
            'error' string message if the operation failed.
    """
    return relationship_lookup.main(event, context)
