"""
Test getting patient details from PDS
"""

import pytest

from ..helpers import WORKSPACE, helpers

FUNCTION_NAME = f"{WORKSPACE}-pds_get_patient_details"


@pytest.mark.pds_api_call
def test_valid_nhs_number(helpers: helpers) -> None:
    """
    Confirm we can retrieve PDS patient details
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "9730424640", "authToken": access_token}
    )

    assert payload["statusCode"] == 200


@pytest.mark.pds_api_call
def test_no_nhs_number(helpers: helpers) -> None:
    """
    Confirm no NHS number returns 400
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "", "authToken": "token12345"}
    )

    assert payload["statusCode"] == 400
    assert payload["body"]["pdsPatientRecord"] is None
    assert payload["body"]["error"] == "NHS Number is not valid."


@pytest.mark.pds_api_call
def test_invalid_nhs_number(helpers: helpers) -> None:
    """
    Confirm an invalid NHS number returns 400
    """
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "900000000", "authToken": "blah"}
    )

    assert payload["statusCode"] == 400
    assert payload["body"]["pdsPatientRecord"] is None
    assert payload["body"]["error"] == "NHS Number is not valid."


@pytest.mark.pds_api_call
def test_valid_nhs_number_no_pds_record(helpers: helpers) -> None:
    """
    Confirm a valid NHS number with no pds record returns 404
    """
    access_token = helpers.get_pds_access_token()
    payload = helpers.invoke_lambda_function(
        FUNCTION_NAME, {"nhsNumber": "7966022757", "authToken": access_token}
    )

    assert payload["statusCode"] == 404
    assert payload["body"]["pdsPatientRecord"] is None
    assert payload["body"]["error"] == "Record Not Found."
